"""
Redis + MongoDB Honeypots — Meridian HR Solutions
Redis on 6379: session cache, JWT tokens, job queue — real attacker bait
MongoDB on 27017: document store with fake HR documents, W-2s, contracts
"""

import asyncio
import json
import time
import logging
import struct
import bson  # pymongo provides this
from datetime import datetime, timedelta
from .db import DB
from .logger import HoneypotLogger
from .enrichment import enrich_ip

logger = logging.getLogger("nosql_honeypot")

# ─── REDIS ────────────────────────────────────────────────────────────────────

REDIS_KEYS = {
    "session:user:8821": '{"user_id":8821,"email":"j.smith@meridianhr.com","role":"admin","exp":1717200000}',
    "session:user:8819": '{"user_id":8819,"email":"a.torres@meridianhr.com","role":"payroll","exp":1717196400}',
    "session:token:payroll_api": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoicGF5cm9sbF9zdmMiLCJyb2xlIjoic2VydmljZSJ9.FAKE",
    "cache:hr_report_2024q1": '{"generated":"2024-04-01","records":847,"status":"complete"}',
    "auth:jwt_secret": "M3r1d1@n_JWT_S3cr3t_2024!",
    "queue:payroll:pending": '["job_48821","job_48822","job_48823"]',
    "config:db_password": "M3r1d1@n_Prod_2024!",
    "config:smtp_password": "SMTP_M3r1d14n@2024",
    "rate:api:192.168.1.1": "12",
}


class RedisHoneypotProtocol(asyncio.Protocol):
    def __init__(self, db: DB, hplogger: HoneypotLogger):
        self.db = db
        self.hplogger = hplogger
        self.transport = None
        self.peer_ip = None
        self.session_id = None
        self.connect_time = time.time()
        self.buffer = b""
        self.authenticated = False
        self.command_count = 0
        self.require_auth = True

    def connection_made(self, transport):
        self.transport = transport
        self.peer_ip = transport.get_extra_info("peername")[0]
        self.session_id = self.db.create_session(self.peer_ip, service="redis")
        logger.info(f"[Redis] Connection from {self.peer_ip}")
        asyncio.ensure_future(enrich_ip(self.peer_ip))

    def data_received(self, data):
        self.buffer += data
        while b"\r\n" in self.buffer:
            self._process_buffer()

    def _process_buffer(self):
        try:
            lines = self.buffer.split(b"\r\n")
            self.buffer = b""

            # Parse RESP protocol
            if lines[0].startswith(b"*"):
                count = int(lines[0][1:])
                args = []
                i = 1
                while i < len(lines) and len(args) < count:
                    if lines[i].startswith(b"$"):
                        i += 1
                        if i < len(lines):
                            args.append(lines[i].decode("utf-8", errors="replace"))
                            i += 1
                    else:
                        i += 1
                if args:
                    self._handle_command(args)
            else:
                # Inline command
                cmd_line = lines[0].decode("utf-8", errors="replace").strip()
                if cmd_line:
                    self._handle_command(cmd_line.split())
        except Exception as e:
            logger.error(f"[Redis] Parse error: {e}")

    def _handle_command(self, args):
        if not args:
            return
        cmd = args[0].upper()
        params = args[1:]
        self.command_count += 1

        raw = " ".join(args)
        self.db.log_command(self.session_id, f"[Redis] {raw}")
        self.hplogger.log_event("redis_command", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "command": raw,
        })

        # Authentication check
        if cmd == "AUTH":
            password = params[0] if params else ""
            if password in {"R3d1s_Sess10n_Key!", "admin", "password", "redis", "123456", "test", ""}:
                self.authenticated = True
                self.db.update_session_auth(self.session_id, "redis", password, success=True)
                self._write("+OK\r\n")
            else:
                self._write("-ERR invalid password\r\n")
            return

        if cmd == "PING":
            self._write("+PONG\r\n")
            return

        if cmd == "QUIT":
            self._write("+OK\r\n")
            self.transport.close()
            return

        if cmd == "INFO":
            info = (
                "# Server\r\nredis_version:7.0.11\r\nredis_mode:standalone\r\n"
                "os:Linux 5.15.0-112-generic x86_64\r\nos_type:Linux\r\n"
                "# Keyspace\r\ndb0:keys=9,expires=3,avg_ttl=3600000\r\n"
            )
            self._write(f"${len(info)}\r\n{info}\r\n")
            return

        if cmd == "KEYS":
            pattern = params[0] if params else "*"
            self.db.flag_high_interest(self.session_id, f"Redis KEYS {pattern} — enumeration")
            keys = list(REDIS_KEYS.keys())
            resp = f"*{len(keys)}\r\n" + "".join(f"${len(k)}\r\n{k}\r\n" for k in keys)
            self._write(resp)
            return

        if cmd == "GET":
            key = params[0] if params else ""
            if "secret" in key or "password" in key or "jwt" in key:
                self.db.flag_high_interest(self.session_id, f"Redis GET sensitive key: {key}")
            val = REDIS_KEYS.get(key)
            if val:
                self._write(f"${len(val)}\r\n{val}\r\n")
            else:
                self._write("$-1\r\n")
            return

        if cmd in ("SET", "SETEX", "MSET"):
            self.db.flag_high_interest(self.session_id, f"Redis {cmd} — write attempt: {' '.join(params)}")
            self._write("+OK\r\n")
            return

        if cmd == "CONFIG":
            if params and params[0].upper() == "SET":
                self.db.flag_high_interest(self.session_id, f"Redis CONFIG SET — config rewrite attempt: {' '.join(params)}")
            self._write("-ERR CONFIG not allowed\r\n")
            return

        if cmd == "SLAVEOF" or cmd == "REPLICAOF":
            self.db.flag_high_interest(self.session_id, f"CRITICAL: Redis {cmd} — RCE via config rewrite: {' '.join(params)}")
            self._write("-ERR operation not permitted\r\n")
            return

        if cmd == "DEBUG":
            self.db.flag_high_interest(self.session_id, f"Redis DEBUG command: {' '.join(params)}")
            self._write("-ERR DEBUG disabled\r\n")
            return

        if cmd == "FLUSHALL" or cmd == "FLUSHDB":
            self.db.flag_high_interest(self.session_id, f"CRITICAL: Redis {cmd} — destructive command")
            self._write("+OK\r\n")
            return

        if cmd == "DBSIZE":
            self._write(f":9\r\n")
            return

        if cmd == "TTL":
            self._write(":-1\r\n")
            return

        if cmd == "TYPE":
            self._write("+string\r\n")
            return

        # Default: OK
        self._write("+OK\r\n")

    def _write(self, data: str):
        self.transport.write(data.encode())

    def connection_lost(self, exc):
        if self.session_id:
            duration = int(time.time() - self.connect_time)
            self.db.close_session(self.session_id, duration)


