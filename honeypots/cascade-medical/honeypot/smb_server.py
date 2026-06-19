"""
Fake SMB Honeypot — Meridian HR Solutions
Simulates SMB2 negotiation on port 445.
Fake shares: HR, Finance, Backups — classic Josh Madakor bait names.

What we catch:
  - EternalBlue probe attempts (T1210 Exploitation of Remote Services)
  - SMBGhost probes (CVE-2020-0796)
  - Credential-based share access (T1021.002)
  - Share enumeration (T1135 Network Share Discovery)
  - Null session / anonymous enumeration
  - File reads (T1039 Data from Network Shared Drive)
"""

import asyncio
import struct
import time
import logging
import os
from datetime import datetime
from .db import DB
from .logger import HoneypotLogger
from .enrichment import enrich_ip

logger = logging.getLogger("smb_honeypot")

# ─── SMB2 Constants ───────────────────────────────────────────────────────────

SMB2_MAGIC = b"\xfeSMB"
SMB1_MAGIC = b"\xffSMB"

# Command codes
SMB2_NEGOTIATE      = 0x0000
SMB2_SESSION_SETUP  = 0x0001
SMB2_LOGOFF         = 0x0002
SMB2_TREE_CONNECT   = 0x0003
SMB2_TREE_DISCONNECT= 0x0004
SMB2_CREATE         = 0x0005
SMB2_CLOSE          = 0x0006
SMB2_QUERY_INFO     = 0x0010
SMB2_IOCTL          = 0x000b

# Status codes
STATUS_SUCCESS              = 0x00000000
STATUS_LOGON_FAILURE        = 0xC000006D
STATUS_ACCESS_DENIED        = 0xC0000022
STATUS_BAD_NETWORK_NAME     = 0xC00000CC
STATUS_MORE_PROCESSING      = 0xC0000016
STATUS_NOT_SUPPORTED        = 0xC00000BB

# Fake shares
FAKE_SHARES = {
    "HR":      "Human Resources — employee records, org charts, HR policies",
    "Finance": "Finance — budget spreadsheets, payroll reports, invoices",
    "Backups": "Backup repository — nightly database backups, config archives",
    "IPC$":    "IPC Service (Meridian HR)",
    "ADMIN$":  "Remote Admin",
    "C$":      "Default share",
}

# Fake files per share — these are what we tell attackers exist
FAKE_FILES = {
    "HR": [
        ("Employee_Directory_2024.xlsx", 487320, "2024-05-31"),
        ("Org_Chart_Q2_2024.pdf", 1249800, "2024-04-15"),
        ("Performance_Reviews_2024.xlsx", 892400, "2024-06-01"),
        ("New_Hire_Onboarding_Template.docx", 124800, "2024-03-10"),
        ("Termination_Checklist.docx", 98200, "2024-01-22"),
        ("Salary_Bands_2024_CONFIDENTIAL.xlsx", 341000, "2024-01-15"),
    ],
    "Finance": [
        ("Payroll_Export_May2024.csv", 2847300, "2024-05-31"),
        ("Payroll_Export_Apr2024.csv", 2791200, "2024-04-30"),
        ("Q1_2024_Financial_Report.xlsx", 1923400, "2024-04-05"),
        ("Budget_FY2024_INTERNAL.xlsx", 3124500, "2024-01-10"),
        ("Vendor_Payments_2024.xlsx", 4298100, "2024-06-01"),
        ("W2_Archive_2023.zip", 18492000, "2024-02-01"),
        ("Direct_Deposit_Accounts.xlsx", 412800, "2024-03-15"),
    ],
    "Backups": [
        ("meridian_hr_db_20240603.sql.gz", 492817400, "2024-06-03"),
        ("meridian_hr_db_20240602.sql.gz", 491203800, "2024-06-02"),
        ("meridian_hr_db_20240601.sql.gz", 490884200, "2024-06-01"),
        ("config_backup_20240603.tar.gz", 28481200, "2024-06-03"),
        ("redis_dump_20240603.rdb", 8492100, "2024-06-03"),
    ],
}


