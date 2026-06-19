# Frequently Asked Questions

**Q: Is this legal to run?**

Yes — you're deploying intentionally vulnerable services on infrastructure you own. Attackers connect voluntarily. You're not hacking anyone; you're watching who tries to hack you. Check local laws, but honeypot operation is legal in the US, EU, and most jurisdictions when deployed on your own infrastructure.

---

**Q: Will this get my server compromised?**

The honeypot services are Python emulators — they don't run real Redis, MySQL, or SSH. There's no real data to steal and no real shell to escape from. The main risk is someone finding your management port (2223) and brute-forcing that — use a strong key-based auth and disable password auth on the HOST sshd.

---

**Q: How much traffic will I get?**

Within minutes of a public IP going live with port 22 open, you'll see SSH scan traffic. Redis (6379) and MongoDB (27017) attract bots within hours. RDP (3389) gets heavy scanner traffic within 24 hours. A typical day sees 500-5,000 auth attempts per node.

---

**Q: How do I query the data without KQL/Azure?**

The SQLite database at `./data/meridian_honeypot.db` is queryable with any SQLite client:

```bash
sqlite3 data/meridian_honeypot.db
sqlite> SELECT peer_ip, username, password, count(*) as cnt
        FROM credential_attempts
        GROUP BY username, password
        ORDER BY cnt DESC LIMIT 20;
```

Or use the `/api/search` endpoint:
```bash
curl "http://localhost:8080/api/search?command=wget"
```

---

**Q: Can I add my own fake services?**

Yes. Add a new listener in `honeypot/server.py`, log events via `db.py` and `logger.py`. The pattern is consistent across all services — pick any existing one as a template.

---

**Q: What does "high interest" mean?**

A session is flagged high-interest when it exhibits attacker behavior beyond basic credential stuffing:
- Got an authenticated shell
- Ran 5+ commands
- Attempted persistence (crontab, authorized_keys, ssh-keygen)
- Attempted privilege escalation (sudo)
- Attempted lateral movement (nmap of internal ranges, SSH to 10.x)
- Ran data exfiltration commands (wget to external IPs)

---

**Q: What's the sophistication score?**

1-10 scale scored by `mitre.py`:
- 1-2: Single credential attempt, no commands
- 3-4: Got a shell, ran basic recon (whoami, ls)
- 5-6: Multi-stage chain, persistence attempt, lateral movement try
- 7-8: Evasion, privilege escalation, custom tooling indicators
- 9-10: APT-level (rarely seen in honeypots)

---

**Q: What are the NorthStar synthetic documents?**

3,181 files representing 10 years of a fictional healthcare organization (NorthStar Regional Health Network). Includes HR records, patient files, IT docs, executive materials, and personal clutter. All PII is synthetic — SSNs use invalid 9XX prefixes, phones use 555 area codes, no real people. The files make the honeypot feel like a real system to attackers who enumerate the filesystem.

Run `docs/gen_northstar.py` to regenerate them (uses `random.seed(42)` for reproducibility).

---

**Q: How do I reset the data?**

```bash
docker compose down
rm -rf data/ logs/
docker compose up -d
```

---

**Q: Can I run both nodes on one VM?**

Yes — use different ports. Modify `docker-compose.yml` for the second node to use offset ports (e.g., RDP on 13389 instead of 3389). You'll get less realistic traffic since real scanners target standard ports, but it works for development.
