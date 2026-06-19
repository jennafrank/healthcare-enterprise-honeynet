"""
Cascade Medical — Additional Service Honeypots
RDP (3389), VNC (5900+), Telnet (23), MSSQL (1433),
Elasticsearch (9200), SMTP/IMAP (25/143/587), HL7 (2575)
"""

import asyncio
import struct
import time
import json
import random
import logging
from datetime import datetime
from .db import DB
from .logger import HoneypotLogger
from .enrichment import enrich_ip

logger = logging.getLogger("extra_honeypots")

# ─── RDP (3389) ──────────────────────────────────────────────────────────────

class RDPHoneypotProtocol(asyncio.Protocol):
    """
    Simulates RDP Connection Request (COTP/X.224) handshake.
    Logs every credential attempt and NLA negotiation.
    RDP is the #1 attacked port after SMB — huge volume expected.
    """
    def __init__(self, db: DB, hplogger: HoneypotLogger):
        self.db = db
        self.hplogger = hplogger
        self.transport = None
        self.peer_ip = None
        self.session_id = None
        self.connect_time = time.time()
        self.buffer = b""
        self.state = "init"
        self.packet_count = 0

    def connection_made(self, transport):
        self.transport = transport
        self.peer_ip = transport.get_extra_info("peername")[0]
        self.session_id = self.db.create_session(self.peer_ip, service="rdp")
        logger.info(f"[RDP] Connection from {self.peer_ip}")
        asyncio.ensure_future(enrich_ip(self.peer_ip))

    def data_received(self, data: bytes):
        self.buffer += data
        self.packet_count += 1

        raw_hex = data[:32].hex()
        self.db.log_command(self.session_id, f"[RDP] pkt#{self.packet_count} hex={raw_hex}")
        self.hplogger.log_event("rdp_data", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "packet_number": self.packet_count,
            "raw_hex": raw_hex,
            "length": len(data),
        })

        # TPKT + X.224 Connection Request (0x03 0x00 ... 0xe0)
        if len(data) >= 11 and data[0] == 0x03 and data[1] == 0x00:
            if self.state == "init":
                self.state = "negotiating"
                username = self._extract_rdp_username(data)
                if username:
                    self.db.log_credential(self.session_id, username, "<rdp-nla>", service="rdp")
                    self.db.update_session_auth(self.session_id, username, "<rdp>", success=False)
                    self.db.flag_high_interest(self.session_id, f"RDP connection attempt: user={username} — T1021.001")
                    self.hplogger.log_event("rdp_auth", {
                        "session_id": self.session_id,
                        "ip": self.peer_ip,
                        "username": username,
                    })

                # X.224 Connection Confirm — protocol mismatch to fingerprint tool
                # Respond with PROTOCOL_RDP (no NLA) forcing credential send
                tpkt = bytes([0x03, 0x00, 0x00, 0x13])  # TPKT header, length 19
                x224 = bytes([
                    0x0e,       # length
                    0xd0,       # X.224 Connection Confirm
                    0x00, 0x00, # dst ref
                    0x00, 0x00, # src ref
                    0x00,       # class
                    0x02, 0x00, # type = RDP negotiation response
                    0x08, 0x00, # length
                    0x00, 0x00, 0x00, 0x00,  # selected protocol = PROTOCOL_RDP (classic, sends cleartext)
                ])
                self.transport.write(tpkt + x224)

            elif self.state == "negotiating":
                # Try to extract NLA username from CredSSP/NTLM blob
                username = self._extract_ntlm_from_credssp(data)
                if username:
                    self.db.log_credential(self.session_id, username, "<ntlm-rdp>", service="rdp")
                    self.db.flag_high_interest(self.session_id, f"RDP NLA credential: {username} — T1021.001")

                # Respond with MCS Connect Response then disconnect
                # (triggers retries and credential re-sends)
                self.transport.close()

    def _extract_rdp_username(self, data: bytes) -> str:
        try:
            # Cookie in CR packet: "Cookie: mstshash=USERNAME\r\n"
            if b"mstshash=" in data:
                start = data.index(b"mstshash=") + 9
                end = data.index(b"\r\n", start)
                return data[start:end].decode("ascii", errors="replace")
        except Exception:
            pass
        return ""

    def _extract_ntlm_from_credssp(self, data: bytes) -> str:
        """Best-effort NTLM username from CredSSP TSRequest."""
        try:
            idx = data.find(b"NTLMSSP\x00")
            if idx == -1:
                return ""
            blob = data[idx:]
            msg_type = struct.unpack("<I", blob[8:12])[0]
            if msg_type != 3:
                return ""
            ulen = struct.unpack("<H", blob[36:38])[0]
            uoff = struct.unpack("<I", blob[40:44])[0]
            return blob[uoff:uoff + ulen].decode("utf-16-le", errors="replace")
        except Exception:
            return ""

    def connection_lost(self, exc):
        if self.session_id:
            self.db.close_session(self.session_id, int(time.time() - self.connect_time))


