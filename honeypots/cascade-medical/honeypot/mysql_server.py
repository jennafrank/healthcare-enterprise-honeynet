"""
MySQL Honeypot — Meridian HR Solutions
Exposes port 3306 with weak credentials and a realistic HR schema.
Logs all queries, credential attempts, and MITRE-tagged behavior.
"""

import asyncio
import struct
import hashlib
import os
import logging
import time
from datetime import datetime
from .db import DB
from .logger import HoneypotLogger
from .enrichment import enrich_ip

logger = logging.getLogger("mysql_honeypot")

# Fake query results for common attacker queries
FAKE_DATABASES = [
    ("information_schema",),
    ("meridian_hr",),
    ("payroll_archive",),
    ("performance_schema",),
]

FAKE_TABLES = {
    "meridian_hr": [
        ("employees",),
        ("payroll",),
        ("benefits",),
        ("users",),
        ("audit_log",),
        ("ssn_records",),
        ("direct_deposit",),
    ],
    "payroll_archive": [
        ("payroll_2022",),
        ("payroll_2023",),
        ("payroll_2024",),
        ("w2_export",),
    ],
}

FAKE_EMPLOYEES = [
    (1, "John", "Smith", "j.smith@meridianhr.com", "Director of HR", "2019-03-14", 142500),
    (2, "Amanda", "Torres", "a.torres@meridianhr.com", "Payroll Manager", "2020-07-01", 98000),
    (3, "Kevin", "Park", "k.park@meridianhr.com", "Systems Admin", "2021-01-10", 112000),
    (4, "Lisa", "Chen", "l.chen@meridianhr.com", "Benefits Coordinator", "2022-04-22", 74000),
    (5, "Marcus", "Williams", "m.williams@meridianhr.com", "HRIS Analyst", "2020-11-30", 88000),
]

FAKE_USERS_TABLE = [
    (1, "admin", "5f4dcc3b5aa765d61d8327deb882cf99", "superadmin", "2024-06-01"),
    (2, "hradmin", "e10adc3949ba59abbe56e057f20f883e", "admin", "2024-05-15"),
    (3, "payroll_svc", "25d55ad283aa400af464c76d713c07ad", "service", "2024-04-01"),
    (4, "reporting", "098f6bcd4621d373cade4e832627b4f6", "readonly", "2024-03-20"),
]

FAKE_SSN = [
    (1, 1, "***-**-4821", "Chase", "****3847"),
    (2, 2, "***-**-7734", "BofA", "****9920"),
    (3, 3, "***-**-2291", "Wells Fargo", "****1104"),
]

WEAK_PASSWORDS = {
    "admin", "root", "password", "123456", "meridian", "hr2024",
    "payroll", "mysql", "test", "1234", "Password1", ""
}


def make_mysql_greeting():
    """Minimal MySQL handshake greeting packet."""
    server_version = b"8.0.36-Meridian-HR\x00"
    connection_id = struct.pack("<I", 4821)
    auth_data_1 = os.urandom(8) + b"\x00"
    capabilities_lower = struct.pack("<H", 0xF7FF)
    charset = b"\x21"
    status = struct.pack("<H", 0x0002)
    capabilities_upper = struct.pack("<H", 0x81FF)
    auth_plugin_len = struct.pack("B", 21)
    reserved = b"\x00" * 10
    auth_data_2 = os.urandom(12) + b"\x00"
    auth_plugin_name = b"mysql_native_password\x00"

    payload = (b"\x0a" + server_version + connection_id + auth_data_1 +
               capabilities_lower + charset + status + capabilities_upper +
               auth_plugin_len + reserved + auth_data_2 + auth_plugin_name)

    length = struct.pack("<I", len(payload))[:3]
    return length + b"\x00" + payload


