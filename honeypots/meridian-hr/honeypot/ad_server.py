"""
Fake Active Directory Honeypot — Meridian HR Solutions
Simulates: LDAP (389), LDAPS (636), Kerberos (88), Global Catalog (3268)

What attackers do against AD and what we log:
  - LDAP anonymous bind attempts (T1087.002 - Domain Account Discovery)
  - LDAP search queries (enumerating users, groups, SPNs, GPOs)
  - Kerberoasting (T1558.003 - requesting TGS for service accounts)
  - AS-REP Roasting (T1558.004 - accounts with no pre-auth required)
  - Password spray via LDAP bind (T1110.003)
  - BloodHound/SharpHound collection patterns
  - DCSync enumeration patterns
"""

import asyncio
import struct
import logging
import time
import re
from datetime import datetime
from .db import DB
from .logger import HoneypotLogger
from .enrichment import enrich_ip

logger = logging.getLogger("ad_honeypot")

# ─── Fake Domain Info ─────────────────────────────────────────────────────────

DOMAIN = "MERIDIANHR"
DOMAIN_FQDN = "meridianhr.local"
DC_NAME = "DC01"
DC_FQDN = f"DC01.{DOMAIN_FQDN}"

# Fake users — designed to attract Kerberoasting (SPNs) and AS-REP roasting
FAKE_USERS = [
    {
        "cn": "John Smith", "sAMAccountName": "jsmith", "mail": "j.smith@meridianhr.com",
        "title": "Director of HR", "department": "Human Resources",
        "memberOf": ["CN=HR-Admins,OU=Groups,DC=meridianhr,DC=local",
                     "CN=Domain Users,CN=Users,DC=meridianhr,DC=local"],
        "userAccountControl": "512",  # Normal account
        "servicePrincipalName": [],
        "lastLogon": "133612345600000000",
    },
    {
        "cn": "svc_payroll", "sAMAccountName": "svc_payroll", "mail": "svc_payroll@meridianhr.com",
        "title": "Service Account", "department": "IT",
        "memberOf": ["CN=Service-Accounts,OU=Groups,DC=meridianhr,DC=local"],
        "userAccountControl": "512",
        # SPN set — this account is Kerberoastable
        "servicePrincipalName": ["MSSQLSvc/meridian-db-primary.meridianhr.local:1433",
                                  "MSSQLSvc/meridian-db-primary.meridianhr.local"],
        "lastLogon": "133612300000000000",
    },
    {
        "cn": "svc_backup", "sAMAccountName": "svc_backup", "mail": "svc_backup@meridianhr.com",
        "title": "Backup Service Account", "department": "IT",
        "memberOf": ["CN=Backup-Operators,CN=Builtin,DC=meridianhr,DC=local"],
        "userAccountControl": "512",
        "servicePrincipalName": ["BackupExec/meridian-hrprod-01.meridianhr.local"],
        "lastLogon": "133610000000000000",
    },
    {
        "cn": "hradmin", "sAMAccountName": "hradmin", "mail": "hradmin@meridianhr.com",
        "title": "HR Administrator", "department": "Human Resources",
        "memberOf": ["CN=HR-Admins,OU=Groups,DC=meridianhr,DC=local",
                     "CN=Domain Admins,CN=Users,DC=meridianhr,DC=local"],
        "userAccountControl": "512",
        "servicePrincipalName": [],
        "lastLogon": "133612400000000000",
    },
    {
        "cn": "svc_adconnect", "sAMAccountName": "svc_adconnect", "mail": "",
        "title": "Azure AD Connect Service", "department": "IT",
        "memberOf": ["CN=Domain Users,CN=Users,DC=meridianhr,DC=local"],
        # No pre-auth required — AS-REP Roastable
        "userAccountControl": "4194816",
        "servicePrincipalName": [],
        "lastLogon": "133600000000000000",
    },
    {
        "cn": "Amanda Torres", "sAMAccountName": "atorres", "mail": "a.torres@meridianhr.com",
        "title": "Payroll Manager", "department": "Payroll",
        "memberOf": ["CN=Payroll-Staff,OU=Groups,DC=meridianhr,DC=local"],
        "userAccountControl": "512",
        "servicePrincipalName": [],
        "lastLogon": "133612350000000000",
    },
    {
        "cn": "Kevin Park", "sAMAccountName": "kpark", "mail": "k.park@meridianhr.com",
        "title": "Systems Administrator", "department": "IT",
        "memberOf": ["CN=Domain Admins,CN=Users,DC=meridianhr,DC=local",
                     "CN=Enterprise Admins,CN=Users,DC=meridianhr,DC=local"],
        "userAccountControl": "512",
        "servicePrincipalName": [],
        "lastLogon": "133612398000000000",
    },
]