# ─── VNC (5900) ──────────────────────────────────────────────────────────────

class VNCHoneypotProtocol(asyncio.Protocol):
    """
    VNC RFB protocol honeypot.
    Logs every connection and authentication attempt.
    VNC is heavily scanned for unauthenticated instances.
    """
    def __init__(self, db: DB, hplogger: HoneypotLogger):
        self.db = db
        self.hplogger = hplogger
        self.transport = None
        self.peer_ip = None
        self.session_id = None
        self.connect_time = time.time()
        self.state = "version"
        self.challenge = None

    def connection_made(self, transport):
        self.transport = transport
        self.peer_ip = transport.get_extra_info("peername")[0]
        self.session_id = self.db.create_session(self.peer_ip, service="vnc")
        logger.info(f"[VNC] Connection from {self.peer_ip}")
        asyncio.ensure_future(enrich_ip(self.peer_ip))
        # Send RFB version
        self.transport.write(b"RFB 003.008\n")

    def data_received(self, data: bytes):
        raw = data.decode("ascii", errors="replace").strip()
        self.db.log_command(self.session_id, f"[VNC] {raw}")
        self.hplogger.log_event("vnc_data", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "data": raw[:100],
            "state": self.state,
        })

        if self.state == "version":
            # Client sent version
            self.state = "security"
            # Offer security types: 1=None (no auth), 2=VNC Auth
            # Offer both — no-auth instances get flagged by scanners immediately
            self.transport.write(bytes([
                0x02,   # 2 security types
                0x01,   # None (no auth)
                0x02,   # VNC Authentication
            ]))

        elif self.state == "security":
            # Client chose security type
            if data and data[0] == 0x01:
                # Chose "None" — unauthenticated access
                self.db.flag_high_interest(
                    self.session_id,
                    "VNC unauthenticated access (security type=None) — T1021.005"
                )
                self.db.update_session_auth(self.session_id, "anonymous", "none", success=True)
                # Security result: OK
                self.transport.write(struct.pack(">I", 0))
                self.state = "authenticated"
            elif data and data[0] == 0x02:
                # Chose VNC Auth — send challenge
                import os
                self.challenge = os.urandom(16)
                self.transport.write(self.challenge)
                self.state = "auth_response"
            else:
                self.transport.close()

        elif self.state == "auth_response":
            # Client sent DES-encrypted challenge response
            response_hex = data.hex()
            self.db.log_credential(self.session_id, "vnc", f"<challenge-response:{response_hex[:16]}>", service="vnc")
            self.db.flag_high_interest(self.session_id, f"VNC auth attempt — T1021.005 challenge={self.challenge.hex()[:16]}")
            # Always fail auth
            self.transport.write(struct.pack(">I", 1))  # Failed
            msg = b"Authentication failed"
            self.transport.write(struct.pack(">I", len(msg)) + msg)
            self.transport.close()

        elif self.state == "authenticated":
            # Post-auth — client init
            self.db.flag_high_interest(self.session_id, "VNC authenticated session — T1021.005")
            # Send ServerInit: 800x600, 32bpp
            name = b"Cascade Medical - Clinical Workstation"
            server_init = (
                struct.pack(">HH", 800, 600) +  # width, height
                bytes([32, 24, 0, 1]) +          # bpp, depth, big-endian, true-colour
                struct.pack(">HHHBBBBBB", 255, 255, 255, 16, 8, 0, 0, 0, 0) +
                bytes([0, 0, 0]) +              # padding
                struct.pack(">I", len(name)) + name
            )
            self.transport.write(server_init)
            self.state = "session"

    def connection_lost(self, exc):
        if self.session_id:
            self.db.close_session(self.session_id, int(time.time() - self.connect_time))


