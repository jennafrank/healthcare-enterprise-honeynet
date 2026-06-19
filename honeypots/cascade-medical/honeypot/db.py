"""
Database layer — SQLite with WAL mode for concurrent honeypot writes.
"""

import sqlite3
import json
import threading
from datetime import datetime
from pathlib import Path


DB_PATH = Path("/app/data/meridian_honeypot.db")
SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE,
    peer_ip TEXT NOT NULL,
    service TEXT DEFAULT 'ssh',
    username TEXT,
    password TEXT,
    auth_success INTEGER DEFAULT 0,
    connect_time TEXT DEFAULT (datetime('now')),
    disconnect_time TEXT,
    duration_seconds INTEGER,
    command_count INTEGER DEFAULT 0,
    high_interest INTEGER DEFAULT 0,
    high_interest_reason TEXT,
    sophistication_score INTEGER DEFAULT 1,
    country TEXT,
    city TEXT,
    asn TEXT,
    isp TEXT,
    is_vpn INTEGER DEFAULT 0,
    is_cloud INTEGER DEFAULT 0,
    abuse_confidence INTEGER DEFAULT 0,
    rdns TEXT,
    mitre_techniques TEXT DEFAULT '[]',
    UNIQUE(session_id)
);

CREATE TABLE IF NOT EXISTS commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    command TEXT,
    timestamp TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS credential_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    peer_ip TEXT,
    service TEXT DEFAULT 'ssh',
    username TEXT,
    password TEXT,
    timestamp TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE INDEX IF NOT EXISTS idx_sessions_ip ON sessions(peer_ip);