FAKE_GROUPS = [
    {"cn": "Domain Admins", "description": "Designated administrators of the domain",
     "member": ["CN=kpark,OU=Users,DC=meridianhr,DC=local", "CN=hradmin,OU=Users,DC=meridianhr,DC=local"]},
    {"cn": "Enterprise Admins", "description": "Enterprise-wide administrators",
     "member": ["CN=kpark,OU=Users,DC=meridianhr,DC=local"]},
    {"cn": "HR-Admins", "description": "HR system administrators",
     "member": ["CN=jsmith,OU=Users,DC=meridianhr,DC=local", "CN=hradmin,OU=Users,DC=meridianhr,DC=local"]},
    {"cn": "Payroll-Staff", "description": "Payroll processing staff",
     "member": ["CN=atorres,OU=Users,DC=meridianhr,DC=local"]},
    {"cn": "Backup-Operators", "description": "Members can bypass file/dir permissions for backup",
     "member": ["CN=svc_backup,OU=Users,DC=meridianhr,DC=local"]},
    {"cn": "Service-Accounts", "description": "Service and automation accounts",
     "member": ["CN=svc_payroll,OU=Users,DC=meridianhr,DC=local",
                "CN=svc_backup,OU=Users,DC=meridianhr,DC=local",
                "CN=svc_adconnect,OU=Users,DC=meridianhr,DC=local"]},
]

# ─── LDAP Protocol Helpers ────────────────────────────────────────────────────

def encode_ldap_string(s: str) -> bytes:
    b = s.encode("utf-8")
    return bytes([0x04, len(b)]) + b

def encode_ldap_sequence(content: bytes) -> bytes:
    return bytes([0x30, len(content)]) + content

def encode_ldap_set(content: bytes) -> bytes:
    return bytes([0x31, len(content)]) + content

def encode_length(n: int) -> bytes:
    if n < 128:
        return bytes([n])
    elif n < 256:
        return bytes([0x81, n])
    else:
        return bytes([0x82, (n >> 8) & 0xFF, n & 0xFF])

def make_ldap_bind_response(result_code: int = 0, msg_id: int = 1) -> bytes:
    """Craft a minimal LDAP BindResponse."""
    # BindResponse: [APPLICATION 1]
    result = bytes([0x0a, 0x01, result_code])  # resultCode
    matched_dn = bytes([0x04, 0x00])            # matchedDN (empty)
    diagnostic = bytes([0x04, 0x00])            # diagnosticMessage (empty)
    bind_resp_content = result + matched_dn + diagnostic
    bind_resp = bytes([0x61]) + encode_length(len(bind_resp_content)) + bind_resp_content

    # Message envelope
    msg_id_enc = bytes([0x02, 0x01, msg_id & 0xFF])
    envelope = msg_id_enc + bind_resp
    return bytes([0x30]) + encode_length(len(envelope)) + envelope

def make_ldap_search_result_entry(dn: str, attributes: dict, msg_id: int) -> bytes:
    """Craft a SearchResultEntry."""
    dn_enc = encode_ldap_string(dn)

    attrs_content = b""
    for attr_name, values in attributes.items():
        if not isinstance(values, list):
            values = [values]
        vals_content = b"".join(encode_ldap_string(str(v)) for v in values if v)
        if vals_content:
            val_set = bytes([0x31]) + encode_length(len(vals_content)) + vals_content
            name_enc = encode_ldap_string(attr_name)
            attr_seq = name_enc + val_set
            attrs_content += bytes([0x30]) + encode_length(len(attr_seq)) + attr_seq

    attrs_seq = bytes([0x30]) + encode_length(len(attrs_content)) + attrs_content

    entry_content = dn_enc + attrs_seq
    # [APPLICATION 4] SearchResultEntry
    entry = bytes([0x64]) + encode_length(len(entry_content)) + entry_content

    msg_id_enc = bytes([0x02, 0x01, msg_id & 0xFF])
    envelope = msg_id_enc + entry
    return bytes([0x30]) + encode_length(len(envelope)) + envelope