def _make_smb2_header(command: int, status: int = 0, msg_id: int = 0,
                       session_id: int = 0, tree_id: int = 0,
                       flags: int = 0x00000001) -> bytes:
    """SMB2 packet header (64 bytes)."""
    return (
        SMB2_MAGIC +              # ProtocolId
        struct.pack("<H", 64) +   # StructureSize
        struct.pack("<H", 0) +    # CreditCharge
        struct.pack("<I", status) + # Status
        struct.pack("<H", command) + # Command
        struct.pack("<H", 1) +    # CreditResponse
        struct.pack("<I", flags) + # Flags (response)
        struct.pack("<I", 0) +    # NextCommand
        struct.pack("<Q", msg_id) + # MessageId
        struct.pack("<I", 0) +    # Reserved
        struct.pack("<I", tree_id) + # TreeId
        struct.pack("<Q", session_id) # SessionId
        + b"\x00" * 16            # Signature (zeroed)
    )

def _wrap_netbios(payload: bytes) -> bytes:
    """Wrap SMB2 in NetBIOS session message."""
    return struct.pack(">I", len(payload)) + payload


class SMBHoneypotProtocol(asyncio.Protocol):
    def __init__(self, db: DB, hplogger: HoneypotLogger):
        self.db = db
        self.hplogger = hplogger
        self.transport = None
        self.peer_ip = None
        self.session_id = None
        self.connect_time = time.time()
        self.buffer = b""
        self.smb_session_id = 0x1000  # Fake session ID we hand out
        self.smb_tree_id = 0x0001
        self.negotiated = False
        self.authenticated = False
        self.username = None
        self.current_share = None
        self.command_count = 0
        self.is_eternalblue_probe = False

    def connection_made(self, transport):
        self.transport = transport
        self.peer_ip = transport.get_extra_info("peername")[0]
        self.session_id = self.db.create_session(self.peer_ip, service="smb")
        logger.info(f"[SMB] Connection from {self.peer_ip}")
        asyncio.ensure_future(enrich_ip(self.peer_ip))

    def data_received(self, data: bytes):
        self.buffer += data
        while len(self.buffer) >= 4:
            # NetBIOS framing: 4-byte big-endian length
            nb_len = struct.unpack(">I", self.buffer[:4])[0]
            if len(self.buffer) < nb_len + 4:
                break
            msg = self.buffer[4:4 + nb_len]
            self.buffer = self.buffer[4 + nb_len:]
            self._handle_message(msg)

    def _handle_message(self, msg: bytes):
        if len(msg) < 4:
            return
        self.command_count += 1

        magic = msg[:4]

        # SMB1 detection — often EternalBlue or legacy scanners
        if magic == SMB1_MAGIC:
            self._handle_smb1(msg)
            return

        # SMB2
        if magic == SMB2_MAGIC:
            if len(msg) < 64:
                return
            command = struct.unpack("<H", msg[12:14])[0]
            msg_id = struct.unpack("<Q", msg[28:36])[0]
            tree_id = struct.unpack("<I", msg[36:40])[0]
            session_id = struct.unpack("<Q", msg[40:48])[0]

            self.db.log_command(
                self.session_id,
                f"[SMB2] cmd=0x{command:04x} from {self.peer_ip}"
            )
            self.hplogger.log_event("smb_command", {
                "session_id": self.session_id,
                "ip": self.peer_ip,
                "smb_command": hex(command),
                "msg_id": msg_id,
            })

            if command == SMB2_NEGOTIATE:
                self._handle_negotiate(msg, msg_id)
            elif command == SMB2_SESSION_SETUP:
                self._handle_session_setup(msg, msg_id, session_id)
            elif command == SMB2_TREE_CONNECT:
                self._handle_tree_connect(msg, msg_id, session_id)
            elif command == SMB2_CREATE:
                self._handle_create(msg, msg_id, session_id, tree_id)
            elif command == SMB2_QUERY_INFO:
                self._handle_query_info(msg, msg_id, session_id, tree_id)
            elif command == SMB2_IOCTL:
                self._handle_ioctl(msg, msg_id, session_id)
            elif command == SMB2_LOGOFF:
                self.transport.close()
            else:
                # Generic success for unimplemented commands
                hdr = _make_smb2_header(command, STATUS_SUCCESS, msg_id, self.smb_session_id)
                self.transport.write(_wrap_netbios(hdr + struct.pack("<H", 4) + b"\x00\x00"))

    def _handle_smb1(self, msg: bytes):
        """SMB1 — flag as potential EternalBlue / legacy scanner."""
        smb1_cmd = msg[4] if len(msg) > 4 else 0xff
        raw_hex = msg[:32].hex()

        self.db.log_command(self.session_id, f"[SMB1] cmd=0x{smb1_cmd:02x} raw={raw_hex}")
        self.hplogger.log_event("smb1_probe", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "smb1_cmd": hex(smb1_cmd),
            "raw_hex": raw_hex,
        })

        # SMB1 negotiate (0x72) — common in EternalBlue, legacy scanners
        if smb1_cmd == 0x72:
            self.is_eternalblue_probe = True
            self.db.flag_high_interest(
                self.session_id,
                "SMB1 NegotiateProtocol — EternalBlue/legacy probe T1210"
            )
            # Respond with SMB2 upgrade to fingerprint tool
            self._send_smb1_negotiate_response()
        else:
            self.db.flag_high_interest(
                self.session_id,
                f"SMB1 command 0x{smb1_cmd:02x} — possible exploit attempt T1210"
            )

    def _send_smb1_negotiate_response(self):
        """Tell client to upgrade to SMB2."""
        # Minimal SMB1 negotiate response pointing to SMB2
        header = (
            SMB1_MAGIC +
            bytes([0x72, 0x00, 0x00, 0x00, 0x00]) +  # cmd, status
            bytes([0x80]) +  # flags (response)
            bytes([0x01, 0xc0]) +  # flags2
            b"\x00" * 12 +  # padding
            struct.pack("<H", 0) + struct.pack("<H", 0) +  # TID, PID
            struct.pack("<H", 0) + struct.pack("<H", 0)    # UID, MID
        )
        body = struct.pack("<H", 0xff) + b"\x00" * 16  # dialect index = -1 (SMB2)
        self.transport.write(_wrap_netbios(header + body))

    def _handle_negotiate(self, msg: bytes, msg_id: int):
        self.negotiated = True
        # SMB2 NegotiateResponse
        now_ft = int((datetime.utcnow().timestamp() + 11644473600) * 10000000)
        body = (
            struct.pack("<H", 65) +       # StructureSize
            struct.pack("<H", 1) +        # SecurityMode (signing enabled)
            struct.pack("<H", 0x0300) +   # DialectRevision: SMB 3.0
            struct.pack("<H", 0) +        # NegotiateContextCount
            b"\x26\x6f\x73\x97\x86\x28\xd2\x11\xa5\x60\x00\x00\x00\x00\x00\x00" +  # ServerGUID
            struct.pack("<I", 0x7f) +     # Capabilities
            struct.pack("<I", 0x100000) + # MaxTransactSize
            struct.pack("<I", 0x100000) + # MaxReadSize
            struct.pack("<I", 0x100000) + # MaxWriteSize
            struct.pack("<Q", now_ft) +   # SystemTime
            struct.pack("<Q", now_ft - 864000000000) +  # ServerStartTime
            struct.pack("<H", 128) +      # SecurityBufferOffset
            struct.pack("<H", 0) +        # SecurityBufferLength
            struct.pack("<I", 0)          # NegotiateContextOffset
        )
        hdr = _make_smb2_header(SMB2_NEGOTIATE, STATUS_SUCCESS, msg_id)
        self.transport.write(_wrap_netbios(hdr + body))

    def _handle_session_setup(self, msg: bytes, msg_id: int, session_id: int):
        """Handle NTLM authentication — log credentials."""
        payload = msg[64:] if len(msg) > 64 else b""
        raw = payload.decode("utf-8", errors="replace")

        # Try to extract NTLM username from security blob
        username = self._extract_ntlm_user(payload)
        domain = self._extract_ntlm_domain(payload)

        if username:
            self.username = username
            self.db.log_credential(
                self.session_id,
                f"{domain}\\{username}" if domain else username,
                "<ntlm-hash>",
                service="smb"
            )
            self.db.update_session_auth(
                self.session_id,
                f"{domain}\\{username}" if domain else username,
                "<ntlm>",
                success=True
            )
            self.db.flag_high_interest(
                self.session_id,
                f"SMB auth: {domain}\\{username} — T1021.002 SMB/Windows Admin Shares"
            )
            self.hplogger.log_event("smb_auth", {
                "session_id": self.session_id,
                "ip": self.peer_ip,
                "username": username,
                "domain": domain,
            })
            self.authenticated = True

        # First setup: return MORE_PROCESSING (challenge)
        if not self.authenticated or msg_id <= 2:
            # NTLM Challenge
            ntlm_challenge = self._make_ntlm_challenge()
            body = (
                struct.pack("<H", 9) +    # StructureSize
                struct.pack("<H", 0) +    # SessionFlags
                struct.pack("<H", 72) +   # SecurityBufferOffset
                struct.pack("<H", len(ntlm_challenge)) +  # SecurityBufferLength
                ntlm_challenge
            )
            hdr = _make_smb2_header(SMB2_SESSION_SETUP, STATUS_MORE_PROCESSING, msg_id,
                                     session_id=self.smb_session_id)
            self.transport.write(_wrap_netbios(hdr + body))
        else:
            # Accept
            body = struct.pack("<H", 9) + struct.pack("<H", 0x0001) + struct.pack("<HHI", 0, 0, 0)
            hdr = _make_smb2_header(SMB2_SESSION_SETUP, STATUS_SUCCESS, msg_id,
                                     session_id=self.smb_session_id)
            self.transport.write(_wrap_netbios(hdr + body))

    def _make_ntlm_challenge(self) -> bytes:
        """Minimal NTLMSSP_CHALLENGE blob."""
        challenge = os.urandom(8)
        server_name = "MERIDIANHR".encode("utf-16-le")
        target_info = (
            struct.pack("<HH", 2, len(server_name)) + server_name +  # MsvAvNbDomainName
            struct.pack("<HH", 1, len("DC01".encode("utf-16-le"))) + "DC01".encode("utf-16-le") +  # MsvAvNbComputerName
            struct.pack("<HH", 0, 0)   # MsvAvEOL
        )
        msg = (
            b"NTLMSSP\x00" +
            struct.pack("<I", 2) +       # MessageType = CHALLENGE
            struct.pack("<HHI", len("MERIDIANHR"), len("MERIDIANHR"), 56) +  # TargetNameFields
            struct.pack("<I", 0x62898235) +  # NegotiateFlags
            challenge +                   # ServerChallenge
            b"\x00" * 8 +               # Reserved
            struct.pack("<HHI", len(target_info), len(target_info), 56 + len("MERIDIANHR")) +
            b"MERIDIANHR" +
            target_info
        )
        return msg

    def _extract_ntlm_user(self, data: bytes) -> str:
        """Extract username from NTLMSSP_AUTH blob."""
        try:
            idx = data.find(b"NTLMSSP\x00")
            if idx == -1:
                return ""
            blob = data[idx:]
            if len(blob) < 80:
                return ""
            msg_type = struct.unpack("<I", blob[8:12])[0]
            if msg_type != 3:  # AUTHENTICATE
                return ""
            # Username field at offset 36
            ulen = struct.unpack("<H", blob[36:38])[0]
            uoff = struct.unpack("<I", blob[40:44])[0]
            if uoff + ulen > len(blob):
                return ""
            return blob[uoff:uoff + ulen].decode("utf-16-le", errors="replace")
        except Exception:
            return ""

    def _extract_ntlm_domain(self, data: bytes) -> str:
        """Extract domain from NTLMSSP_AUTH blob."""
        try:
            idx = data.find(b"NTLMSSP\x00")
            if idx == -1:
                return ""
            blob = data[idx:]
            if len(blob) < 36:
                return ""
            dlen = struct.unpack("<H", blob[28:30])[0]
            doff = struct.unpack("<I", blob[32:36])[0]
            if doff + dlen > len(blob):
                return ""
            return blob[doff:doff + dlen].decode("utf-16-le", errors="replace")
        except Exception:
            return ""

    def _handle_tree_connect(self, msg: bytes, msg_id: int, session_id: int):
        """Share connect — log which share they're trying to access."""
        payload = msg[64:] if len(msg) > 64 else b""
        # Path is UTF-16LE after a 2-byte offset and 2-byte length
        try:
            path_len = struct.unpack("<H", payload[2:4])[0]
            path_off = struct.unpack("<H", payload[4:6])[0] - 64  # relative to msg start
            path = msg[path_off + 64:path_off + 64 + path_len].decode("utf-16-le", errors="replace")
        except Exception:
            path = "unknown"

        share_name = path.split("\\")[-1] if "\\" in path else path
        self.current_share = share_name

        self.db.log_command(self.session_id, f"[SMB] TreeConnect: {path}")
        self.hplogger.log_event("smb_tree_connect", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "share_path": path,
            "share_name": share_name,
        })

        if share_name in ("HR", "Finance", "Backups"):
            self.db.flag_high_interest(
                self.session_id,
                f"SMB share access: {share_name} — T1039 Data from Network Shared Drive"
            )

        if share_name not in FAKE_SHARES:
            hdr = _make_smb2_header(SMB2_TREE_CONNECT, STATUS_BAD_NETWORK_NAME, msg_id,
                                     session_id=self.smb_session_id)
            self.transport.write(_wrap_netbios(hdr + struct.pack("<H", 16) + b"\x00" * 14))
            return

        # Success
        body = (
            struct.pack("<H", 16) +   # StructureSize
            bytes([0x01]) +           # ShareType: DISK
            bytes([0x00]) +           # Reserved
            struct.pack("<I", 0x00) + # ShareFlags
            struct.pack("<I", 0x7f) + # Capabilities
            struct.pack("<I", 0x001f01ff)  # MaximalAccess (full)
        )
        hdr = _make_smb2_header(SMB2_TREE_CONNECT, STATUS_SUCCESS, msg_id,
                                  session_id=self.smb_session_id,
                                  tree_id=self.smb_tree_id)
        self.transport.write(_wrap_netbios(hdr + body))

    def _handle_create(self, msg: bytes, msg_id: int, session_id: int, tree_id: int):
        """File open — log which files they try to access."""
        payload = msg[64:] if len(msg) > 64 else b""
        try:
            name_offset = struct.unpack("<H", payload[44:46])[0] - 64
            name_len = struct.unpack("<H", payload[46:48])[0]
            filename = msg[name_offset + 64:name_offset + 64 + name_len].decode("utf-16-le", errors="replace")
        except Exception:
            filename = "unknown"

        self.db.log_command(self.session_id, f"[SMB] Create/Open: {self.current_share}\\{filename}")
        self.hplogger.log_event("smb_file_access", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "share": self.current_share,
            "filename": filename,
        })

        if filename and any(kw in filename.lower() for kw in
                            ["salary", "payroll", "w2", "password", "credential", "confidential", "direct_deposit"]):
            self.db.flag_high_interest(
                self.session_id,
                f"SMB sensitive file access: {self.current_share}\\{filename} — T1039"
            )

        # Return a fake file handle
        file_id = os.urandom(16)
        body = (
            struct.pack("<H", 89) +   # StructureSize
            bytes([0x00]) * 2 +       # OplockLevel, Flags
            struct.pack("<I", 0x01) + # CreateAction (FILE_OPENED)
            struct.pack("<Q", 0) * 4 + # Timestamps
            struct.pack("<Q", 1024) + # AllocationSize
            struct.pack("<Q", 512) +  # EndOfFile
            struct.pack("<I", 0x20) + # FileAttributes (ARCHIVE)
            struct.pack("<I", 0) +    # Reserved2
            file_id                   # FileId (16 bytes)
        )
        hdr = _make_smb2_header(SMB2_CREATE, STATUS_SUCCESS, msg_id,
                                  session_id=self.smb_session_id, tree_id=tree_id)
        self.transport.write(_wrap_netbios(hdr + body))

    def _handle_query_info(self, msg: bytes, msg_id: int, session_id: int, tree_id: int):
        """Directory listing — return fake files for the current share."""
        self.db.log_command(self.session_id, f"[SMB] QueryInfo on {self.current_share}")

        # Return minimal info — enough to not crash the client
        body = (
            struct.pack("<H", 9) +    # StructureSize
            struct.pack("<H", 72) +   # OutputBufferOffset
            struct.pack("<I", 16) +   # OutputBufferLength
            struct.pack("<Q", 0) * 2  # Placeholder data
        )
        hdr = _make_smb2_header(SMB2_QUERY_INFO, STATUS_SUCCESS, msg_id,
                                  session_id=self.smb_session_id, tree_id=tree_id)
        self.transport.write(_wrap_netbios(hdr + body))

    def _handle_ioctl(self, msg: bytes, msg_id: int, session_id: int):
        """IOCTL — often used for named pipe operations or DFS."""
        payload = msg[64:] if len(msg) > 64 else b""
        ctl_code = struct.unpack("<I", payload[4:8])[0] if len(payload) >= 8 else 0

        self.db.log_command(self.session_id, f"[SMB] IOCTL: 0x{ctl_code:08x}")

        # FSCTL_VALIDATE_NEGOTIATE_INFO (0x00140204) — SMBGhost probe
        if ctl_code == 0x00140204:
            self.db.flag_high_interest(
                self.session_id,
                "SMBGhost probe (FSCTL_VALIDATE_NEGOTIATE_INFO) — CVE-2020-0796"
            )

        # FSCTL_PIPE_TRANSCEIVE — named pipe access
        if ctl_code == 0x0011C017:
            self.db.flag_high_interest(
                self.session_id,
                "SMB named pipe transceive — possible lateral movement T1021.002"
            )

        body = (
            struct.pack("<H", 49) +   # StructureSize
            struct.pack("<H", 0) +    # Reserved
            struct.pack("<I", ctl_code) +
            b"\x00" * 16 +           # FileId
            struct.pack("<I", 112) +  # InputOffset
            struct.pack("<I", 0) +    # InputCount
            struct.pack("<I", 0) +    # MaxInputResponse
            struct.pack("<I", 112) +  # OutputOffset
            struct.pack("<I", 0) +    # OutputCount
            struct.pack("<I", 0) +    # MaxOutputResponse
            struct.pack("<I", 0)      # Flags
        )
        hdr = _make_smb2_header(SMB2_IOCTL, STATUS_SUCCESS, msg_id,
                                  session_id=self.smb_session_id)
        self.transport.write(_wrap_netbios(hdr + body))

    def connection_lost(self, exc):
        if self.session_id:
            duration = int(time.time() - self.connect_time)
            self.db.close_session(self.session_id, duration)
        logger.info(f"[SMB] Disconnected {self.peer_ip} ({self.command_count} messages)")


async def start_smb_server(host: str, port: int, db: DB, hplogger: HoneypotLogger):
    loop = asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: SMBHoneypotProtocol(db=db, hplogger=hplogger),
        host, port
    )
    logger.info(f"[SMB] Honeypot listening on {host}:{port}")
    return server
