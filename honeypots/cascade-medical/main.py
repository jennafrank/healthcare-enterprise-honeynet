"""
Cascade Medical Center Honeypot — Main Entry Point
Services: SSH, RDP, VNC, Telnet, MySQL, MSSQL, Redis, MongoDB,
          Elasticsearch, SMTP, HL7, LDAP/AD, SMB + Samba, Dashboard

Honeynet node — paired with Meridian HR (10.0.0.4)
Update MERIDIAN_IP below with your teammate's actual VM private IP.
"""

import asyncio
import asyncssh
import logging
import os
import sys
import threading
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/app/logs/cascade_honeypot.log"),
    ]
)
logger = logging.getLogger("cascade_main")

from honeypot.db import DB
from honeypot.logger import HoneypotLogger
from honeypot.mysql_server import start_mysql_server
from honeypot.nosql_servers import start_redis_server, start_mongodb_server
from honeypot.ad_server import start_ldap_server, start_ldaps_server, start_gc_server, start_kerberos_server
from honeypot.smb_server import start_smb_server
from honeypot.extra_servers import (
    start_rdp_server, start_vnc_server, start_telnet_server,
    start_mssql_server, start_elasticsearch_server,
    start_smtp_server, start_hl7_server,
)
from honeypot.mitre import tag_session

# ─── Config ───────────────────────────────────────────────────────────────────
BIND_HOST      = os.environ.get("BIND_HOST", "0.0.0.0")
SSH_PORT       = int(os.environ.get("SSH_PORT", 22))
RDP_PORT       = int(os.environ.get("RDP_PORT", 3389))
VNC_PORT       = int(os.environ.get("VNC_PORT", 5900))
TELNET_PORT    = int(os.environ.get("TELNET_PORT", 23))
MYSQL_PORT     = int(os.environ.get("MYSQL_PORT", 3306))
MSSQL_PORT     = int(os.environ.get("MSSQL_PORT", 1433))
REDIS_PORT     = int(os.environ.get("REDIS_PORT", 6379))
MONGO_PORT     = int(os.environ.get("MONGO_PORT", 27017))
ES_PORT        = int(os.environ.get("ES_PORT", 9200))
SMTP_PORT      = int(os.environ.get("SMTP_PORT", 25))
SMTP_ALT_PORT  = int(os.environ.get("SMTP_ALT_PORT", 587))
HL7_PORT       = int(os.environ.get("HL7_PORT", 2575))
LDAP_PORT      = int(os.environ.get("LDAP_PORT", 389))
LDAPS_PORT     = int(os.environ.get("LDAPS_PORT", 636))
GC_PORT        = int(os.environ.get("GC_PORT", 3268))
KRB_PORT       = int(os.environ.get("KRB_PORT", 88))
SMB_PORT       = int(os.environ.get("SMB_PORT", 445))
DASHBOARD_PORT = int(os.environ.get("DASHBOARD_PORT", 8080))
HOST_KEY       = os.environ.get("HOST_KEY_PATH", "/app/data/ssh_host_key")

# ── HONEYNET: Set this to your teammate's VM private IP ───────────────────────
MERIDIAN_IP    = os.environ.get("MERIDIAN_IP", "10.0.0.4")


def generate_host_key():
    key_path = Path(HOST_KEY)
    if not key_path.exists():
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key = asyncssh.generate_private_key("ssh-rsa", key_size=2048)
        key.write_private_key(str(key_path))
    return str(key_path)


def run_dashboard(db: DB):
    sys.path.insert(0, str(Path(__file__).parent))
    from dashboard.app import app
    import dashboard.app as dash_module
    dash_module.db = db
    app.run(host=BIND_HOST, port=DASHBOARD_PORT, debug=False, use_reloader=False)


def _make_ssh_server(db, hplogger):
    from honeypot.ssh_server import HoneypotSSHServer
    return HoneypotSSHServer(db=db, hplogger=hplogger)


async def _handle_ssh_process(process, db, hplogger):
    from honeypot.shell import FakeShell
    import random

    server = process.channel.get_extra_info("server_object") if hasattr(process.channel, "get_extra_info") else None
    session_id = getattr(server, "session_id", "local")
    username = getattr(server, "username", "clinadm")
    peer_ip = getattr(server, "peer_ip", "0.0.0.0")

    shell = FakeShell(chan=process.stdout, session_id=session_id,
                      username=username, db=db, hplogger=hplogger)

    await asyncio.sleep(random.uniform(0.8, 1.8))
    process.stdout.write(shell.motd())
    process.stdout.write(shell.prompt())

    try:
        async for line in process.stdin:
            if line:
                await shell.handle_input(line)
                if not process.stdin.at_eof():
                    process.stdout.write(shell.prompt())
    except Exception:
        pass
    process.exit(0)