def make_ldap_search_result_done(msg_id: int, result_code: int = 0) -> bytes:
    """Craft a SearchResultDone."""
    result = bytes([0x0a, 0x01, result_code])
    matched_dn = bytes([0x04, 0x00])
    diagnostic = bytes([0x04, 0x00])
    done_content = result + matched_dn + diagnostic
    # [APPLICATION 5] SearchResultDone
    done = bytes([0x65]) + encode_length(len(done_content)) + done_content

    msg_id_enc = bytes([0x02, 0x01, msg_id & 0xFF])
    envelope = msg_id_enc + done
    return bytes([0x30]) + encode_length(len(envelope)) + envelope

def make_ldap_error(msg_id: int, result_code: int = 32, msg: str = "") -> bytes:
    """Generic LDAP error response."""
    result = bytes([0x0a, 0x01, result_code])
    matched_dn = bytes([0x04, 0x00])
    diag_b = msg.encode()
    diagnostic = bytes([0x04, len(diag_b)]) + diag_b
    content = result + matched_dn + diagnostic
    resp = bytes([0x65]) + encode_length(len(content)) + content
    msg_id_enc = bytes([0x02, 0x01, msg_id & 0xFF])
    envelope = msg_id_enc + resp
    return bytes([0x30]) + encode_length(len(envelope)) + envelope

# ─── LDAP Server ─────────────────────────────────────────────────────────────

def _detect_bloodhound(query: str) -> bool:
    """Detect BloodHound/SharpHound collection patterns."""
    bh_patterns = [
        "objectclass=user", "objectclass=group", "objectclass=computer",
        "objectclass=grouppolicycontainer", "ms-mcs-admpwd",
        "serviceprincipalname=*", "useraccountcontrol",
        "samaccounttype=805306368", "samaccounttype=268435456",
        "objectclass=organizationalunit", "gplink", "gpcfilesyspath",
        "admincount=1", "isdeleted=false",
    ]
    q_lower = query.lower()
    return sum(1 for p in bh_patterns if p in q_lower) >= 2

def _detect_kerberoast(query: str) -> bool:
    return "serviceprincipalname" in query.lower() and "user" in query.lower()

def _detect_asrep(query: str) -> bool:
    return "4194816" in query or "4194304" in query or "dont_req_preauth" in query.lower()

def _extract_query_str(data: bytes) -> str:
    """Best-effort extract readable text from LDAP search filter."""
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        return repr(data)


