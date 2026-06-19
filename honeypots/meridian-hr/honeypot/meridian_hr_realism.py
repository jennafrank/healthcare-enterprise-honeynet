"""
Realism enhancements for the Meridian HR honeypot.

Usage — import what you need:
  from .meridian_hr_realism import ssh_latency, mysql_latency
  from .meridian_hr_realism import build_smb_share_files
  from .meridian_hr_realism import generate_noise_lines
  from .meridian_hr_realism import configure_rotating_logger, write_logrotate_conf
"""

import asyncio
import logging
import logging.handlers
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


# ─── Latency helpers ─────────────────────────────────────────────────────────

async def ssh_latency() -> None:
    """50–200ms per-command delay.  Drop-in for shell._dispatch."""
    await asyncio.sleep(random.uniform(0.05, 0.20))


async def mysql_latency() -> None:
    """30–150ms per-query delay.  Call at the top of _handle_query."""
    await asyncio.sleep(random.uniform(0.03, 0.15))


# ─── Document metadata ───────────────────────────────────────────────────────

def _random_doc_date(anchor: datetime, span_days: int = 180) -> str:
    delta = random.randint(0, span_days)
    return (anchor - timedelta(days=delta)).strftime("%Y-%m-%d")


def randomize_smb_files(
    files_dict: Dict[str, List[Tuple]],
    anchor: datetime = None,
) -> Dict[str, List[Tuple]]:
    """
    Return a copy of FAKE_FILES with dates randomised over a 6-month window
    and sizes jittered ±5% so every run looks like a lived-in server.
    Call once at startup and assign back to smb_server.FAKE_FILES.
    """
    if anchor is None:
        anchor = datetime.utcnow()
    out: Dict[str, List[Tuple]] = {}
    for share, entries in files_dict.items():
        refreshed = []
        for name, size, _old_date in entries:
            new_date = _random_doc_date(anchor)
            new_size = int(size * random.uniform(0.95, 1.05))
            refreshed.append((name, new_size, new_date))
        out[share] = refreshed
    return out


# ─── SMB share file builder ───────────────────────────────────────────────────
# Keeps share listings current (no hardcoded 2024 dates) and adds variety.

_HR_TEMPLATES = [
    "Employee_Directory_{year}.xlsx",
    "Org_Chart_Q{q}_{year}.pdf",
    "Performance_Reviews_{year}.xlsx",
    "New_Hire_Onboarding_Template.docx",
    "Termination_Checklist.docx",
    "Salary_Bands_{year}_CONFIDENTIAL.xlsx",
    "Job_Description_Templates_{year}.docx",
    "Benefits_Enrollment_{year}.xlsx",
    "FMLA_Request_Forms.pdf",
    "EEO_Report_{year}.xlsx",
    "Exit_Interview_Summary_{year}.pdf",
    "HR_Policy_Manual_v{v}.pdf",
]

_FINANCE_TEMPLATES = [
    "Payroll_Export_{mon}{year}.csv",
    "Q{q}_{year}_Financial_Report.xlsx",
    "Budget_FY{year}_INTERNAL.xlsx",
    "Vendor_Payments_{year}.xlsx",
    "W2_Archive_{prev_year}.zip",
    "Direct_Deposit_Accounts.xlsx",
    "AP_Aging_Report_{mon}{year}.xlsx",
    "Expense_Reports_{year}_Q{q}.xlsx",
    "1099_Contractors_{year}.xlsx",
    "Bank_Reconciliation_{mon}{year}.xlsx",
]

_BACKUP_TEMPLATES = [
    "meridian_hr_db_{date}.sql.gz",
    "config_backup_{date}.tar.gz",
    "redis_dump_{date}.rdb",
    "mongo_backup_{date}.tar.gz",
    "nginx_conf_backup_{date}.tar.gz",
]


def build_smb_share_files(anchor: datetime = None) -> Dict[str, List[Tuple]]:
    """
    Generate current FAKE_FILES relative to *anchor* (defaults to now).
    Assign to smb_server.FAKE_FILES at startup so the honeypot never shows
    stale 2024 timestamps.

    Example:
        from honeypot.meridian_hr_realism import build_smb_share_files
        smb_server.FAKE_FILES = build_smb_share_files()
    """
    if anchor is None:
        anchor = datetime.utcnow()

    year = anchor.year
    prev_year = year - 1
    q = (anchor.month - 1) // 3 + 1
    mon = anchor.strftime("%b")   # e.g. "Jun" — templates append year separately
    v = random.randint(3, 7)

    def rdate() -> str:
        return _random_doc_date(anchor)

    def rsize(lo: int, hi: int) -> int:
        return random.randint(lo, hi)

    hr_files = [
        (t.format(year=year, q=q, v=v), rsize(80_000, 5_000_000), rdate())
        for t in random.sample(_HR_TEMPLATES, k=6)
    ]

    finance_files = [
        (t.format(year=year, prev_year=prev_year, q=q, mon=mon), rsize(200_000, 20_000_000), rdate())
        for t in random.sample(_FINANCE_TEMPLATES, k=7)
    ]

    backup_files = [
        (
            _BACKUP_TEMPLATES[i % len(_BACKUP_TEMPLATES)].format(
                date=(anchor - timedelta(days=i)).strftime("%Y%m%d")
            ),
            rsize(50_000_000, 600_000_000),
            (anchor - timedelta(days=i)).strftime("%Y-%m-%d"),
        )
        for i in range(5)
    ]

    return {"HR": hr_files, "Finance": finance_files, "Backups": backup_files}