# ─── Telnet (23) ─────────────────────────────────────────────────────────────

class TelnetHoneypotProtocol(asyncio.Protocol):
    """
    Telnet honeypot — port 23.
    Telnet sends credentials in plaintext — we capture everything.
    Very heavily scanned by IoT botnets.
    """
    def __init__(self, db: DB, hplogger: HoneypotLogger):
        self.db = db
        self.hplogger = hplogger
        self.transport = None
        self.peer_ip = None
        self.session_id = None
        self.connect_time = time.time()
        self.state = "username"
        self.username = ""
        self.buffer = ""

    def connection_made(self, transport):
        self.transport = transport
        self.peer_ip = transport.get_extra_info("peername")[0]
        self.session_id = self.db.create_session(self.peer_ip, service="telnet")
        logger.info(f"[Telnet] Connection from {self.peer_ip}")
        asyncio.ensure_future(enrich_ip(self.peer_ip))
        # Telnet negotiation then banner
        self.transport.write(
            bytes([0xff, 0xfb, 0x01]) +   # WILL ECHO
            bytes([0xff, 0xfb, 0x03]) +   # WILL SUPPRESS-GO-AHEAD
            bytes([0xff, 0xfd, 0x1f]) +   # DO NAWS
            b"\r\nCascade Medical Center\r\nEMR Terminal Access\r\n\r\nlogin: "
        )

    def data_received(self, data: bytes):
        # Strip telnet IAC sequences
        clean = b""
        i = 0
        while i < len(data):
            if data[i] == 0xff and i + 2 < len(data):
                i += 3
            else:
                clean += bytes([data[i]])
                i += 1

        text = clean.decode("ascii", errors="replace").replace("\r", "").replace("\x00", "")

        if self.state == "username":
            self.buffer += text
            self.transport.write(text.encode())  # echo
            if "\n" in self.buffer:
                self.username = self.buffer.strip()
                self.buffer = ""
                self.state = "password"
                self.transport.write(b"\r\nPassword: ")

        elif self.state == "password":
            self.buffer += text
            # Don't echo password
            if "\n" in self.buffer:
                password = self.buffer.strip()
                self.buffer = ""
                self.db.log_credential(self.session_id, self.username, password, service="telnet")
                self.db.update_session_auth(self.session_id, self.username, password, success=False)
                self.hplogger.log_event("telnet_auth", {
                    "session_id": self.session_id,
                    "ip": self.peer_ip,
                    "username": self.username,
                    "password": password,  # Telnet is plaintext — we get it all
                })
                self.db.flag_high_interest(
                    self.session_id,
                    f"Telnet plaintext credentials: {self.username}/{password} — T1078"
                )
                # Always fail
                asyncio.ensure_future(self._fail_login())

    async def _fail_login(self):
        await asyncio.sleep(1.5)
        self.transport.write(b"\r\nLogin incorrect\r\n\r\nlogin: ")
        self.username = ""
        self.state = "username"

    def connection_lost(self, exc):
        if self.session_id:
            self.db.close_session(self.session_id, int(time.time() - self.connect_time))


# ─── MSSQL (1433) ────────────────────────────────────────────────────────────