async def main():
    logger.info("=" * 65)
    logger.info("  Cascade Medical Center Honeypot — Starting")
    logger.info(f"  Honeynet pair: Meridian HR at {MERIDIAN_IP}")
    logger.info("=" * 65)

    db = DB()
    hplogger = HoneypotLogger()
    host_key = generate_host_key()

    # Generate documents if not already done
    doc_path = Path("/srv/samba/Clinical/Patient_Records")
    if not doc_path.exists() or not any(doc_path.iterdir()):
        logger.info("[Docs] Generating hospital document corpus...")
        try:
            import subprocess
            subprocess.run(["python3", "/app/generate_documents.py"], check=True)
        except Exception as e:
            logger.warning(f"[Docs] Could not auto-generate: {e} — run manually")

    # Start dashboard
    threading.Thread(target=run_dashboard, args=(db,), daemon=True).start()

    # ── Start all honeypot services ───────────────────────────────────────────
    services = [
        ("MySQL",         start_mysql_server(BIND_HOST, MYSQL_PORT, db, hplogger)),
        ("Redis",         start_redis_server(BIND_HOST, REDIS_PORT, db, hplogger)),
        ("MongoDB",       start_mongodb_server(BIND_HOST, MONGO_PORT, db, hplogger)),
        ("RDP",           start_rdp_server(BIND_HOST, RDP_PORT, db, hplogger)),
        ("VNC",           start_vnc_server(BIND_HOST, VNC_PORT, db, hplogger)),
        ("Telnet",        start_telnet_server(BIND_HOST, TELNET_PORT, db, hplogger)),
        ("MSSQL",         start_mssql_server(BIND_HOST, MSSQL_PORT, db, hplogger)),
        ("Elasticsearch", start_elasticsearch_server(BIND_HOST, ES_PORT, db, hplogger)),
        ("SMTP",          start_smtp_server(BIND_HOST, SMTP_PORT, db, hplogger)),
        ("SMTP-587",      start_smtp_server(BIND_HOST, SMTP_ALT_PORT, db, hplogger)),
        ("HL7",           start_hl7_server(BIND_HOST, HL7_PORT, db, hplogger)),
        ("LDAP",          start_ldap_server(BIND_HOST, LDAP_PORT, db, hplogger)),
        ("LDAPS",         start_ldaps_server(BIND_HOST, LDAPS_PORT, db, hplogger)),
        ("GlobalCatalog", start_gc_server(BIND_HOST, GC_PORT, db, hplogger)),
        ("Kerberos",      start_kerberos_server(BIND_HOST, KRB_PORT, db, hplogger)),
    ]

    for name, coro in services:
        try:
            await coro
        except OSError as e:
            logger.warning(f"[{name}] Could not bind: {e}")

    # SMB
    try:
        await start_smb_server(BIND_HOST, SMB_PORT, db, hplogger)
    except OSError:
        logger.warning("[SMB] Port 445 unavailable — real Samba may own it (OK)")

    # SSH
    try:
        await asyncssh.create_server(
            lambda: _make_ssh_server(db, hplogger),
            BIND_HOST, SSH_PORT,
            server_host_keys=[host_key],
            process_factory=lambda p: _handle_ssh_process(p, db, hplogger),
        )
        logger.info(f"[SSH] {BIND_HOST}:{SSH_PORT}")
    except Exception as e:
        logger.warning(f"[SSH] {e}")

    # Summary
    logger.info("")
    logger.info("  ██████╗ █████╗ ███████╗ ██████╗ █████╗ ██████╗ ███████╗")
    logger.info("  Cascade Medical Center Honeynet Node — ALL SERVICES UP")
    logger.info(f"  Dashboard:  http://{BIND_HOST}:{DASHBOARD_PORT}")
    logger.info(f"  Paired with Meridian HR at: {MERIDIAN_IP}")
    logger.info("  Lateral movement between nodes will be detected.")
    logger.info("")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