# ─── System noise log lines ──────────────────────────────────────────────────
# Append these to shell._fake_auth_log() or write to /var/log/syslog output.

_NOISE_TEMPLATES = [
    "{ts} {host} CRON[{pid}]: (root) CMD (/opt/meridian/scripts/health_check.sh)",
    "{ts} {host} CRON[{pid}]: (CRON) error (grandchild #2 failed with exit status 1)",
    "{ts} {host} kernel: [UFW BLOCK] IN=eth0 OUT= SRC={ext_ip} DST=10.0.1.{last} PROTO=TCP DPT=3306",
    "{ts} {host} sshd[{pid}]: Failed password for invalid user {bad_user} from {ext_ip} port {port} ssh2",
    "{ts} {host} sshd[{pid}]: Connection closed by invalid user {bad_user} {ext_ip} port {port} [preauth]",
    "{ts} {host} sudo[{pid}]:  meridian : TTY=pts/0 ; PWD=/opt/meridian ; USER=root ; COMMAND=/bin/systemctl status mysql",
    "{ts} {host} systemd[1]: meridian-payroll.service: Scheduled restart job, restart counter is at 1.",
    "{ts} {host} systemd[1]: Started Session {sess} of user meridian.",
    "{ts} {host} mysqld[{pid}]: [Warning] Aborted connection {conn} to db: 'meridian_hr' user: 'meridian_app' host: 'localhost' (Got an error reading communication packets)",
    "{ts} {host} run-parts[{pid}]: (/etc/cron.daily) finished logrotate",
    "{ts} {host} postfix/pickup[{pid}]: {msgid}: uid=1000 from=<meridian@meridianhr.internal>",
    "{ts} {host} sshd[{pid}]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 rhost={ext_ip}",
    "{ts} {host} kernel: [UFW BLOCK] IN=eth0 OUT= SRC={ext_ip} DST=10.0.1.{last} PROTO=TCP DPT=445",
    "{ts} {host} sudo[{pid}]: pam_unix(sudo:auth): authentication failure; logname=deploy uid=1004 euid=0",
    "{ts} {host} CRON[{pid}]: (root) CMD (/opt/meridian/scripts/rotate_logs.sh >> /var/log/rotation.log 2>&1)",
]

_BAD_USERS = [
    "admin", "oracle", "ubnt", "pi", "test", "guest", "ftpuser",
    "user", "support", "nagios", "ansible", "deploy", "git",
]


def generate_noise_lines(
    count: int = 20,
    host: str = "meridian-hrprod-01",
    anchor: datetime = None,
) -> List[str]:
    """
    Return *count* realistic syslog-format noise lines spread over the
    past hour.  Use in shell._fake_auth_log() or in a /var/log/syslog handler.
    """
    if anchor is None:
        anchor = datetime.utcnow()
    lines = []
    for _ in range(count):
        when = anchor - timedelta(seconds=random.randint(0, 3600))
        ts = when.strftime("%b %d %H:%M:%S")
        tmpl = random.choice(_NOISE_TEMPLATES)
        lines.append(tmpl.format(
            ts=ts,
            host=host,
            pid=random.randint(1000, 9999),
            ext_ip=(
                f"{random.randint(1,254)}.{random.randint(1,254)}"
                f".{random.randint(1,254)}.{random.randint(1,254)}"
            ),
            last=random.randint(1, 60),
            bad_user=random.choice(_BAD_USERS),
            port=random.randint(40000, 65535),
            sess=random.randint(100, 999),
            conn=random.randint(1000, 9999),
            msgid="".join(random.choices("ABCDEF0123456789", k=12)),
        ))
    return sorted(lines)  # chronological by timestamp prefix


# ─── Log rotation ────────────────────────────────────────────────────────────

def configure_rotating_logger(
    name: str,
    log_path: str,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Return a Logger with a RotatingFileHandler (10 MB × 5 = 50 MB cap).
    Replaces any existing handlers on *name* so it is safe to call at startup.
    """
    log = logging.getLogger(name)
    log.setLevel(level)
    log.handlers = [h for h in log.handlers if not isinstance(h, logging.handlers.RotatingFileHandler)]
    handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    ))
    log.addHandler(handler)
    return log


def write_logrotate_conf(
    log_dir: str,
    conf_path: str = "/etc/logrotate.d/meridian-honeypot",
) -> str:
    """
    Write a logrotate(8) config for *.log files in *log_dir*.
    Returns the config text; logs a warning if it cannot write (not root).
    """
    conf = (
        f"{log_dir}/*.log {{\n"
        "    daily\n"
        "    rotate 14\n"
        "    compress\n"
        "    delaycompress\n"
        "    missingok\n"
        "    notifempty\n"
        "    create 0640 root adm\n"
        "    sharedscripts\n"
        "    postrotate\n"
        "        systemctl reload-or-restart rsyslog 2>/dev/null || true\n"
        "    endscript\n"
        "}\n"
    )
    try:
        with open(conf_path, "w") as fh:
            fh.write(conf)
        logging.getLogger("realism").info("logrotate config written to %s", conf_path)
    except PermissionError:
        logging.getLogger("realism").warning(
            "Cannot write %s (not root).  Logrotate config:\n%s", conf_path, conf
        )
    return conf
