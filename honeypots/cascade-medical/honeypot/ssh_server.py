"""
Meridian HR Solutions — SSH Honeypot
Poses as an internal Ubuntu admin server for a mid-size HR/payroll company.
Logs every credential attempt, command, and session to SQLite + JSONL.
"""

import asyncio
import asyncssh
import logging
import time
import random
from datetime import datetime
from .shell import FakeShell
from .db import DB
from .logger import HoneypotLogger
from .enrichment import enrich_ip
from .mitre import tag_session

logger = logging.getLogger("ssh_honeypot")


class HoneypotSSHServer(asyncssh.SSHServer):
    def __init__(self, db: DB, hplogger: HoneypotLogger):
        self.db = db
        self.hplogger = hplogger
        self._conn = None
        self.session_id = None
        self.peer_ip = None
        self.username = None
        self.password = None
        self.connect_time = None

    def connection_made(self, conn):
        self._conn = conn
        self.peer_ip = conn.get_extra_info("peername")[0]
        self.connect_time = time.time()
        self.session_id = self.db.create_session(self.peer_ip)
        logger.info(f"[SSH] Connection from {self.peer_ip} (session {self.session_id})")

    def connection_lost(self, exc):
        if self.session_id:
            duration = int(time.time() - self.connect_time)
            self.db.close_session(self.session_id, duration)
            asyncio.create_task(self._finalize_session())

    async def _finalize_session(self):
        cmds = self.db.get_session_commands(self.session_id)
        techniques = tag_session(cmds)
        self.db.update_mitre(self.session_id, techniques)

    def begin_auth(self, username):
        self.username = username
        return True  # always require password

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        self.password = password
        # Log the attempt
        self.db.log_credential(self.session_id, username, password)
        self.hplogger.log_event("auth_attempt", {
            "session_id": self.session_id,
            "ip": self.peer_ip,
            "username": username,
            "password": password,
        })
        # Enrich IP asynchronously
        asyncio.create_task(self._enrich(self.peer_ip, self.session_id))
        # Weak credentials that get "accepted"
        weak_users = {"admin", "root", "meridian", "hradmin", "payroll", "backup", "ubuntu", "sysadmin"}
        weak_passwords = {"admin", "password", "123456", "meridian", "hr2024", "payroll", "Password1",
                          "admin123", "root", "letmein", "welcome", "changeme", "P@ssw0rd", "Hr@2024!"}
        if username in weak_users or password in weak_passwords or len(password) <= 6:
            self.db.update_session_auth(self.session_id, username, password, success=True)
            return True
        # 15% random acceptance to catch sophisticated actors using custom creds
        if random.random() < 0.15:
            self.db.update_session_auth(self.session_id, username, password, success=True)
            return True
        return False

    async def _enrich(self, ip, session_id):
        data = await enrich_ip(ip)
        self.db.update_enrichment(session_id, data)


class HoneypotSession(asyncssh.SSHServerSession):
    def __init__(self, session_id: int, peer_ip: str, username: str, db: DB, hplogger: HoneypotLogger):
        self.session_id = session_id
        self.peer_ip = peer_ip
        self.username = username
        self.db = db
        self.hplogger = hplogger
        self.shell = None
        self._chan = None

    def connection_made(self, chan):
        self._chan = chan
        self.shell = FakeShell(
            chan=chan,
            session_id=self.session_id,
            username=self.username,
            db=self.db,
            hplogger=self.hplogger,
        )
        # Realistic login delay
        time.sleep(random.uniform(0.8, 2.0))
        self._chan.write(self.shell.motd())

    def shell_requested(self):
        return True

    def exec_requested(self, command):
        return True

    def data_received(self, data, datatype):
        if self.shell:
            asyncio.get_event_loop().run_until_complete(
                self.shell.handle_input(data)
            ) if asyncio.get_event_loop().is_running() else None
            asyncio.ensure_future(self.shell.handle_input(data))

    def eof_received(self):
        if self._chan:
            self._chan.close()


async def start_ssh_server(host: str, port: int, host_key: str, db: DB, hplogger: HoneypotLogger):
    def server_factory():
        return HoneypotSSHServer(db=db, hplogger=hplogger)

    def session_factory(session_server):
        return HoneypotSession(
            session_id=session_server.session_id,
            peer_ip=session_server.peer_ip,
            username=session_server.username or "unknown",
            db=db,
            hplogger=hplogger,
        )

    await asyncssh.create_server(
        server_factory,
        host,
        port,
        server_host_keys=[host_key],
        process_factory=None,
        session_factory=lambda conn: session_factory(conn._server),
        line_editor=False,
    )
    logger.info(f"[SSH] Listening on {host}:{port}")