FAKE_MSSQL_TABLES = {
    "epic_emr": ["dbo.Patients","dbo.Encounters","dbo.Orders","dbo.Results","dbo.Medications",
                 "dbo.Providers","dbo.InsuranceClaims","dbo.AuditLog"],
    "CascadeEMR": ["dbo.PatientDemographics","dbo.ClinicalNotes","dbo.PrescriptionHistory",
                   "dbo.Billing","dbo.DiagnosisCodes","dbo.LabOrders"],
    "master": ["sys.databases","sys.objects","sys.server_principals"],
}

class MSSQLHoneypotProtocol(asyncio.Protocol):
    """
    MSSQL TDS protocol honeypot — port 1433.
    sa account brute-forcing is constant (Josh's note).
    Logs every login attempt and query.
    """
    def __init__(self, db: DB, hplogger: HoneypotLogger):
        self.db = db
        self.hplogger = hplogger
        self.transport = None
        self.peer_ip = None
        self.session_id = None
        self.connect_time = time.time()
        self.buffer = b""
        self.authenticated = False
        self.query_count = 0

    def connection_made(self, transport):
        self.transport = transport
        self.peer_ip = transport.get_extra_info("peername")[0]
        self.session_id = self.db.create_session(self.peer_ip, service="mssql")
        logger.info(f"[MSSQL] Connection from {self.peer_ip}")
        asyncio.ensure_future(enrich_ip(self.peer_ip))

    def data_received(self, data: bytes):
        self.buffer += data
        self.hplogger.log_event("mssql_data", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "hex": data[:32].hex(),
            "length": len(data),
        })

        if len(data) >= 8:
            pkt_type = data[0]

            # TDS PreLogin (0x12)
            if pkt_type == 0x12:
                self._send_prelogin_response()

            # TDS Login7 (0x10)
            elif pkt_type == 0x10:
                self._handle_login(data)

            # TDS SQL Batch (0x01)
            elif pkt_type == 0x01 and self.authenticated:
                query = self._extract_query(data)
                self._handle_query(query)

    def _send_prelogin_response(self):
        """TDS PreLogin response — version + encryption."""
        payload = (
            b"\x04\x00\x1a\x00\x06"   # VERSION option
            b"\x01\x00\x20\x00\x01"   # ENCRYPTION = NOT_SUP
            b"\xff"                     # terminator
            b"\x16\x00\x00\x00\x00\x00"  # version: SQL Server 2019
            b"\x02"                     # encryption: NOT_SUP
        )
        tds_header = bytes([0x04, 0x01]) + struct.pack(">H", len(payload) + 8) + bytes([0x00, 0x00, 0x01, 0x00])
        self.transport.write(tds_header + payload)

    def _handle_login(self, data: bytes):
        username, password = self._extract_login_creds(data)
        self.db.log_credential(self.session_id, username, password or "<obfuscated>", service="mssql")
        self.hplogger.log_event("mssql_login", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "username": username,
        })

        weak = {"sa", "admin", "Administrator", "cascade", "mssql", "root", ""}
        if username in weak or (password and len(password) <= 8):
            self.authenticated = True
            self.db.update_session_auth(self.session_id, username, "<mssql>", success=True)
            self.db.flag_high_interest(self.session_id, f"MSSQL login accepted: {username} — T1078")
            self._send_login_ack(username)
        else:
            self._send_login_error(username)

    def _extract_login_creds(self, data: bytes):
        try:
            # Login7 packet: fixed header at offset 8, username at various offsets
            # Username offset at bytes 36-37 (from packet start)
            if len(data) < 50:
                return "sa", ""
            uoff = struct.unpack("<H", data[36:38])[0]
            ulen = struct.unpack("<H", data[38:40])[0]
            username = data[8 + uoff:8 + uoff + ulen * 2].decode("utf-16-le", errors="replace")
            return username or "sa", ""
        except Exception:
            return "sa", ""

    def _send_login_ack(self, username: str):
        # TDS LOGINACK token
        prog = b"Microsoft SQL Server"
        payload = (
            bytes([0xad]) +              # LOGINACK token
            struct.pack("<H", 1 + len(prog) + 4 + 4) +
            bytes([0x01]) +             # interface
            bytes([0x74, 0x00, 0x04, 0x00]) +  # tdsVersion
            bytes([len(prog)]) + prog +
            bytes([0x0f, 0x00, 0x07, 0xd0]) +  # server version
            bytes([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # DONE token
        )
        tds = bytes([0x04, 0x01]) + struct.pack(">H", len(payload) + 8) + bytes([0x00, 0x00, 0x01, 0x00])
        self.transport.write(tds + payload)

    def _send_login_error(self, username: str):
        msg = f"Login failed for user '{username}'.".encode("utf-16-le")
        payload = (
            bytes([0xaa]) +             # ERROR token
            struct.pack("<H", len(msg) + 17) +
            struct.pack("<I", 18456) +  # error number
            bytes([0x01, 0x0e]) +       # state, class
            struct.pack("<H", len(msg) // 2) + msg +
            bytes([0x00, 0x00])
        )
        tds = bytes([0x04, 0x01]) + struct.pack(">H", len(payload) + 8) + bytes([0x00, 0x00, 0x01, 0x00])
        self.transport.write(tds + payload)
        self.transport.close()

    def _extract_query(self, data: bytes) -> str:
        try:
            return data[8:].decode("utf-16-le", errors="replace").strip()
        except Exception:
            return data[8:].decode("ascii", errors="replace").strip()

    def _handle_query(self, query: str):
        self.query_count += 1
        self.db.log_command(self.session_id, f"[MSSQL] {query}")
        self.hplogger.log_event("mssql_query", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "query": query,
        })
        q = query.lower()

        if "xp_cmdshell" in q:
            self.db.flag_high_interest(self.session_id, f"CRITICAL: xp_cmdshell — RCE attempt T1059: {query}")
            self._send_text_result("xp_cmdshell disabled")
        elif "exec" in q and ("master" in q or "xp_" in q):
            self.db.flag_high_interest(self.session_id, f"MSSQL stored proc exec: {query}")
            self._send_text_result("Permission denied")
        elif "select" in q and ("password" in q or "hash" in q or "sys.sql_logins" in q):
            self.db.flag_high_interest(self.session_id, f"MSSQL credential query: {query} — T1003")
            self._send_text_result("sa\t0x020012345FAKE")
        elif "show databases" in q or "select name" in q:
            self._send_text_result("\n".join(FAKE_MSSQL_TABLES.keys()))
        elif "select" in q and "patients" in q:
            self.db.flag_high_interest(self.session_id, f"MSSQL patient data query — T1530: {query}")
            self._send_text_result("MRN-482821\tMargaret Williams\t1958-04-12\t***-**-4821")
        else:
            self._send_text_result("")

    def _send_text_result(self, text: str):
        payload = (bytes([0xfd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
        tds = bytes([0x04, 0x01]) + struct.pack(">H", len(payload) + 8) + bytes([0x00, 0x00, 0x01, 0x00])
        self.transport.write(tds + payload)

    def connection_lost(self, exc):
        if self.session_id:
            self.db.close_session(self.session_id, int(time.time() - self.connect_time))


# ─── Elasticsearch (9200) ────────────────────────────────────────────────────

class ElasticsearchHoneypotProtocol(asyncio.Protocol):
    """
    Elasticsearch REST API honeypot — port 9200.
    Unauthenticated Elasticsearch gets hit within minutes (Josh).
    Serves fake patient index data.
    """
    def __init__(self, db: DB, hplogger: HoneypotLogger):
        self.db = db
        self.hplogger = hplogger
        self.transport = None
        self.peer_ip = None
        self.session_id = None
        self.connect_time = time.time()
        self.buffer = b""

    def connection_made(self, transport):
        self.transport = transport
        self.peer_ip = transport.get_extra_info("peername")[0]
        self.session_id = self.db.create_session(self.peer_ip, service="elasticsearch")
        logger.info(f"[ES] Connection from {self.peer_ip}")
        asyncio.ensure_future(enrich_ip(self.peer_ip))

    def data_received(self, data: bytes):
        self.buffer += data
        if b"\r\n\r\n" in self.buffer:
            request = self.buffer.decode("utf-8", errors="replace")
            self.buffer = b""
            self._handle_http(request)

    def _handle_http(self, request: str):
        lines = request.split("\r\n")
        if not lines:
            return
        method, path = lines[0].split()[:2] if len(lines[0].split()) >= 2 else ("GET", "/")

        self.db.log_command(self.session_id, f"[ES] {method} {path}")
        self.hplogger.log_event("elasticsearch_request", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "method": method,
            "path": path,
        })

        # Route responses
        if path == "/" or path == "":
            body = json.dumps({
                "name": "cascade-es-node01",
                "cluster_name": "cascade-medical",
                "version": {"number": "8.13.0", "build_flavor": "default"},
                "tagline": "You Know, for Search"
            })
        elif "_cat/indices" in path:
            self.db.flag_high_interest(self.session_id, "ES index enumeration — T1083")
            body = "\n".join([
                "green open patients          48821 2.4gb",
                "green open lab_results       182441 8.1gb",
                "green open radiology_reports 29812 1.8gb",
                "green open pharmacy_orders   94221 3.2gb",
                "green open audit_log         482910 12.4gb",
            ])
            self._send_response(200, body, content_type="text/plain")
            return
        elif "_cluster/health" in path:
            body = json.dumps({"cluster_name":"cascade-medical","status":"green","number_of_nodes":1})
        elif "patients" in path and "_search" in path:
            self.db.flag_high_interest(self.session_id, "CRITICAL: ES patient data search — T1530 PHI exposure")
            body = json.dumps({
                "hits": {"total": {"value": 48821},
                "hits": [{"_index":"patients","_id":"MRN-482821",
                          "_source":{"name":"Margaret Williams","dob":"1958-04-12",
                                     "ssn":"***-**-4821","diagnosis":"Type 2 Diabetes","attending":"Dr. Sarah Chen"}}]}})
        elif method == "DELETE":
            self.db.flag_high_interest(self.session_id, f"CRITICAL: ES DELETE {path} — T1485 Data Destruction")
            body = json.dumps({"acknowledged": True})
        elif method == "PUT" and "settings" in path:
            self.db.flag_high_interest(self.session_id, f"ES settings modification: {path} — T1562")
            body = json.dumps({"acknowledged": True})
        elif "_xpack/security" in path or "_security" in path:
            self.db.flag_high_interest(self.session_id, "ES security configuration probe")
            body = json.dumps({"error": "Security not enabled", "status": 400})
            self._send_response(400, body)
            return
        else:
            body = json.dumps({"acknowledged": True})

        self._send_response(200, body)

    def _send_response(self, status: int, body: str, content_type: str = "application/json"):
        status_text = {200: "OK", 400: "Bad Request", 401: "Unauthorized", 404: "Not Found"}.get(status, "OK")
        response = (
            f"HTTP/1.1 {status} {status_text}\r\n"
            f"Content-Type: {content_type}; charset=UTF-8\r\n"
            f"Content-Length: {len(body.encode())}\r\n"
            f"X-elastic-product: Elasticsearch\r\n"
            f"\r\n"
            f"{body}"
        )
        self.transport.write(response.encode())

    def connection_lost(self, exc):
        if self.session_id:
            self.db.close_session(self.session_id, int(time.time() - self.connect_time))


# ─── SMTP (25/587) ───────────────────────────────────────────────────────────

class SMTPHoneypotProtocol(asyncio.Protocol):
    """
    SMTP honeypot — ports 25 and 587.
    Open relays get abused fast (Josh).
    Logs every AUTH attempt and message.
    """
    def __init__(self, db: DB, hplogger: HoneypotLogger):
        self.db = db
        self.hplogger = hplogger
        self.transport = None
        self.peer_ip = None
        self.session_id = None
        self.connect_time = time.time()
        self.state = "greeting"
        self.mail_from = ""
        self.rcpt_to = []
        self.auth_user = ""
        self.buffer = b""

    def connection_made(self, transport):
        self.transport = transport
        self.peer_ip = transport.get_extra_info("peername")[0]
        self.session_id = self.db.create_session(self.peer_ip, service="smtp")
        logger.info(f"[SMTP] Connection from {self.peer_ip}")
        asyncio.ensure_future(enrich_ip(self.peer_ip))
        self.transport.write(b"220 cascade-mail.cascademedical.local ESMTP Postfix (Ubuntu)\r\n")

    def data_received(self, data: bytes):
        self.buffer += data
        while b"\r\n" in self.buffer:
            line, self.buffer = self.buffer.split(b"\r\n", 1)
            self._handle_line(line.decode("ascii", errors="replace").strip())

    def _handle_line(self, line: str):
        self.db.log_command(self.session_id, f"[SMTP] {line}")
        upper = line.upper()

        if upper.startswith("EHLO") or upper.startswith("HELO"):
            self.transport.write(
                b"250-cascade-mail.cascademedical.local\r\n"
                b"250-PIPELINING\r\n"
                b"250-SIZE 10240000\r\n"
                b"250-AUTH LOGIN PLAIN\r\n"
                b"250-AUTH=LOGIN PLAIN\r\n"
                b"250 SMTPUTF8\r\n"
            )
        elif upper.startswith("AUTH"):
            parts = line.split()
            mechanism = parts[1].upper() if len(parts) > 1 else "PLAIN"
            if mechanism == "PLAIN" and len(parts) > 2:
                import base64
                try:
                    decoded = base64.b64decode(parts[2]).decode("ascii", errors="replace")
                    creds = decoded.split("\x00")
                    username = creds[1] if len(creds) > 1 else ""
                    password = creds[2] if len(creds) > 2 else ""
                    self.db.log_credential(self.session_id, username, password, service="smtp")
                    self.db.flag_high_interest(self.session_id, f"SMTP AUTH PLAIN credentials: {username}/{password} — T1078")
                    self.hplogger.log_event("smtp_auth", {"session_id": self.session_id, "ip": self.peer_ip,
                                                          "username": username, "password": password})
                except Exception:
                    pass
            self.transport.write(b"235 2.7.0 Authentication successful\r\n")
            self.db.update_session_auth(self.session_id, self.auth_user or "smtp", "<smtp>", success=True)
        elif upper.startswith("MAIL FROM"):
            self.mail_from = line
            self.transport.write(b"250 2.1.0 Ok\r\n")
        elif upper.startswith("RCPT TO"):
            self.rcpt_to.append(line)
            self.transport.write(b"250 2.1.5 Ok\r\n")
            if len(self.rcpt_to) > 5:
                self.db.flag_high_interest(self.session_id, f"SMTP open relay abuse — multiple recipients T1566")
        elif upper == "DATA":
            self.state = "data"
            self.transport.write(b"354 End data with <CR><LF>.<CR><LF>\r\n")
        elif upper == "QUIT":
            self.transport.write(b"221 2.0.0 Bye\r\n")
            self.transport.close()
        elif upper == "VRFY" or upper.startswith("VRFY "):
            user = line[5:] if len(line) > 5 else ""
            self.db.flag_high_interest(self.session_id, f"SMTP VRFY user enumeration: {user} — T1087")
            self.transport.write(f"252 Cannot VRFY user, but will accept message\r\n".encode())
        elif upper == "EXPN" or upper.startswith("EXPN "):
            self.db.flag_high_interest(self.session_id, f"SMTP EXPN mailing list enumeration — T1087")
            self.transport.write(b"252 Cannot EXPN\r\n")
        elif self.state == "data":
            if line == ".":
                self.state = "greeting"
                self.db.flag_high_interest(self.session_id,
                    f"SMTP message sent: FROM={self.mail_from} TO={self.rcpt_to} — T1566 Phishing/Relay")
                self.transport.write(b"250 2.0.0 Ok: queued as FAKE12345\r\n")
            # else: accumulate message body (not stored)
        else:
            self.transport.write(b"500 5.5.1 Command unrecognized\r\n")

    def connection_lost(self, exc):
        if self.session_id:
            self.db.close_session(self.session_id, int(time.time() - self.connect_time))


# ─── HL7 (2575) ──────────────────────────────────────────────────────────────

class HL7HoneypotProtocol(asyncio.Protocol):
    """
    HL7 MLLP honeypot — port 2575.
    HL7 is the medical records interchange protocol.
    Exposed HL7 interfaces = direct patient data access.
    """
    def __init__(self, db: DB, hplogger: HoneypotLogger):
        self.db = db
        self.hplogger = hplogger
        self.transport = None
        self.peer_ip = None
        self.session_id = None
        self.connect_time = time.time()
        self.buffer = b""

    def connection_made(self, transport):
        self.transport = transport
        self.peer_ip = transport.get_extra_info("peername")[0]
        self.session_id = self.db.create_session(self.peer_ip, service="hl7")
        self.db.flag_high_interest(self.session_id, "HL7 MLLP connection — medical records interface T1530")
        logger.info(f"[HL7] Connection from {self.peer_ip}")
        asyncio.ensure_future(enrich_ip(self.peer_ip))

    def data_received(self, data: bytes):
        self.buffer += data
        # MLLP: 0x0b ... 0x1c 0x0d
        if b"\x1c\x0d" in self.buffer:
            msg = self.buffer.decode("ascii", errors="replace")
            self.db.log_command(self.session_id, f"[HL7] {msg[:200]}")
            self.hplogger.log_event("hl7_message", {
                "session_id": self.session_id,
                "ip": self.peer_ip,
                "message": msg[:500],
            })
            self.db.flag_high_interest(self.session_id, f"HL7 message received — PHI in transit T1530")
            # Send ACK
            ack = (b"\x0b"
                   b"MSH|^~\\&|CASCADE|CMC|ATTACKER|EXT|20240603120000||ACK|MSG001|P|2.5\r"
                   b"MSA|AA|MSG001|Message accepted\r"
                   b"\x1c\x0d")
            self.transport.write(ack)
            self.buffer = b""

    def connection_lost(self, exc):
        if self.session_id:
            self.db.close_session(self.session_id, int(time.time() - self.connect_time))


# ─── Server Starters ─────────────────────────────────────────────────────────

async def start_rdp_server(host, port, db, hplogger):
    loop = asyncio.get_running_loop()
    s = await loop.create_server(lambda: RDPHoneypotProtocol(db, hplogger), host, port)
    logger.info(f"[RDP] {host}:{port}")
    return s

async def start_vnc_server(host, port, db, hplogger):
    loop = asyncio.get_running_loop()
    s = await loop.create_server(lambda: VNCHoneypotProtocol(db, hplogger), host, port)
    logger.info(f"[VNC] {host}:{port}")
    return s

async def start_telnet_server(host, port, db, hplogger):
    loop = asyncio.get_running_loop()
    s = await loop.create_server(lambda: TelnetHoneypotProtocol(db, hplogger), host, port)
    logger.info(f"[Telnet] {host}:{port}")
    return s

async def start_mssql_server(host, port, db, hplogger):
    loop = asyncio.get_running_loop()
    s = await loop.create_server(lambda: MSSQLHoneypotProtocol(db, hplogger), host, port)
    logger.info(f"[MSSQL] {host}:{port}")
    return s

async def start_elasticsearch_server(host, port, db, hplogger):
    loop = asyncio.get_running_loop()
    s = await loop.create_server(lambda: ElasticsearchHoneypotProtocol(db, hplogger), host, port)
    logger.info(f"[Elasticsearch] {host}:{port}")
    return s

async def start_smtp_server(host, port, db, hplogger):
    loop = asyncio.get_running_loop()
    s = await loop.create_server(lambda: SMTPHoneypotProtocol(db, hplogger), host, port)
    logger.info(f"[SMTP] {host}:{port}")
    return s

async def start_hl7_server(host, port, db, hplogger):
    loop = asyncio.get_running_loop()
    s = await loop.create_server(lambda: HL7HoneypotProtocol(db, hplogger), host, port)
    logger.info(f"[HL7] {host}:{port}")
    return s