async def start_redis_server(host: str, port: int, db: DB, hplogger: HoneypotLogger):
    loop = asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: RedisHoneypotProtocol(db=db, hplogger=hplogger),
        host, port
    )
    logger.info(f"[Redis] Listening on {host}:{port}")
    return server


# ─── MONGODB ──────────────────────────────────────────────────────────────────

FAKE_MONGO_DOCS = {
    "employees": [
        {"_id": "emp001", "name": "John Smith", "email": "j.smith@meridianhr.com",
         "ssn": "***-**-4821", "salary": 142500, "department": "HR", "manager": "CEO"},
        {"_id": "emp002", "name": "Amanda Torres", "email": "a.torres@meridianhr.com",
         "ssn": "***-**-7734", "salary": 98000, "department": "Payroll", "manager": "John Smith"},
        {"_id": "emp003", "name": "Kevin Park", "email": "k.park@meridianhr.com",
         "ssn": "***-**-2291", "salary": 112000, "department": "IT", "manager": "John Smith"},
    ],
    "contracts": [
        {"_id": "ctr001", "employee": "emp001", "type": "employment", "start": "2019-03-14",
         "salary": 142500, "status": "active", "signed": True},
        {"_id": "ctr002", "employee": "emp002", "type": "employment", "start": "2020-07-01",
         "salary": 98000, "status": "active", "signed": True},
    ],
    "w2_documents": [
        {"_id": "w2_2023_001", "employee": "emp001", "year": 2023, "wages": 142500,
         "federal_tax": 32175, "state_tax": 7125, "ssn_last4": "4821"},
        {"_id": "w2_2023_002", "employee": "emp002", "year": 2023, "wages": 98000,
         "federal_tax": 22050, "state_tax": 4900, "ssn_last4": "7734"},
    ],
    "api_keys": [
        {"_id": "key001", "service": "adp_integration", "key": "ADP_LIVE_abcdef123456FAKE",
         "created": "2024-01-01", "permissions": ["read_payroll", "write_employees"]},
        {"_id": "key002", "service": "benefits_portal", "key": "BEN_LIVE_xyz789FAKE",
         "created": "2024-02-15", "permissions": ["read_benefits", "update_enrollment"]},
    ],
}


