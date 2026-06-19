"""
MySQL General Query Log Parser
Tails /var/log/mysql/general.log and writes structured events
into the honeypot SQLite DB and JSONL alongside protocol-level capture.

Use this when running a REAL MySQL instance.
Run as: python3 -m honeypot.mysql_log_parser
"""

import re
import time
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from honeypot.db import DB
from honeypot.logger import HoneypotLogger
from honeypot.mitre import tag_session

logger = logging.getLogger("mysql_log_parser")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [mysql_log] %(message)s")

GENERAL_LOG = Path("/var/log/mysql/general.log")

# ─── MITRE-relevant query patterns ───────────────────────────────────────────
HIGH_INTEREST_PATTERNS = [
    (re.compile(r"SELECT.+FROM.+users", re.I),          "Credential table query",          "T1003"),
    (re.compile(r"SELECT.+FROM.+ssn",   re.I),          "SSN/PII table query",             "T1530"),
    (re.compile(r"SELECT.+FROM.+payroll", re.I),        "Payroll table query",             "T1530"),
    (re.compile(r"SELECT.+password",     re.I),         "Password field query",            "T1003"),
    (re.compile(r"LOAD\s+DATA",          re.I),         "MySQL file read attempt",         "T1005"),
    (re.compile(r"INTO\s+OUTFILE",       re.I),         "MySQL file write attempt",        "T1005"),
    (re.compile(r"INTO\s+DUMPFILE",      re.I),         "MySQL dumpfile write",            "T1005"),
    (re.compile(r"xp_cmdshell",          re.I),         "Command execution attempt",       "T1059"),
    (re.compile(r"SHOW\s+DATABASES",     re.I),         "Database enumeration",            "T1083"),
    (re.compile(r"SHOW\s+TABLES",        re.I),         "Table enumeration",               "T1083"),
    (re.compile(r"information_schema",   re.I),         "Schema enumeration",              "T1083"),
    (re.compile(r"SELECT.+\*\s+FROM",    re.I),         "Wildcard SELECT — bulk data pull","T1530"),
    (re.compile(r"DROP\s+(TABLE|DATABASE)", re.I),      "Destructive query",               "T1485"),
    (re.compile(r"CREATE\s+USER",        re.I),         "Account creation attempt",        "T1136"),
    (re.compile(r"GRANT\s+ALL",          re.I),         "Privilege escalation",            "T1548"),
    (re.compile(r"mysqldump",            re.I),         "mysqldump exfil attempt",         "T1005"),
]

# General log line format:
# 2024-06-03T08:22:14.847291Z    48 Connect   meridian_app@localhost on meridian_hr using TCP/IP
# 2024-06-03T08:22:14.848123Z    48 Query     SELECT * FROM employees
GENERAL_LOG_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)\s+(\d+)\s+(\w+)\s+(.*)"
)

# Connect line extracts IP:
# Connect   user@ip on db using TCP/IP
CONNECT_RE = re.compile(r"(\S+)@(\S+) on (\S*)")


class MySQLLogParser:
    def __init__(self, db: DB, hplogger: HoneypotLogger,
                 log_path: Path = GENERAL_LOG):
        self.db = db
        self.hplogger = hplogger
        self.log_path = log_path
        # thread_id → session_id mapping
        self._sessions: dict = {}
        # thread_id → list of queries
        self._query_history: dict = {}

    def tail(self):
        """Tail the general query log indefinitely."""
        logger.info(f"Tailing {self.log_path}")
        with open(self.log_path, "r", errors="replace") as f:
            # Seek to end on startup (don't replay old logs)
            f.seek(0, 2)
            while True:
                line = f.readline()
                if line:
                    self._process_line(line.rstrip())
                else:
                    time.sleep(0.1)

    def _process_line(self, line: str):
        m = GENERAL_LOG_RE.match(line)
        if not m:
            return

        timestamp_str, thread_id_str, event_type, detail = m.groups()
        thread_id = int(thread_id_str)

        if event_type == "Connect":
            self._handle_connect(thread_id, timestamp_str, detail)

        elif event_type == "Query":
            self._handle_query(thread_id, timestamp_str, detail)

        elif event_type == "Quit":
            self._handle_quit(thread_id)

        elif event_type == "Init_DB":
            sid = self._sessions.get(thread_id)
            if sid:
                self.db.log_command(sid, f"[MySQL] USE {detail}")

    def _handle_connect(self, thread_id: int, timestamp_str: str, detail: str):
        cm = CONNECT_RE.match(detail)
        if not cm:
            return

        username, host, database = cm.groups()
        # host is "ip" or "localhost" or "ip:port"
        ip = host.split(":")[0] if ":" in host else host
        if ip in ("localhost", "127.0.0.1", "::1"):
            return  # Ignore local application connections

        sid = self.db.create_session(ip, service="mysql_real")
        self._sessions[thread_id] = sid
        self._query_history[thread_id] = []

        self.db.update_session_auth(sid, username, "<real-mysql-connect>", success=True)
        self.db.log_command(sid, f"[MySQL] CONNECT user={username} db={database}")

        self.hplogger.log_event("mysql_real_connect", {
            "session_id": sid,
            "ip": ip,
            "username": username,
            "database": database,
            "thread_id": thread_id,
            "timestamp": timestamp_str,
        })

        logger.info(f"[MySQL-real] New connection: {username}@{ip} → {database} (tid={thread_id})")

    def _handle_query(self, thread_id: int, timestamp_str: str, query: str):
        sid = self._sessions.get(thread_id)
        if not sid:
            return

        self.db.log_command(sid, f"[MySQL] {query}")
        self._query_history.setdefault(thread_id, []).append(query)

        self.hplogger.log_event("mysql_real_query", {
            "session_id": sid,
            "query": query,
            "timestamp": timestamp_str,
            "thread_id": thread_id,
        })

        # Check high-interest patterns
        for pattern, reason, technique_id in HIGH_INTEREST_PATTERNS:
            if pattern.search(query):
                self.db.flag_high_interest(sid, f"{reason} [{technique_id}]: {query[:120]}")
                self.hplogger.log_event("mysql_real_high_interest", {
                    "session_id": sid,
                    "query": query,
                    "reason": reason,
                    "technique_id": technique_id,
                })
                logger.warning(f"[MySQL-real] HIGH INTEREST [{technique_id}] {reason}: {query[:80]}")
                break

    def _handle_quit(self, thread_id: int):
        sid = self._sessions.pop(thread_id, None)
        queries = self._query_history.pop(thread_id, [])
        if sid and queries:
            techniques = tag_session(queries)
            self.db.update_mitre(sid, techniques)
            logger.info(f"[MySQL-real] Session {sid} closed. {len(queries)} queries, {len(techniques)} MITRE techniques.")


def main():
    db = DB()
    hplogger = HoneypotLogger()
    parser = MySQLLogParser(db=db, hplogger=hplogger)

    if not GENERAL_LOG.exists():
        logger.error(f"MySQL general log not found: {GENERAL_LOG}")
        logger.error("Enable it in /etc/mysql/mysql.conf.d/mysqld.cnf:")
        logger.error("  general_log = ON")
        logger.error("  general_log_file = /var/log/mysql/general.log")
        sys.exit(1)

    logger.info("MySQL general query log parser started.")
    try:
        parser.tail()
    except KeyboardInterrupt:
        logger.info("Stopped.")


if __name__ == "__main__":
    main()