def encode_result_set(columns, rows):
    """Encode a simple MySQL result set."""
    packets = []

    def make_packet(payload, seq):
        length = struct.pack("<I", len(payload))[:3]
        return length + struct.pack("B", seq) + payload

    # Column count
    seq = 1
    packets.append(make_packet(b"\x01" + struct.pack("B", len(columns)), seq))
    seq += 1

    # Column definitions
    for col_name in columns:
        col_name_b = col_name.encode()
        payload = (b"\x03def\x00\x00\x00" + struct.pack("B", len(col_name_b)) +
                   col_name_b + b"\x00" + struct.pack("B", len(col_name_b)) +
                   col_name_b + b"\x00\x0c\x21\x00\xff\x00\x00\x00\xfd\x00\x00\x00\x00\x00")
        packets.append(make_packet(payload, seq))
        seq += 1

    # EOF
    packets.append(make_packet(b"\xfe\x00\x00\x02\x00", seq))
    seq += 1

    # Rows
    for row in rows:
        row_payload = b""
        for val in row:
            s = str(val).encode()
            row_payload += struct.pack("B", len(s)) + s
        packets.append(make_packet(row_payload, seq))
        seq += 1

    # Final EOF
    packets.append(make_packet(b"\xfe\x00\x00\x02\x00", seq))
    return b"".join(packets)


def ok_packet(seq=1):
    return struct.pack("<I", 7)[:3] + struct.pack("B", seq) + b"\x00\x00\x00\x02\x00\x00\x00"


def err_packet(msg, seq=2):
    payload = b"\xff" + struct.pack("<H", 1045) + b"#28000" + msg.encode()
    return struct.pack("<I", len(payload))[:3] + struct.pack("B", seq) + payload


