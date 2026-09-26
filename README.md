# 🍯 Healthcare Enterprise Honeynet

**A production-grade two-node honeypot deployment for threat hunting, SOC training, and attacker behavior research.**

Built and maintained by [Jenna Frank](https://github.com/jennafrank) using [Claude Code](https://claude.ai/code).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Docker](https://img.shields.io/badge/docker-compose-blue)
![Platform](https://img.shields.io/badge/platform-Azure-0078d4)

---

## What Is This?

The Healthcare Enterprise Honeynet is a realistic multi-service honeypot environment that mimics two organizations in a healthcare network:

| Node                    | Identity                        | Services                                        |
|-------------------------|---------------------------------|-------------------------------------------------|
| **Meridian HR**         | A fictional HR software company | SSH, Redis, MongoDB, MySQL, Kerberos, LDAP, SMB |
| **Cascade Medical EMR** | A fictional hospital EMR system | RDP, MSSQL, VNC, Telnet, SSH, HL7, SMTP         |

Every attacker who touches either system is logged, enriched with threat intelligence, scored for sophistication, and surfaced in a real-time SOC dashboard. The two nodes are networked to attract — and detect — lateral movement between them.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│           Healthcare Enterprise Honeynet Cyber Range                │
│                        Azure East US 2                              │
├──────────────────────────────┬──────────────────────────────────────┤
│   Meridian HR Node           │   Cascade Medical Node               │
│   <public-ip>                │   <public-ip>                        │
│                              │                                      │
│   SSH     :22                │   RDP      :3389                     │
│   Redis   :6379              │   MSSQL    :1433                     │
│   MongoDB :27017             │   VNC      :5900                     │
│   MySQL   :3306              │   Telnet   :23                       │
│   Kerberos:88                │   SSH      :22                       │
│   LDAP    :389/636           │   HL7      :2575                     │
│   SMB     :445               │   SMTP     :25                       │
│                              │                                      │
│   Dashboard  :8080           │   Dashboard  :8080                   │
│   Unified    :9090 ──────────┼──► (pulls from both)                 │
└──────────────────────────────┴──────────────────────────────────────┘
                                        │
                               SQLite per node
                               events.jsonl per node
                               Full threat enrichment
                               MITRE ATT&CK mapping
```

---

## Dashboards

The dashboards are not publicly hosted. Run them on your own deployment:

| Dashboard | URL | Description |
|-----------|-----|-------------|
| Meridian HR | `http://<meridian-public-ip>:8080` | Single-node Meridian dashboard |
| Cascade Medical | `http://<cascade-public-ip>:8080` | Single-node Cascade dashboard |
| **Unified SOC** | `http://<meridian-public-ip>:9090` | **Combined view of both honeypots** |

The unified dashboard includes a **Threat Hunt** panel: search across both honeypots by IP, username, command, or service with live results. Set the Cascade node's address in `honeypots/meridian-hr/dashboard/templates/unified.html` (`CAS_BASE`).

> [!WARNING]
> **The dashboards and the search API have no authentication**, and they listen on all interfaces (`0.0.0.0`). Anyone who can reach ports 8080 and 9090 can read every captured session, credential and command. Restrict those ports to your own IP address with an Azure Network Security Group, or reach them through an SSH tunnel. Do not expose them to the internet. The unified dashboard's browser code calls the Cascade node's API directly, so the Cascade port 8080 rule must allow your IP too.

---

## Quick Start

### Prerequisites

- Docker + Docker Compose
- Python 3.12+
- An Azure VM (or any Linux host) with ports accessible

### Deploy Meridian HR

```bash
git clone https://github.com/jennafrank/healthcare-enterprise-honeynet.git
cd healthcare-enterprise-honeynet/honeypots/meridian-hr

cp .env.example .env
# Edit .env with your API keys

docker compose up -d
```

Dashboard at `http://YOUR_IP:8080`

### Deploy Cascade Medical

```bash
cd healthcare-enterprise-honeynet/honeypots/cascade-medical

cp .env.example .env
docker compose up -d
```

Dashboard at `http://YOUR_IP:8080`

### Deploy Unified Dashboard

The unified dashboard runs as a second Flask app on port 9090 of the Meridian node. It's included in `unified_app.py` and started automatically by `main.py`. Update `CAS_BASE` in `dashboard/templates/unified.html` to point to your Cascade node's IP.

---

## Services Covered

What attackers actually did, from the honeypot databases in [`backups/`](backups/). This is a short window: about a day and a half per node, June 17 to 19, 2026 (timestamps as recorded by the honeypots).

**Across both nodes, nearly everything was internet-wide scanning and credential guessing.** None of the deeper techniques these services were built to attract (AS-REP roasting, Redis replication hijack, `xp_cmdshell`, HL7 record enumeration) appeared in this window.

### Meridian HR (Corporate HR System)

June 17 22:46 to June 19 04:53: 444 sessions from 208 IP addresses.

| Service | Port | Sessions | Source IPs | What we saw |
|---------|------|---------:|-----------:|-------------|
| SSH | 22 | 157 | 59 | 81 login attempts from 8 IPs; `root`, `admin` and `test` tried most. No commands recorded. |
| LDAP | 389/636 | 111 | 72 | Connections only; no directory queries recorded. |
| MongoDB | 27017 | 105 | 44 | Handshake queries against `admin.$cmd` and a `buildinfo` probe. Fingerprinting, no data access. |
| Redis | 6379 | 37 | 21 | `PING`, `INFO`, `QUIT`, and HTTP `GET` requests sent to the Redis port by web scanners. No config changes. |
| Kerberos | 88 | 34 | 19 | Malformed and HTTP-style requests from scanners. No AS-REP roasting or Kerberoasting. |
| MySQL | 3306 | 0 | 0 | None recorded in this window. |
| SMB | 445 | 0 | 0 | None recorded in this window. |

### Cascade Medical EMR (Hospital System)

June 18 03:25 to June 19 05:43: 2,458 sessions from 122 IP addresses.

| Service | Port | Sessions | Source IPs | What we saw |
|---------|------|---------:|-----------:|-------------|
| Telnet | 23 | 1,516 | 17 | 3,744 login attempts from 12 IPs. The most common "usernames" were `enable`, `system` and `sh`, shell-escape strings used by IoT botnet tooling. |
| VNC | 5900 | 717 | 3 | 713 login attempts from a single IP, all with username `vnc`. |
| SSH | 22 | 67 | 49 | 10 login attempts from 5 IPs. No commands recorded. |
| MongoDB | 27017 | 49 | 4 | Handshake queries against `admin.$cmd`. |
| RDP | 3389 | 42 | 6 | Connection requests carrying scanner `mstshash` cookies; 5 login attempts. |
| LDAP | 389/636/3268 | 15 | 9 | Connections only. |
| SMTP | 25/587 | 12 | 10 | `EHLO` from scanners identifying as `masscan` and `scan.invalid`, and `STARTTLS`. No relay attempts recorded. |
| Kerberos | 88 | 11 | 8 | Malformed and HTTP-style requests. |
| MySQL | 3306 | 9 | 7 | `SET AUTOCOMMIT=0`, `SHOW DATABASES`. |
| Redis | 6379 | 9 | 5 | `PING`, `INFO`, `QUIT`. |
| Elasticsearch | 9200 | 8 | 3 | `GET /` and `GET /_cat/indices`: index enumeration. |
| MSSQL | 1433 | 3 | 1 | Connections only; no queries recorded. |
| HL7 | 2575 | 0 | 0 | None recorded in this window. |
| SMB | 445 | 0 | 0 | None recorded in this window. |

---

## Synthetic Document Ecosystem

Both honeypot nodes include a **3,181-file synthetic document library** (`northstar-documents/`) representing NorthStar Regional Health Network — a fictional healthcare organization. Files span 2016–2026 and include:

- **HR records**: Employee contracts, W-2 forms, performance reviews, org charts
- **Patient files**: Intake forms, discharge summaries, lab results, prescriptions
- **IT documentation**: Network diagrams, runbooks, incident reports, change logs
- **Executive content**: Board minutes, strategic plans, M&A documents, budgets
- **Personal clutter**: Desktop screenshots, browser bookmarks, draft emails, journal entries
- **Billing & insurance**: Claims, EOBs, insurance correspondence
- **Compliance**: HIPAA assessments, audit reports, BAA agreements

All PII is **entirely synthetic** — SSNs use 9XX prefixes (invalid), phone numbers use 555 area codes, and no real individuals are represented.

This dataset makes the honeypot realistic enough to attract and hold attacker attention, while providing rich data for threat hunting training.

> **Generator script**: `docs/gen_northstar.py` — run with `python3 gen_northstar.py` to regenerate all 3,181 files.

---

## Threat Intelligence Stack

Each session is automatically enriched with:

- **IP geolocation** (country, city, ISP, ASN)
- **AbuseIPDB score** (abuse confidence 0-100)
- **VPN/datacenter detection**
- **MITRE ATT&CK technique mapping** (T1059, T1082, T1547, etc.)
- **Sophistication scoring** (1-10 scale)
- **High-interest flagging** (lateral movement, persistence attempts, privilege escalation)

---

## Threat Hunting

The `threat-hunting/` directory contains:

| File | Description |
|------|-------------|
| [`threat_hunting_queries.kql`](threat-hunting/threat_hunting_queries.kql) | 30+ KQL queries (adaptable to SQL/DuckDB) covering recon, brute force, lateral movement, MITRE TTPs, anomaly detection |
| [`threat_hunting_guide_for_newbies.md`](threat-hunting/threat_hunting_guide_for_newbies.md) | Beginner's guide: what to look for, how to read attack chains, full worked example with MITRE mapping |
| [`sophistication_rating_framework.md`](threat-hunting/sophistication_rating_framework.md) | 1-10 attacker scoring rubric, vulnerability severity ratings, 4 scored real-world examples |

### Live Hunt

Use the **Threat Hunt panel** in the unified dashboard at `http://<meridian-public-ip>:9090`:
- Search by IP, username, command keyword, or service
- Results across Sessions, Commands, and Credentials tabs
- Queries both honeypots simultaneously

### API Search

```bash
# Find all wget/curl commands
curl "http://<meridian-public-ip>:8080/api/search?command=wget"

# Find all attempts from a specific IP
curl "http://<meridian-public-ip>:8080/api/search?ip=203.0.113"

# Find all SSH attempts with username 'admin'
curl "http://<meridian-public-ip>:8080/api/search?username=admin&service=ssh"
```

---

## Repo Structure

```
healthcare-enterprise-honeynet/
├── README.md
├── ARCHITECTURE.md
├── LICENSE
├── .gitignore
│
├── honeypots/
│   ├── meridian-hr/              # Meridian HR honeypot
│   │   ├── honeypot/             # Core service emulators
│   │   │   ├── server.py         # Main listener orchestrator
│   │   │   ├── db.py             # SQLite data layer + search
│   │   │   ├── shell.py          # Fake SSH shell
│   │   │   ├── logger.py         # JSONL event logger
│   │   │   ├── session.py        # Session management
│   │   │   ├── enrichment.py     # IP enrichment (geo, abuse)
│   │   │   ├── mitre.py          # MITRE ATT&CK mapping
│   │   │   ├── nosql_servers.py  # Redis + MongoDB emulators
│   │   │   ├── ad/               # Kerberos/LDAP/AD emulation
│   │   │   └── ...
│   │   ├── dashboard/
│   │   │   ├── app.py            # Flask API + /api/search
│   │   │   └── templates/
│   │   │       ├── index.html    # Meridian SOC dashboard
│   │   │       └── unified.html  # Unified SOC dashboard (port 9090)
│   │   ├── main.py               # Entry point (starts all services)
│   │   ├── unified_app.py        # Unified dashboard Flask app
│   │   ├── lateral_detector.py   # Cross-honeypot pivot detection
│   │   ├── docker-compose.yml
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── .env.example
│   │
│   └── cascade-medical/          # Cascade Medical EMR honeypot
│       ├── honeypot/             # RDP, MSSQL, VNC, HL7, SMTP emulators
│       ├── dashboard/
│       │   ├── app.py            # Flask API + /api/search
│       │   └── templates/
│       │       └── index.html    # Cascade SOC dashboard
│       ├── main.py
│       ├── docker-compose.yml
│       ├── Dockerfile
│       ├── requirements.txt
│       └── .env.example
│
├── threat-hunting/
│   ├── threat_hunting_queries.kql          # 30+ hunt queries
│   ├── threat_hunting_guide_for_newbies.md # Beginner's guide
│   └── sophistication_rating_framework.md  # Attacker scoring
│
├── azure/
│   ├── VM_setup.md               # VM sizing and configuration
│   └── NSG_rules.md              # Required firewall rules
│
└── docs/
    ├── DEPLOYMENT.md             # Step-by-step deploy guide
    ├── TROUBLESHOOTING.md        # Common issues and fixes
    ├── FAQ.md                    # Frequently asked questions
    └── gen_northstar.py          # Synthetic document generator (3,181 files)
```

---

## Azure Deployment

See [`azure/VM_setup.md`](azure/VM_setup.md) for full instructions. Quick reference:

**Recommended VM specs per node:**
- Size: `Standard_B2s` (2 vCPU, 4GB RAM)
- OS: Ubuntu 22.04 LTS
- Disk: 30GB Standard SSD
- Region: East US 2

**Required NSG inbound rules:**
```
Port 22    → SSH (management)
Port 8080  → Dashboard
Port 9090  → Unified dashboard (Meridian only)
Port 2223  → Alternate SSH (optional management port)
```
Plus whichever honeypot ports you want exposed to the internet.

---

## Built With Claude Code

I built this with [Claude Code](https://claude.ai/code) as my coding partner. Claude Code wrote most of the Python service emulators, the Flask dashboards, the synthetic documents and the documentation, working from my direction. My part:

- **Designed the scenario:** two fictional healthcare organizations, an HR software company and a hospital EMR, on separate Azure VMs, networked so lateral movement between them would show up. I chose which services each node exposes.
- **Decided what to capture:** session, credential and command logging per node, MITRE ATT&CK tagging, and the 1 to 10 sophistication rubric in [`threat-hunting/`](threat-hunting/).
- **Deployed and ran it** on Azure and collected the attacker traffic summarized in [Services Covered](#services-covered).
- **Tested and verified it** myself before and during the run.

---

## Contributing

Pull requests welcome. Areas of interest:

- New protocol emulators (FTP, Elasticsearch, Postgres)
- Better GeoIP integration
- Terraform/Ansible for one-click deployment
- ML-based attacker clustering
- MISP/OpenCTI threat intel integration
- Grafana dashboard alternative

---

## Ethical Use

This software is for **defensive security research, SOC training, and honeypot deployment on systems you own or have explicit permission to monitor**. Do not deploy against systems you do not own. All attacker data captured is for research purposes only.

---

## License

MIT — see [LICENSE](LICENSE).
