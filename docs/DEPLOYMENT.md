# Deployment Guide

## Prerequisites

- Two Linux VMs (Azure, AWS, GCP, or bare metal)
- Docker + Docker Compose installed on each
- Ports accessible from the internet (see NSG_rules.md)
- Git

## Step 1: Clone the Repo

```bash
git clone https://github.com/jennafrank/log-n-pacific-cyber-range.git
cd log-n-pacific-cyber-range
```

## Step 2: Deploy Meridian HR

```bash
cd honeypots/meridian-hr
cp .env.example .env
# Optionally add your AbuseIPDB API key to .env for enrichment
docker compose up -d --build
```

Verify it's running:
```bash
docker compose ps
docker compose logs -f
```

Dashboard: `http://YOUR_IP:8080`

## Step 3: Deploy Cascade Medical

On the second VM:
```bash
cd honeypots/cascade-medical
cp .env.example .env
docker compose up -d --build
```

Dashboard: `http://YOUR_IP:8080`

## Step 4: Configure the Unified Dashboard

The unified dashboard is served from Meridian's port 9090. You need to update the Cascade IP:

Edit `honeypots/meridian-hr/dashboard/templates/unified.html`:
```javascript
// Find this line near the top of the <script> block:
const CAS_BASE = 'http://20.246.106.71:8080';
// Replace with your Cascade Medical VM's public IP:
const CAS_BASE = 'http://YOUR_CASCADE_IP:8080';
```

Then restart Meridian:
```bash
docker compose restart
```

Unified dashboard: `http://YOUR_MERIDIAN_IP:9090`

## Step 5: Generate Synthetic Documents (Optional)

To add realistic-looking files to attract attackers:

```bash
python3 docs/gen_northstar.py
# Creates 3,181 files in /tmp/northstar/
# Copy to both VMs: scp -r /tmp/northstar/ user@VM:~/northstar-documents/
```

## Step 6: Enable AbuseIPDB Enrichment (Optional)

1. Sign up at https://www.abuseipdb.com (free tier: 1,000 checks/day)
2. Add your key to `.env`:
   ```
   ABUSEIPDB_API_KEY=your_key_here
   ```
3. Restart the container

## Updating

```bash
git pull origin main
docker compose down
docker compose up -d --build
```

## Data Persistence

- `./data/` — SQLite database (sessions, commands, credentials)
- `./logs/` — Raw JSONL event log

Both are volume-mounted and survive `docker compose restart`. They are **not** version-controlled (see .gitignore).