CREATE INDEX IF NOT EXISTS idx_sessions_service ON sessions(service);
CREATE INDEX IF NOT EXISTS idx_sessions_high_interest ON sessions(high_interest);
CREATE INDEX IF NOT EXISTS idx_commands_session ON commands(session_id);
CREATE INDEX IF NOT EXISTS idx_creds_ip ON credential_attempts(peer_ip);
"""

_session_counter = 0
_counter_lock = threading.Lock()


def _make_session_id(service: str) -> str:
    global _session_counter
    with _counter_lock:
        _session_counter += 1
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"{service}_{ts}_{_session_counter:06d}"


class DB:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_schema()

    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return self._local.conn

    def _init_schema(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(SCHEMA)
        conn.commit()
        conn.close()

    def create_session(self, peer_ip: str, service: str = "ssh") -> str:
        sid = _make_session_id(service)
        self._conn().execute(
            "INSERT OR IGNORE INTO sessions (session_id, peer_ip, service) VALUES (?, ?, ?)",
            (sid, peer_ip, service)
        )
        self._conn().commit()
        return sid

    def update_session_auth(self, session_id: str, username: str, password: str, success: bool):
        self._conn().execute(
            "UPDATE sessions SET username=?, password=?, auth_success=? WHERE session_id=?",
            (username, password, int(success), session_id)
        )
        self._conn().commit()

    def log_credential(self, session_id: str, username: str, password: str, service: str = "ssh"):
        row = self._conn().execute(
            "SELECT peer_ip FROM sessions WHERE session_id=?", (session_id,)
        ).fetchone()
        ip = row["peer_ip"] if row else "unknown"
        self._conn().execute(
            "INSERT INTO credential_attempts (session_id, peer_ip, service, username, password) VALUES (?,?,?,?,?)",
            (session_id, ip, service, username, password)
        )
        self._conn().commit()

    def log_command(self, session_id: str, command: str):
        self._conn().execute(
            "INSERT INTO commands (session_id, command) VALUES (?,?)",
            (session_id, command)
        )
        self._conn().execute(
            "UPDATE sessions SET command_count = command_count + 1 WHERE session_id=?",
            (session_id,)
        )
        self._conn().commit()

    def close_session(self, session_id: str, duration: int):
        self._conn().execute(
            "UPDATE sessions SET disconnect_time=datetime('now'), duration_seconds=? WHERE session_id=?",
            (duration, session_id)
        )
        self._conn().commit()

    def flag_high_interest(self, session_id: str, reason: str):
        existing = self._conn().execute(
            "SELECT high_interest_reason FROM sessions WHERE session_id=?", (session_id,)
        ).fetchone()
        if existing:
            prev = existing["high_interest_reason"] or ""
            combined = (prev + " | " + reason).strip(" | ") if prev else reason
            self._conn().execute(
                "UPDATE sessions SET high_interest=1, high_interest_reason=? WHERE session_id=?",
                (combined, session_id)
            )
            self._conn().commit()

    def update_enrichment(self, session_id: str, data: dict):
        self._conn().execute(
            """UPDATE sessions SET country=?, city=?, asn=?, isp=?,
               is_vpn=?, is_cloud=?, abuse_confidence=?, rdns=?
               WHERE session_id=?""",
            (
                data.get("country"), data.get("city"), data.get("asn"),
                data.get("isp"), int(data.get("is_vpn", False)),
                int(data.get("is_cloud", False)), data.get("abuse_confidence", 0),
                data.get("rdns"), session_id
            )
        )
        self._conn().commit()

    def update_mitre(self, session_id: str, techniques: list, score: int = None):
        update = "UPDATE sessions SET mitre_techniques=?"
        params = [json.dumps(techniques)]
        if score is not None:
            update += ", sophistication_score=?"
            params.append(score)
        update += " WHERE session_id=?"
        params.append(session_id)
        self._conn().execute(update, params)
        self._conn().commit()

    def get_session_commands(self, session_id: str) -> list:
        rows = self._conn().execute(
            "SELECT command FROM commands WHERE session_id=? ORDER BY id", (session_id,)
        ).fetchall()
        return [r["command"] for r in rows]

    def update_session_auth(self, session_id: str, username: str, password: str, success: bool):
        self._conn().execute(
            "UPDATE sessions SET username=?, password=?, auth_success=? WHERE session_id=?",
            (username, password, int(success), session_id)
        )
        self._conn().commit()

    # ─── Dashboard Queries ────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        c = self._conn()
        total = c.execute("SELECT COUNT(*) as n FROM sessions").fetchone()["n"]
        authed = c.execute("SELECT COUNT(*) as n FROM sessions WHERE auth_success=1").fetchone()["n"]
        hi = c.execute("SELECT COUNT(*) as n FROM sessions WHERE high_interest=1").fetchone()["n"]
        creds = c.execute("SELECT COUNT(*) as n FROM credential_attempts").fetchone()["n"]
        cmds = c.execute("SELECT COUNT(*) as n FROM commands").fetchone()["n"]
        unique_ips = c.execute("SELECT COUNT(DISTINCT peer_ip) as n FROM sessions").fetchone()["n"]
        return {
            "total_sessions": total,
            "authenticated_sessions": authed,
            "high_interest_sessions": hi,
            "credential_attempts": creds,
            "total_commands": cmds,
            "unique_ips": unique_ips,
        }

    def get_recent_sessions(self, limit: int = 50) -> list:
        rows = self._conn().execute(
            """SELECT session_id, peer_ip, service, username, auth_success,
                      connect_time, duration_seconds, command_count, high_interest,
                      high_interest_reason, sophistication_score, country, city,
                      isp, abuse_confidence, mitre_techniques
               FROM sessions ORDER BY id DESC LIMIT ?""", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_top_countries(self, limit: int = 10) -> list:
        rows = self._conn().execute(
            "SELECT country, COUNT(*) as cnt FROM sessions WHERE country IS NOT NULL GROUP BY country ORDER BY cnt DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_top_credentials(self, limit: int = 15) -> list:
        rows = self._conn().execute(
            "SELECT username, password, COUNT(*) as cnt FROM credential_attempts GROUP BY username, password ORDER BY cnt DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_top_asns(self, limit: int = 10) -> list:
        rows = self._conn().execute(
            "SELECT asn, isp, is_cloud, COUNT(*) as cnt FROM sessions WHERE asn IS NOT NULL GROUP BY asn ORDER BY cnt DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_service_breakdown(self) -> list:
        rows = self._conn().execute(
            "SELECT service, COUNT(*) as cnt FROM sessions GROUP BY service"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_hourly_volume(self) -> list:
        rows = self._conn().execute(
            """SELECT strftime('%Y-%m-%d %H:00', connect_time) as hour,
                      COUNT(*) as cnt
               FROM sessions
               WHERE connect_time >= datetime('now', '-24 hours')
               GROUP BY hour ORDER BY hour"""
        ).fetchall()
        return [dict(r) for r in rows]

    def get_mitre_summary(self) -> list:
        rows = self._conn().execute(
            "SELECT mitre_techniques FROM sessions WHERE mitre_techniques != '[]'"
        ).fetchall()
        counts = {}
        for row in rows:
            try:
                techs = json.loads(row["mitre_techniques"])
                for t in techs:
                    tid = t["technique_id"]
                    if tid not in counts:
                        counts[tid] = {"technique_id": tid, "technique_name": t["technique_name"], "count": 0}
                    counts[tid]["count"] += 1
            except Exception:
                pass
        return sorted(counts.values(), key=lambda x: x["count"], reverse=True)

    def get_high_interest_sessions(self, limit: int = 20) -> list:
        rows = self._conn().execute(
            """SELECT s.session_id, s.peer_ip, s.service, s.username, s.connect_time,
                      s.duration_seconds, s.command_count, s.sophistication_score,
                      s.high_interest_reason, s.country, s.city, s.isp,
                      s.abuse_confidence, s.mitre_techniques,
                      GROUP_CONCAT(c.command, ' | ') as commands
               FROM sessions s
               LEFT JOIN commands c ON s.session_id = c.session_id
               WHERE s.high_interest = 1
               GROUP BY s.session_id
               ORDER BY s.id DESC LIMIT ?""", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_sophistication_distribution(self) -> list:
        rows = self._conn().execute(
            "SELECT sophistication_score, COUNT(*) as cnt FROM sessions GROUP BY sophistication_score ORDER BY sophistication_score"
        ).fetchall()
        return [dict(r) for r in rows]