class MySQLHoneypotProtocol(asyncio.Protocol):
    def __init__(self, db: DB, hplogger: HoneypotLogger):
        self.db = db
        self.hplogger = hplogger
        self.transport = None
        self.peer_ip = None
        self.session_id = None
        self.authenticated = False
        self.current_db = "meridian_hr"
        self.state = "greeting"
        self.connect_time = time.time()
        self.query_count = 0

    def connection_made(self, transport):
        self.transport = transport
        self.peer_ip = transport.get_extra_info("peername")[0]
        self.session_id = self.db.create_session(self.peer_ip, service="mysql")
        logger.info(f"[MySQL] Connection from {self.peer_ip}")
        self.transport.write(make_mysql_greeting())

    def data_received(self, data):
        if self.state == "greeting":
            self._handle_handshake(data)
        elif self.state == "authenticated":
            self._handle_command(data)

    def _handle_handshake(self, data):
        try:
            if len(data) < 36:
                self.transport.write(err_packet("Bad handshake", seq=2))
                self.transport.close()
                return

            # Parse username from handshake response
            # MySQL handshake response: 4 caps + 4 maxpkt + 1 charset + 23 reserved + username\0
            offset = 36
            username_end = data.index(b"\x00", offset)
            username = data[offset:username_end].decode("utf-8", errors="replace")

            # Password hash follows
            pw_offset = username_end + 1
            pw_len = data[pw_offset] if pw_offset < len(data) else 0
            password_hash = data[pw_offset + 1: pw_offset + 1 + pw_len].hex() if pw_len else ""

            # Log attempt
            self.db.log_credential(self.session_id, username, f"<hash:{password_hash[:16]}>")
            self.hplogger.log_event("mysql_auth", {
                "session_id": self.session_id,
                "ip": self.peer_ip,
                "username": username,
                "password_hash": password_hash[:32],
            })

            # Accept weak/common usernames
            if username in {"root", "admin", "meridian", "hradmin", "payroll", "mysql", "test", "sa", ""}:
                self.authenticated = True
                self.state = "authenticated"
                self.db.update_session_auth(self.session_id, username, "<hash>", success=True)
                asyncio.ensure_future(enrich_ip(self.peer_ip))
                self.transport.write(ok_packet(seq=2))
                logger.info(f"[MySQL] Auth accepted: {username}@{self.peer_ip}")
            else:
                self.transport.write(err_packet(
                    f"Access denied for user '{username}'@'{self.peer_ip}' (using password: YES)"
                ))
                self.transport.close()
        except Exception as e:
            logger.error(f"[MySQL] Handshake error: {e}")
            self.transport.close()

    def _handle_command(self, data):
        if len(data) < 5:
            return
        try:
            # MySQL command packet: 3 len + 1 seq + 1 cmd + query
            cmd_type = data[4]
            payload = data[5:].decode("utf-8", errors="replace").strip()

            self.query_count += 1
            self.db.log_command(self.session_id, f"[MySQL] {payload}")
            self.hplogger.log_event("mysql_query", {
                "session_id": self.session_id,
                "ip": self.peer_ip,
                "query": payload,
                "query_number": self.query_count,
            })

            # COM_QUIT
            if cmd_type == 0x01:
                self.transport.close()
                return

            # COM_QUERY
            if cmd_type == 0x03:
                self._handle_query(payload)

            # COM_INIT_DB
            elif cmd_type == 0x02:
                self.current_db = payload
                self.transport.write(ok_packet(seq=1))

        except Exception as e:
            logger.error(f"[MySQL] Command error: {e}")

    def _handle_query(self, query: str):
        q = query.strip().lower()

        if "show databases" in q:
            self.transport.write(encode_result_set(["Database"], FAKE_DATABASES))

        elif "show tables" in q:
            db = self.current_db
            tables = FAKE_TABLES.get(db, [("(no tables)",)])
            self.transport.write(encode_result_set([f"Tables_in_{db}"], tables))

        elif "select" in q and "employees" in q:
            self.db.flag_high_interest(self.session_id, f"SELECT from employees table: {query}")
            if "salary" in q or "ssn" in q or "*" in q:
                self.db.flag_high_interest(self.session_id, "CRITICAL: employee PII/salary query")
            self.transport.write(encode_result_set(
                ["id", "first_name", "last_name", "email", "title", "hire_date", "salary"],
                FAKE_EMPLOYEES
            ))

        elif "select" in q and "users" in q:
            self.db.flag_high_interest(self.session_id, f"CRITICAL: users table query — credential harvest: {query}")
            self.transport.write(encode_result_set(
                ["id", "username", "password_hash", "role", "last_login"],
                FAKE_USERS_TABLE
            ))

        elif "select" in q and "ssn" in q:
            self.db.flag_high_interest(self.session_id, "CRITICAL: SSN table accessed")
            self.transport.write(encode_result_set(
                ["id", "employee_id", "ssn_masked", "bank", "account_masked"],
                FAKE_SSN
            ))

        elif "select" in q and "payroll" in q:
            self.db.flag_high_interest(self.session_id, f"Payroll table query: {query}")
            self.transport.write(encode_result_set(
                ["id", "employee_id", "gross_pay", "net_pay", "pay_date"],
                [(1, 3, 11875.00, 8421.33, "2024-05-31"),
                 (2, 4, 9416.67, 6708.22, "2024-05-31"),
                 (3, 5, 7333.33, 5231.44, "2024-05-31")]
            ))

        elif "select version" in q or "@@version" in q:
            self.transport.write(encode_result_set(["@@version"], [("8.0.36-Meridian-HR",)]))

        elif "select user" in q or "current_user" in q:
            self.transport.write(encode_result_set(["user()"], [("meridian_app@localhost",)]))

        elif "select database" in q:
            self.transport.write(encode_result_set(["database()"], [(self.current_db,)]))

        elif q.startswith("use "):
            self.current_db = q[4:].strip().strip(";")
            self.transport.write(ok_packet(seq=1))

        elif "create " in q or "insert " in q or "update " in q or "delete " in q or "drop " in q:
            self.db.flag_high_interest(self.session_id, f"Write/destructive query: {query}")
            self.transport.write(ok_packet(seq=1))

        elif "load data" in q or "into outfile" in q or "into dumpfile" in q:
            self.db.flag_high_interest(self.session_id, f"CRITICAL: MySQL file read/write attempt: {query}")
            self.transport.write(err_packet("Access denied for this operation"))

        elif "xp_cmdshell" in q or "exec " in q:
            self.db.flag_high_interest(self.session_id, f"CRITICAL: Command execution attempt: {query}")
            self.transport.write(err_packet("Unknown command"))

        else:
            self.transport.write(ok_packet(seq=1))

    def connection_lost(self, exc):
        if self.session_id:
            duration = int(time.time() - self.connect_time)
            self.db.close_session(self.session_id, duration)
        logger.info(f"[MySQL] Disconnected {self.peer_ip} ({self.query_count} queries)")


async def start_mysql_server(host: str, port: int, db: DB, hplogger: HoneypotLogger):
    loop = asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: MySQLHoneypotProtocol(db=db, hplogger=hplogger),
        host, port
    )
    logger.info(f"[MySQL] Listening on {host}:{port}")
    return server