def _encode_bson_doc(doc: dict) -> bytes:
    """Minimal BSON encoding — enough to look real."""
    try:
        import bson as bson_lib
        return bson_lib.encode(doc)
    except ImportError:
        # Fallback: raw bytes approximation
        j = json.dumps(doc).encode()
        size = len(j) + 5
        return struct.pack("<i", size) + j + b"\x00"


def _make_mongo_reply(request_id: int, docs: list) -> bytes:
    """MongoDB wire protocol OP_REPLY."""
    OP_REPLY = 1
    flags = 0
    cursor_id = 0
    starting_from = 0
    number_returned = len(docs)

    docs_bytes = b"".join(_encode_bson_doc(d) for d in docs)

    header_len = 16
    msg_len = header_len + 20 + len(docs_bytes)

    header = struct.pack("<iiii", msg_len, 0, request_id, OP_REPLY)
    body = struct.pack("<iqqii", flags, cursor_id, starting_from, number_returned, 0)

    return header + body[:-4] + struct.pack("<i", number_returned) + docs_bytes


class MongoHoneypotProtocol(asyncio.Protocol):
    def __init__(self, db: DB, hplogger: HoneypotLogger):
        self.db = db
        self.hplogger = hplogger
        self.transport = None
        self.peer_ip = None
        self.session_id = None
        self.connect_time = time.time()
        self.buffer = b""
        self.command_count = 0

    def connection_made(self, transport):
        self.transport = transport
        self.peer_ip = transport.get_extra_info("peername")[0]
        self.session_id = self.db.create_session(self.peer_ip, service="mongodb")
        logger.info(f"[MongoDB] Connection from {self.peer_ip}")
        asyncio.ensure_future(enrich_ip(self.peer_ip))

    def data_received(self, data):
        self.buffer += data
        while len(self.buffer) >= 16:
            msg_len = struct.unpack("<i", self.buffer[:4])[0]
            if len(self.buffer) < msg_len:
                break
            msg = self.buffer[:msg_len]
            self.buffer = self.buffer[msg_len:]
            self._handle_message(msg)

    def _handle_message(self, msg: bytes):
        try:
            if len(msg) < 16:
                return
            msg_len, req_id, resp_to, opcode = struct.unpack("<iiii", msg[:16])
            payload = msg[16:]

            # OP_QUERY (2004) or OP_MSG (2013)
            if opcode == 2004:
                self._handle_op_query(payload, req_id)
            elif opcode == 2013:
                self._handle_op_msg(payload, req_id)
        except Exception as e:
            logger.error(f"[MongoDB] Message error: {e}")

    def _handle_op_query(self, payload: bytes, req_id: int):
        try:
            flags = struct.unpack("<i", payload[:4])[0]
            ns_end = payload.index(b"\x00", 4)
            namespace = payload[4:ns_end].decode("utf-8", errors="replace")
            collection = namespace.split(".")[-1] if "." in namespace else namespace

            skip = struct.unpack("<i", payload[ns_end + 1:ns_end + 5])[0]
            limit = struct.unpack("<i", payload[ns_end + 5:ns_end + 9])[0]

            self.command_count += 1
            self.db.log_command(self.session_id, f"[MongoDB] query {namespace}")
            self.hplogger.log_event("mongo_query", {
                "session_id": self.session_id,
                "ip": self.peer_ip,
                "namespace": namespace,
            })

            docs = self._get_docs_for_collection(collection)
            reply = self._build_simple_reply(req_id, docs)
            self.transport.write(reply)

        except Exception as e:
            logger.error(f"[MongoDB] OP_QUERY error: {e}")

    def _handle_op_msg(self, payload: bytes, req_id: int):
        try:
            flags = struct.unpack("<I", payload[:4])[0]
            # Section type 0 = body
            sec_type = payload[4]
            if sec_type == 0:
                body_bytes = payload[5:]
                # Try to parse command name
                try:
                    import bson as bson_lib
                    doc = bson_lib.decode(body_bytes)
                    cmd = list(doc.keys())[0] if doc else "unknown"
                    coll = doc.get(cmd, "")
                    db_name = doc.get("$db", "meridian_docs")
                except Exception:
                    cmd = "unknown"
                    coll = ""
                    db_name = "meridian_docs"

                self.command_count += 1
                raw_cmd = f"[MongoDB] {cmd} {coll}"
                self.db.log_command(self.session_id, raw_cmd)
                self.hplogger.log_event("mongo_command", {
                    "session_id": self.session_id,
                    "ip": self.peer_ip,
                    "command": cmd,
                    "collection": str(coll),
                    "database": db_name,
                })

                if cmd in ("find", "aggregate"):
                    if str(coll) in ("api_keys", "w2_documents", "employees"):
                        self.db.flag_high_interest(self.session_id, f"MongoDB {cmd} on sensitive collection: {coll}")
                    docs = self._get_docs_for_collection(str(coll))
                    self.transport.write(self._build_msg_reply(req_id, docs, db_name))
                elif cmd in ("drop", "dropDatabase", "delete", "deleteMany"):
                    self.db.flag_high_interest(self.session_id, f"MongoDB destructive: {cmd} {coll}")
                    self.transport.write(self._build_ok_reply(req_id))
                elif cmd == "listCollections":
                    colls = [{"name": k, "type": "collection"} for k in FAKE_MONGO_DOCS.keys()]
                    self.transport.write(self._build_msg_reply(req_id, colls, db_name))
                elif cmd == "isMaster" or cmd == "ismaster" or cmd == "hello":
                    self.transport.write(self._build_hello_reply(req_id))
                elif cmd == "createUser" or cmd == "grantRolesToUser":
                    self.db.flag_high_interest(self.session_id, f"MongoDB user creation: {cmd}")
                    self.transport.write(self._build_ok_reply(req_id))
                else:
                    self.transport.write(self._build_ok_reply(req_id))
        except Exception as e:
            logger.error(f"[MongoDB] OP_MSG error: {e}")

    def _get_docs_for_collection(self, collection: str) -> list:
        return FAKE_MONGO_DOCS.get(collection, [{"info": "no documents found"}])

    def _build_simple_reply(self, req_id: int, docs: list) -> bytes:
        """Minimal OP_REPLY."""
        OP_REPLY = 1
        try:
            import bson as b
            docs_bytes = b"".join(b.encode(d) for d in docs)
        except ImportError:
            docs_bytes = json.dumps(docs).encode()

        body = struct.pack("<i", 0)   # flags
        body += struct.pack("<q", 0)  # cursor_id
        body += struct.pack("<i", 0)  # starting_from
        body += struct.pack("<i", len(docs))  # number_returned
        body += docs_bytes

        msg_len = 16 + len(body)
        header = struct.pack("<iiii", msg_len, req_id + 1, req_id, OP_REPLY)
        return header + body

    def _build_ok_reply(self, req_id: int) -> bytes:
        try:
            import bson as b
            doc = b.encode({"ok": 1})
        except ImportError:
            doc = b'{"ok": 1}'
        return self._wrap_op_msg(req_id, doc)

    def _build_hello_reply(self, req_id: int) -> bytes:
        try:
            import bson as b
            doc = b.encode({
                "ismaster": True,
                "maxBsonObjectSize": 16777216,
                "maxMessageSizeBytes": 48000000,
                "maxWriteBatchSize": 100000,
                "localTime": datetime.utcnow(),
                "connectionId": 48821,
                "minWireVersion": 0,
                "maxWireVersion": 17,
                "ok": 1,
            })
        except ImportError:
            doc = b'{"ismaster": true, "ok": 1}'
        return self._wrap_op_msg(req_id, doc)

    def _build_msg_reply(self, req_id: int, docs: list, db_name: str) -> bytes:
        try:
            import bson as b
            cursor_doc = b.encode({
                "cursor": {
                    "firstBatch": docs,
                    "id": 0,
                    "ns": f"{db_name}.results"
                },
                "ok": 1
            })
        except ImportError:
            cursor_doc = json.dumps({"cursor": {"firstBatch": docs, "id": 0}, "ok": 1}).encode()
        return self._wrap_op_msg(req_id, cursor_doc)

    def _wrap_op_msg(self, req_id: int, body_doc: bytes) -> bytes:
        OP_MSG = 2013
        flags = struct.pack("<I", 0)
        section = b"\x00" + body_doc
        payload = flags + section
        msg_len = 16 + len(payload)
        header = struct.pack("<iiii", msg_len, req_id + 1, req_id, OP_MSG)
        return header + payload

    def connection_lost(self, exc):
        if self.session_id:
            duration = int(time.time() - self.connect_time)
            self.db.close_session(self.session_id, duration)


async def start_mongodb_server(host: str, port: int, db: DB, hplogger: HoneypotLogger):
    loop = asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: MongoHoneypotProtocol(db=db, hplogger=hplogger),
        host, port
    )
    logger.info(f"[MongoDB] Listening on {host}:{port}")
    return server
