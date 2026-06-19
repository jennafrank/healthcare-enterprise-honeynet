# Troubleshooting

## Dashboard shows "Loading..." and never loads

**Cause:** CDN dependencies (Chart.js, Bootstrap) failing, or Flask isn't running.

**Fix:**
```bash
docker compose logs app | grep -i error
docker compose ps  # check container is Up
curl http://localhost:8080/api/stats  # test API directly
```

If the API returns data but the browser shows nothing, check browser console for JS errors.

## Container starts but ports show `{}`

**Cause:** A port binding conflict. Most commonly, host Samba is using port 445.

**Fix:** Remove `- "445:445"` from `docker-compose.yml`:
```yaml
# Remove or comment out this line:
# - "445:445"
```
Then: `docker compose down && docker compose up -d`

Verify: `docker inspect <container_name> | grep -A5 '"Ports"'`

## Port 8080 unreachable from browser

**Cause:** Azure NSG blocking inbound traffic.

**Fix:** In Azure Portal → VM → Networking → Add inbound rule:
- Port: 8080
- Protocol: TCP
- Source: Your IP (or Any for testing)
- Action: Allow

## SSH to management port fails

If you've exposed port 22 to the internet as a honeypot, you need a separate management port:
```bash
# Add to /etc/ssh/sshd_config on the HOST (not container):
Port 2223
# Then restart: sudo systemctl restart sshd
```

## Unified dashboard can't reach Cascade

**Cause:** CORS or the Cascade IP hasn't been updated in unified.html.

**Check:** Open browser DevTools → Network tab → look for failed requests to `20.246.106.71:8080`

**Fix:** Verify Cascade's `/api/stats` is reachable:
```bash
curl http://YOUR_CASCADE_IP:8080/api/stats
```

If unreachable, check Cascade's NSG rules (port 8080 must allow your Meridian VM's IP).

## Container loses files after `docker compose down`

Only these directories are volume-mounted (persistent):
- `./data/` — database
- `./logs/` — event logs
- `./dashboard/templates/` — HTML templates

Any files docker-cp'd directly into the container are lost on `down`. To make changes permanent, either:
1. Edit files on the host and volume-mount them, or
2. Rebuild the image: `docker compose up -d --build`

## AbuseIPDB not enriching

- Check your API key in `.env`
- Free tier limit is 1,000 checks/day — may be exhausted
- Check: `docker compose logs app | grep -i abuse`

## Kerberos/LDAP not appearing in sessions

These services use raw TCP and may be blocked by some ISPs. Verify:
```bash
docker compose exec honeypot ss -tlnp | grep -E '88|389'
```

## SQLite "database is locked"

The honeypot uses WAL mode to handle concurrent writes. If you see this error:
```bash
docker compose restart
```

If it persists, the WAL file may be corrupt:
```bash
# Backup first!
cp data/meridian_honeypot.db data/meridian_honeypot.db.bak
sqlite3 data/meridian_honeypot.db "PRAGMA integrity_check;"
```
