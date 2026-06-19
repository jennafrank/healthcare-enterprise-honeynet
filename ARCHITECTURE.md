# Architecture

## Network Topology

```
                        INTERNET
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
    ┌──────────────────┐     ┌──────────────────────┐
    │  Meridian HR     │     │  Cascade Medical EMR │
    │  20.242.13.15    │     │  20.246.106.71       │
    │                  │     │                      │
    │  Azure NSG       │     │  Azure NSG           │
    │  (inbound rules) │     │  (inbound rules)     │
    └────────┬─────────┘     └──────────┬───────────┘
             │                          │
    ┌────────▼─────────┐     ┌──────────▼───────────┐
    │  Docker Container│     │  Docker Container    │
    │  main.py         │     │  main.py             │
    │                  │     │                      │
    │  ┌─────────────┐ │     │  ┌─────────────────┐ │
    │  │ SSH :22     │ │     │  │ RDP    :3389    │ │
    │  │ Redis :6379 │ │     │  │ MSSQL  :1433    │ │
    │  │ Mongo :27017│ │     │  │ VNC    :5900    │ │
    │  │ MySQL :3306 │ │     │  │ Telnet :23      │ │
    │  │ Kerb  :88   │ │     │  │ SSH    :22      │ │
    │  │ LDAP  :389  │ │     │  │ HL7    :2575    │ │
    │  │ SMB   :445  │ │     │  │ SMTP   :25      │ │
    │  └──────┬──────┘ │     │  └────────┬────────┘ │
    │         │        │     │           │          │
    │  ┌──────▼──────┐ │     │  ┌────────▼────────┐ │
    │  │  db.py      │ │     │  │  db.py          │ │
    │  │  SQLite     │ │     │  │  SQLite         │ │
    │  │  JSONL log  │ │     │  │  JSONL log      │ │
    │  └──────┬──────┘ │     │  └────────┬────────┘ │
    │         │        │     │           │          │
    │  ┌──────▼──────┐ │     │  ┌────────▼────────┐ │
    │  │ dashboard/  │ │     │  │ dashboard/      │ │
    │  │ app.py :8080│ │     │  │ app.py :8080    │ │
    │  └─────────────┘ │     │  └─────────────────┘ │
    │                  │     │                      │
    │  ┌─────────────┐ │     │                      │
    │  │unified_app  │ │     │                      │
    │  │ .py :9090   │◄├─────┼── pulls /api/* ──────┘
    │  └─────────────┘ │     │
    └──────────────────┘     └──────────────────────┘
```

## Data Flow

```
Attacker connection
        │
        ▼
Service handler (ssh_server.py, nosql_servers.py, etc.)
        │
        ├── Log raw event → logs/events.jsonl
        │
        ├── Store session → SQLite (db.py)
        │
        ├── Enrich IP → enrichment.py
        │   ├── ip-api.com (geo: country, city, ISP, ASN)
        │   └── AbuseIPDB (abuse confidence score)
        │
        ├── Detect MITRE TTPs → mitre.py
        │   └── Pattern match commands → technique IDs
        │
        ├── Score sophistication → mitre.py
        │   └── 1-10 based on TTPs, persistence, evasion
        │
        ├── Flag high-interest → server.py
        │   └── Lateral movement, persistence, data exfil
        │
        └── Push to SSE queue → dashboard/app.py
                │
                └── Real-time browser update
```

## Component Inventory

### Core Services (`honeypot/`)

| File | Purpose |
|------|---------|
| `server.py` | Orchestrates all listener threads |
| `session.py` | Session lifecycle (create, update, close) |
| `db.py` | SQLite schema, CRUD, dashboard queries, search |
| `logger.py` | JSONL event file writer |
| `shell.py` | Fake interactive SSH shell with realistic responses |
| `enrichment.py` | Async IP enrichment (geo + abuse score) |
| `mitre.py` | Command → MITRE technique regex matching + scoring |
| `nosql_servers.py` | Redis + MongoDB protocol emulators |
| `ssh_server.py` | SSH server using Paramiko |
| `ad/` | Active Directory: Kerberos AS-REQ/TGS-REQ, LDAP bind/search |
| `smb_server.py` | SMB share enumeration emulator |
| `mysql_server.py` | MySQL wire protocol handler |

### Dashboard (`dashboard/`)

| File | Purpose |
|------|---------|
| `app.py` | Flask REST API (12 endpoints + /api/search) |
| `templates/index.html` | Single-node SOC dashboard |
| `templates/unified.html` | Unified cross-node SOC dashboard with hunt panel |

### Unified Dashboard (`unified_app.py`)

Separate Flask app on port 9090. Fetches from both nodes' `/api/*` endpoints using `Promise.allSettled`, merges data, renders combined view. Includes:
- Side-by-side stat cards (Meridian blue / Cascade orange)
- Stacked SVG hourly bar chart (both nodes)
- Combined world heatmap (Canvas API)
- Merged MITRE, credentials, ASN tables
- Separate session tables per node
- **Threat Hunt panel** (live search across both nodes)

### Lateral Detection (`lateral_detector.py`)

Background thread that periodically cross-references both SQLite databases. Flags sessions where the same source IP appears on both nodes within a configurable time window. Writes findings to a `lateral_movement` table.

## Database Schema

```sql
-- sessions: one row per attacker connection
CREATE TABLE sessions (
    id                  INTEGER PRIMARY KEY,
    session_id          TEXT UNIQUE,        -- e.g. ssh_20260619_000001
    peer_ip             TEXT,               -- attacker IP
    service             TEXT,               -- ssh|redis|mongodb|...
    username            TEXT,
    password            TEXT,
    auth_success        INTEGER,            -- 0|1
    connect_time        TEXT,
    disconnect_time     TEXT,
    duration_seconds    INTEGER,
    command_count       INTEGER,
    high_interest       INTEGER,            -- 0|1
    high_interest_reason TEXT,
    sophistication_score INTEGER,           -- 1-10
    country             TEXT,
    city                TEXT,
    asn                 TEXT,
    isp                 TEXT,
    is_vpn              INTEGER,
    is_cloud            INTEGER,
    abuse_confidence    INTEGER,            -- 0-100
    rdns                TEXT,
    mitre_techniques    TEXT                -- JSON array
);

-- commands: one row per shell command
CREATE TABLE commands (
    id          INTEGER PRIMARY KEY,
    session_id  TEXT,
    command     TEXT,
    timestamp   TEXT
);

-- credential_attempts: all auth tries
CREATE TABLE credential_attempts (
    id          INTEGER PRIMARY KEY,
    session_id  TEXT,
    peer_ip     TEXT,
    service     TEXT,
    username    TEXT,
    password    TEXT,
    timestamp   TEXT
);
```

## API Reference

Both nodes expose the same REST API on port 8080:

| Endpoint | Description |
|----------|-------------|
| `GET /` | SOC dashboard HTML |
| `GET /api/stats` | Aggregate counts |
| `GET /api/sessions?limit=N` | Recent sessions |
| `GET /api/credentials` | Top credential pairs |
| `GET /api/countries` | Top attacking countries |
| `GET /api/asns` | Top attacking ASNs |
| `GET /api/services` | Breakdown by service |
| `GET /api/hourly` | Events per hour (24h) |
| `GET /api/mitre` | MITRE technique counts |
| `GET /api/high-interest` | High-interest sessions |
| `GET /api/sophistication` | Sophistication distribution |
| `GET /api/search` | **Live search** (ip, username, command, service, from, to) |
| `GET /api/events` | SSE stream for real-time updates |