class LDAPHoneypotProtocol(asyncio.Protocol):
    def __init__(self, db: DB, hplogger: HoneypotLogger):
        self.db = db
        self.hplogger = hplogger
        self.transport = None
        self.peer_ip = None
        self.session_id = None
        self.connect_time = time.time()
        self.buffer = b""
        self.bound = False
        self.bind_dn = ""
        self.query_count = 0

    def connection_made(self, transport):
        self.transport = transport
        self.peer_ip = transport.get_extra_info("peername")[0]
        self.session_id = self.db.create_session(self.peer_ip, service="ldap")
        logger.info(f"[LDAP] Connection from {self.peer_ip}")
        asyncio.ensure_future(enrich_ip(self.peer_ip))

    def data_received(self, data: bytes):
        self.buffer += data
        while self._has_complete_message():
            self._process_next_message()

    def _has_complete_message(self) -> bool:
        if len(self.buffer) < 2:
            return False
        if self.buffer[0] != 0x30:
            return False
        if self.buffer[1] < 128:
            total = self.buffer[1] + 2
        elif self.buffer[1] == 0x81:
            if len(self.buffer) < 3:
                return False
            total = self.buffer[2] + 3
        elif self.buffer[1] == 0x82:
            if len(self.buffer) < 4:
                return False
            total = ((self.buffer[2] << 8) | self.buffer[3]) + 4
        else:
            return False
        return len(self.buffer) >= total

    def _consume_message(self) -> bytes:
        if self.buffer[1] < 128:
            total = self.buffer[1] + 2
        elif self.buffer[1] == 0x81:
            total = self.buffer[2] + 3
        else:
            total = ((self.buffer[2] << 8) | self.buffer[3]) + 4
        msg = self.buffer[:total]
        self.buffer = self.buffer[total:]
        return msg

    def _process_next_message(self):
        msg = self._consume_message()
        try:
            # Extract message ID (bytes 2-4 typically)
            msg_id = msg[3] if len(msg) > 3 else 1
            # Find operation tag
            op_offset = 4 if msg[1] < 128 else (5 if msg[1] == 0x81 else 6)
            if op_offset >= len(msg):
                return
            op_tag = msg[op_offset]

            if op_tag == 0x60:    # BindRequest
                self._handle_bind(msg, msg_id)
            elif op_tag == 0x63:  # SearchRequest
                self._handle_search(msg, msg_id)
            elif op_tag == 0x66:  # ModifyRequest
                self._handle_modify(msg, msg_id)
            elif op_tag == 0x68:  # AddRequest
                self._handle_add(msg, msg_id)
            elif op_tag == 0x42:  # UnbindRequest
                self.transport.close()
            # Ignore other ops silently
        except Exception as e:
            logger.debug(f"[LDAP] Message parse error: {e}")

    def _handle_bind(self, msg: bytes, msg_id: int):
        raw = _extract_query_str(msg)
        # Try to pull DN and password from raw bytes
        try:
            dn_start = msg.index(b"\x04", 6)
            dn_len = msg[dn_start + 1]
            dn = msg[dn_start + 2: dn_start + 2 + dn_len].decode("utf-8", errors="replace")
        except (ValueError, IndexError):
            dn = "anonymous"

        self.bind_dn = dn
        is_anonymous = not dn or dn == "anonymous"

        self.db.log_credential(self.session_id, dn or "anonymous", "<ldap-bind>", service="ldap")
        self.hplogger.log_event("ldap_bind", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "bind_dn": dn,
            "anonymous": is_anonymous,
        })

        if is_anonymous:
            self.db.flag_high_interest(self.session_id, "LDAP anonymous bind — enumeration likely")

        # Accept all binds — real AD also accepts anonymous for base queries
        self.bound = True
        self.db.update_session_auth(self.session_id, dn or "anonymous", "<ldap>", success=True)
        self.transport.write(make_ldap_bind_response(result_code=0, msg_id=msg_id))

    def _handle_search(self, msg: bytes, msg_id: int):
        self.query_count += 1
        raw = _extract_query_str(msg)
        self.db.log_command(self.session_id, f"[LDAP SEARCH] {raw[:200]}")

        self.hplogger.log_event("ldap_search", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "query_raw": raw[:300],
            "query_number": self.query_count,
        })

        # Detect attack patterns
        if _detect_bloodhound(raw):
            self.db.flag_high_interest(
                self.session_id,
                "BloodHound/SharpHound collection pattern detected — T1087.002 Domain Account Discovery"
            )
            self._send_bloodhound_response(msg_id)
            return

        if _detect_kerberoast(raw):
            self.db.flag_high_interest(
                self.session_id,
                "Kerberoasting enumeration — SPN query T1558.003"
            )
            self._send_kerberoastable_users(msg_id)
            return

        if _detect_asrep(raw):
            self.db.flag_high_interest(
                self.session_id,
                "AS-REP Roasting enumeration — T1558.004 accounts without pre-auth"
            )
            self._send_asrep_users(msg_id)
            return

        if "ms-mcs-admpwd" in raw.lower():
            self.db.flag_high_interest(
                self.session_id,
                "LAPS password read attempt — T1552.001 Credentials in Files"
            )

        if "admincount=1" in raw.lower():
            self.db.flag_high_interest(
                self.session_id,
                "AdminSDHolder/privileged account enumeration"
            )

        if "dcsync" in raw.lower() or "replication" in raw.lower():
            self.db.flag_high_interest(
                self.session_id,
                "DCSync enumeration pattern — T1003.006"
            )

        # Default: send all users
        self._send_all_users(msg_id)

    def _send_all_users(self, msg_id: int):
        for user in FAKE_USERS:
            dn = f"CN={user['sAMAccountName']},OU=Users,DC=meridianhr,DC=local"
            attrs = {
                "cn": [user["cn"]],
                "sAMAccountName": [user["sAMAccountName"]],
                "mail": [user.get("mail", "")],
                "title": [user.get("title", "")],
                "department": [user.get("department", "")],
                "userAccountControl": [user.get("userAccountControl", "512")],
                "memberOf": user.get("memberOf", []),
                "lastLogon": [user.get("lastLogon", "0")],
                "objectClass": ["top", "person", "organizationalPerson", "user"],
                "distinguishedName": [dn],
            }
            if user.get("servicePrincipalName"):
                attrs["servicePrincipalName"] = user["servicePrincipalName"]
            self.transport.write(make_ldap_search_result_entry(dn, attrs, msg_id))
        self.transport.write(make_ldap_search_result_done(msg_id))

    def _send_kerberoastable_users(self, msg_id: int):
        """Return only users with SPNs set."""
        kerberoastable = [u for u in FAKE_USERS if u.get("servicePrincipalName")]
        for user in kerberoastable:
            dn = f"CN={user['sAMAccountName']},OU=Users,DC=meridianhr,DC=local"
            attrs = {
                "cn": [user["cn"]],
                "sAMAccountName": [user["sAMAccountName"]],
                "servicePrincipalName": user["servicePrincipalName"],
                "userAccountControl": [user.get("userAccountControl", "512")],
                "memberOf": user.get("memberOf", []),
                "objectClass": ["top", "person", "organizationalPerson", "user"],
                "distinguishedName": [dn],
            }
            self.transport.write(make_ldap_search_result_entry(dn, attrs, msg_id))
        self.transport.write(make_ldap_search_result_done(msg_id))

    def _send_asrep_users(self, msg_id: int):
        """Return only accounts with DONT_REQUIRE_PREAUTH set."""
        asrep_users = [u for u in FAKE_USERS if u.get("userAccountControl") == "4194816"]
        for user in asrep_users:
            dn = f"CN={user['sAMAccountName']},OU=Users,DC=meridianhr,DC=local"
            attrs = {
                "cn": [user["cn"]],
                "sAMAccountName": [user["sAMAccountName"]],
                "userAccountControl": ["4194816"],
                "objectClass": ["top", "person", "organizationalPerson", "user"],
                "distinguishedName": [dn],
            }
            self.transport.write(make_ldap_search_result_entry(dn, attrs, msg_id))
        self.transport.write(make_ldap_search_result_done(msg_id))

    def _send_bloodhound_response(self, msg_id: int):
        """Return full domain object set to feed BloodHound collection."""
        # Users
        for user in FAKE_USERS:
            dn = f"CN={user['sAMAccountName']},OU=Users,DC=meridianhr,DC=local"
            attrs = {
                "cn": [user["cn"]],
                "sAMAccountName": [user["sAMAccountName"]],
                "userAccountControl": [user.get("userAccountControl", "512")],
                "memberOf": user.get("memberOf", []),
                "objectClass": ["top", "person", "organizationalPerson", "user"],
                "distinguishedName": [dn],
                "lastLogon": [user.get("lastLogon", "0")],
                "adminCount": ["1"] if "Domain Admins" in " ".join(user.get("memberOf", [])) else ["0"],
            }
            if user.get("servicePrincipalName"):
                attrs["servicePrincipalName"] = user["servicePrincipalName"]
            self.transport.write(make_ldap_search_result_entry(dn, attrs, msg_id))

        # Groups
        for group in FAKE_GROUPS:
            dn = f"CN={group['cn']},CN=Users,DC=meridianhr,DC=local"
            attrs = {
                "cn": [group["cn"]],
                "description": [group["description"]],
                "member": group["member"],
                "objectClass": ["top", "group"],
                "distinguishedName": [dn],
                "groupType": ["-2147483646"],
            }
            self.transport.write(make_ldap_search_result_entry(dn, attrs, msg_id))

        # Domain root object
        root_dn = "DC=meridianhr,DC=local"
        root_attrs = {
            "dc": ["meridianhr"],
            "objectClass": ["top", "domain", "domainDNS"],
            "distinguishedName": [root_dn],
            "name": [DOMAIN_FQDN],
            "dNSHostName": [DC_FQDN],
            "functionalLevel": ["7"],  # Windows Server 2016
        }
        self.transport.write(make_ldap_search_result_entry(root_dn, root_attrs, msg_id))
        self.transport.write(make_ldap_search_result_done(msg_id))

    def _handle_modify(self, msg: bytes, msg_id: int):
        raw = _extract_query_str(msg)
        self.db.flag_high_interest(self.session_id, f"LDAP ModifyRequest — T1098 Account Manipulation: {raw[:100]}")
        self.db.log_command(self.session_id, f"[LDAP MODIFY] {raw[:200]}")
        # Return success (let them think it worked)
        resp_content = bytes([0x0a, 0x01, 0x00, 0x04, 0x00, 0x04, 0x00])
        resp = bytes([0x67]) + encode_length(len(resp_content)) + resp_content
        msg_id_enc = bytes([0x02, 0x01, msg_id & 0xFF])
        envelope = msg_id_enc + resp
        self.transport.write(bytes([0x30]) + encode_length(len(envelope)) + envelope)

    def _handle_add(self, msg: bytes, msg_id: int):
        raw = _extract_query_str(msg)
        self.db.flag_high_interest(
            self.session_id,
            f"LDAP AddRequest — T1136.001 Create Account attempt: {raw[:100]}"
        )
        self.db.log_command(self.session_id, f"[LDAP ADD] {raw[:200]}")
        # Return insufficientAccessRights (50)
        resp_content = bytes([0x0a, 0x01, 0x32, 0x04, 0x00, 0x04, 0x00])
        resp = bytes([0x69]) + encode_length(len(resp_content)) + resp_content
        msg_id_enc = bytes([0x02, 0x01, msg_id & 0xFF])
        envelope = msg_id_enc + resp
        self.transport.write(bytes([0x30]) + encode_length(len(envelope)) + envelope)

    def connection_lost(self, exc):
        if self.session_id:
            duration = int(time.time() - self.connect_time)
            self.db.close_session(self.session_id, duration)


# ─── Kerberos (port 88) ───────────────────────────────────────────────────────

class KerberosHoneypotProtocol(asyncio.Protocol):
    """
    Minimal Kerberos AS-REQ / TGS-REQ handler.
    Logs every request, detects roasting attempts, returns plausible errors.
    Does NOT issue real tickets — just observation.
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
        self.session_id = self.db.create_session(self.peer_ip, service="kerberos")
        logger.info(f"[Kerberos] Connection from {self.peer_ip}")
        asyncio.ensure_future(enrich_ip(self.peer_ip))

    def data_received(self, data: bytes):
        self.buffer += data
        if len(self.buffer) >= 4:
            self._handle_krb_message(self.buffer)
            self.buffer = b""

    def _handle_krb_message(self, data: bytes):
        raw_hex = data[:32].hex()
        raw_str = data.decode("utf-8", errors="replace")

        # Detect message type from ASN.1 APPLICATION tag
        # AS-REQ = [APPLICATION 10] = 0x6a
        # TGS-REQ = [APPLICATION 12] = 0x6c
        msg_type = "unknown"
        if len(data) > 0:
            tag = data[0] if data[0] != 0x00 else (data[4] if len(data) > 4 else 0)
            if 0x6a in data[:8]:
                msg_type = "AS-REQ"
            elif 0x6c in data[:8]:
                msg_type = "TGS-REQ"

        # Try to extract username from KRB5 ASN.1 (best effort)
        username = self._extract_krb_username(data)

        self.db.log_command(self.session_id, f"[Kerberos] {msg_type} from {self.peer_ip} user={username}")
        self.hplogger.log_event("kerberos_request", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "message_type": msg_type,
            "username": username,
            "raw_hex": raw_hex,
        })

        if msg_type == "AS-REQ":
            # Could be AS-REP roasting (no pre-auth) or normal auth
            if username in ["svc_adconnect"]:  # our no-preauth account
                self.db.flag_high_interest(
                    self.session_id,
                    f"AS-REP Roasting attempt against {username} — T1558.004"
                )
            else:
                self.db.flag_high_interest(
                    self.session_id,
                    f"Kerberos AS-REQ for {username} — T1558 Kerberos ticket request"
                )
            # Return KRB_ERROR: PREAUTH_REQUIRED (25) — forces client to send hash
            self.transport.write(self._make_krb_error(25, "PREAUTH_REQUIRED"))

        elif msg_type == "TGS-REQ":
            self.db.flag_high_interest(
                self.session_id,
                f"Kerberoasting TGS-REQ for SPN — T1558.003"
            )
            # Return KRB_ERROR: server not found (7) — realistic failure
            self.transport.write(self._make_krb_error(7, "S_PRINCIPAL_UNKNOWN"))

        else:
            self.transport.write(self._make_krb_error(6, "C_PRINCIPAL_UNKNOWN"))

    def _extract_krb_username(self, data: bytes) -> str:
        """Best-effort username extraction from KRB5 ASN.1."""
        try:
            # Look for printable ASCII sequences that look like usernames
            text = data.decode("latin-1")
            candidates = re.findall(r"[a-zA-Z][a-zA-Z0-9_\-\.]{2,30}", text)
            # Filter to plausible usernames (skip domain names and noise)
            for c in candidates:
                if c.lower() not in ("meridianhr", "local", "krbtgt", "host", "ldap", "cifs"):
                    return c
        except Exception:
            pass
        return "unknown"

    def _make_krb_error(self, error_code: int, error_text: str) -> bytes:
        """Minimal KRB_ERROR response."""
        # KRB_ERROR = [APPLICATION 30] = 0x7e
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%SZ").encode()
        realm = DOMAIN_FQDN.encode()
        sname = b"krbtgt"
        err_msg = error_text.encode()

        # Rough ASN.1 encoding — enough to trigger real clients to log an error
        content = (
            bytes([0xa0, 0x03, 0x02, 0x01, 0x05]) +    # pvno = 5
            bytes([0xa1, 0x03, 0x02, 0x01, 0x1e]) +    # msg-type = 30
            bytes([0xa4, 0x03, 0x02, 0x01, error_code & 0xFF]) +  # error-code
            bytes([0xa5, len(realm) + 2, 0x1b, len(realm)]) + realm +  # realm
            bytes([0xa6, len(err_msg) + 2, 0x1b, len(err_msg)]) + err_msg  # e-text
        )
        return bytes([0x7e]) + encode_length(len(content)) + content

    def connection_lost(self, exc):
        if self.session_id:
            duration = int(time.time() - self.connect_time)
            self.db.close_session(self.session_id, duration)


# ─── Server Starters ──────────────────────────────────────────────────────────

async def start_ldap_server(host: str, port: int, db: DB, hplogger: HoneypotLogger):
    loop = asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: LDAPHoneypotProtocol(db=db, hplogger=hplogger),
        host, port
    )
    logger.info(f"[LDAP] Honeypot listening on {host}:{port}")
    return server

async def start_ldaps_server(host: str, port: int, db: DB, hplogger: HoneypotLogger):
    """LDAPS on 636 — same protocol, TLS would be in front in a real deployment."""
    loop = asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: LDAPHoneypotProtocol(db=db, hplogger=hplogger),
        host, port
    )
    logger.info(f"[LDAPS] Honeypot listening on {host}:{port}")
    return server

async def start_gc_server(host: str, port: int, db: DB, hplogger: HoneypotLogger):
    """Global Catalog on 3268 — same LDAP protocol."""
    loop = asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: LDAPHoneypotProtocol(db=db, hplogger=hplogger),
        host, port
    )
    logger.info(f"[Global Catalog] Honeypot listening on {host}:{port}")
    return server

async def start_kerberos_server(host: str, port: int, db: DB, hplogger: HoneypotLogger):
    loop = asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: KerberosHoneypotProtocol(db=db, hplogger=hplogger),
        host, port
    )
    logger.info(f"[Kerberos] Honeypot listening on {host}:{port}")
    return server
