"""
MITRE ATT&CK Auto-Tagger — Meridian Honeypot
Tags sessions with relevant ATT&CK techniques based on observed commands/behavior.
Covers all four services: SSH, MySQL, Redis, MongoDB.
"""

import re
from typing import List, Tuple

# (regex pattern, technique_id, technique_name, description)
RULES: List[Tuple[str, str, str, str]] = [
    # Initial Access / Credential Access
    (r"(brute|hydra|medusa|ncrack|spray)", "T1110", "Brute Force", "Credential brute force tool detected"),
    (r"cat\s+/etc/shadow", "T1003.008", "OS Credential Dumping: /etc/shadow", "Shadow file read"),
    (r"cat\s+/etc/passwd", "T1003", "OS Credential Dumping", "Password file read"),
    (r"\[MySQL\].*users", "T1003", "OS Credential Dumping", "MySQL users table queried"),
    (r"\[MySQL\].*password", "T1003", "OS Credential Dumping", "MySQL password hash access"),
    (r"\[Redis\].*KEYS", "T1552.001", "Credentials in Files", "Redis key enumeration"),
    (r"\[Redis\].*GET.*(secret|password|jwt|token|key)", "T1552.001", "Credentials in Files", "Redis sensitive key access"),
    (r"(cat|grep|find).*(db\.conf|config|\.env|credentials|secret|password)", "T1552.001", "Credentials in Files", "Credential file access"),
    (r"env|printenv", "T1552.001", "Credentials in Files", "Environment variable dump (may contain creds)"),
    (r"\[MongoDB\].*api_keys", "T1552.001", "Credentials in Files", "MongoDB API keys collection accessed"),
    (r"cat.*/home/\w+/notes", "T1552.001", "Credentials in Files", "Notes file read (contained SFTP creds)"),

    # Discovery
    (r"(nmap|masscan|zmap|shodan)", "T1046", "Network Service Discovery", "Network scanner detected"),
    (r"netstat|ss -|ip\s+addr|ifconfig", "T1049", "System Network Connections Discovery", "Network connection enumeration"),
    (r"ps\s+(aux|ef)|top|htop", "T1057", "Process Discovery", "Process list enumeration"),
    (r"(show databases|show tables|\[MongoDB\] find)", "T1083", "File and Directory Discovery", "Database enumeration"),
    (r"(ls\s+-|find\s+/|locate\s+)", "T1083", "File and Directory Discovery", "File system enumeration"),
    (r"(uname|/etc/os-release|lscpu|free|df)", "T1082", "System Information Discovery", "System info gathered"),
    (r"(id|whoami|groups)", "T1033", "System Owner/User Discovery", "User identity checked"),
    (r"(crontab -l|cat /etc/cron)", "T1053.003", "Scheduled Task/Job: Cron", "Cron job enumeration"),
    (r"cat.*/etc/hosts", "T1016", "System Network Configuration Discovery", "Hosts file read"),
    (r"\[Redis\] INFO", "T1082", "System Information Discovery", "Redis server info gathered"),
    (r"\[MySQL\].*@@version|select version", "T1082", "System Information Discovery", "MySQL version fingerprinted"),

    # Credential Access (specific)
    (r"\[MySQL\].*ssn", "T1555", "Credentials from Password Stores", "SSN/PII table accessed in MySQL"),
    (r"\[MongoDB\].*w2_documents", "T1555", "Credentials from Password Stores", "W-2 documents accessed in MongoDB"),
    (r"cat.*/etc/mysql|debian\.cnf", "T1552.001", "Credentials in Files", "MySQL credential file read"),
    (r"\[Redis\] CONFIG SET", "T1562.001", "Impair Defenses", "Redis config rewrite attempt (potential RCE vector)"),
    (r"\[Redis\] (SLAVEOF|REPLICAOF)", "T1190", "Exploit Public-Facing Application", "Redis replication abuse attempt"),

    # Lateral Movement
    (r"ssh\s+([\d\.]+|[\w\-\.]+@)", "T1021.004", "Remote Services: SSH", "SSH lateral movement attempt"),
    (r"scp\s+", "T1021.004", "Remote Services: SSH", "SCP file transfer (possible exfil or lateral)"),
    (r"\[MySQL\].*LOAD DATA|INTO OUTFILE|INTO DUMPFILE", "T1005", "Data from Local System", "MySQL file read/write RCE attempt"),

    # Execution
    (r"(python|python3|perl|ruby|php)\s+", "T1059", "Command and Scripting Interpreter", "Scripting interpreter invoked"),
    (r"nc\s+|netcat|ncat", "T1059.004", "Unix Shell", "Netcat invoked (possible reverse shell)"),
    (r"/dev/tcp/", "T1059.004", "Unix Shell", "Bash /dev/tcp reverse shell attempt"),
    (r"xp_cmdshell|exec\s+xp_", "T1059.003", "Windows Command Shell", "SQL Server command execution attempt"),
    (r"\[MySQL\] xp_cmdshell", "T1190", "Exploit Public-Facing Application", "MySQL command injection attempt"),

    # Persistence
    (r"crontab\s+-e|echo.*crontab|>/etc/cron", "T1053.003", "Scheduled Task/Job: Cron", "Cron modification attempt"),
    (r"(adduser|useradd|usermod)\s+", "T1136.001", "Create Account: Local Account", "Account creation attempt"),
    (r"(ssh-keygen|authorized_keys)", "T1098.004", "SSH Authorized Keys", "SSH key persistence attempt"),
    (r"systemctl\s+(enable|start)\s+", "T1543.002", "Create or Modify System Process: Systemd Service", "Systemd persistence attempt"),
    (r"(screen|tmux)\s+", "T1059.004", "Unix Shell", "Terminal multiplexer for persistence"),
    (r"\[Redis\] SET", "T1059", "Command and Scripting Interpreter", "Redis write — possible webshell persistence vector"),

    # Privilege Escalation
    (r"sudo\s+(su|bash|sh|-i)", "T1548.003", "Sudo and Sudo Caching", "Sudo escalation attempt"),
    (r"^su(\s|$)", "T1548.003", "Sudo and Sudo Caching", "Su escalation"),
    (r"(SUID|chmod [+]s|chmod\s+4[0-9]{3})", "T1548.001", "Setuid and Setgid", "SUID bit manipulation"),
    (r"chmod\s+\+x", "T1222.002", "File and Directory Permissions Modification: Linux", "chmod +x on file"),

    # Defense Evasion
    (r"(export HISTFILE=/dev/null|HISTSIZE=0|unset HISTFILE)", "T1070.003", "Indicator Removal: Clear Command History", "Anti-forensics: history disabled"),
    (r"(shred|wipe|srm|rm\s+-rf.*/var/log)", "T1070.004", "Indicator Removal: File Deletion", "Log deletion attempt"),
    (r"(kill\s+\d+.*log|pkill.*log|stop.*syslog)", "T1562.001", "Impair Defenses: Disable or Modify Tools", "Logging service kill attempt"),

    # Exfiltration
    (r"(wget|curl)\s+http", "T1105", "Ingress Tool Transfer", "Tool download via wget/curl"),
    (r"(scp|rsync|sftp).+@", "T1048", "Exfiltration Over Alternative Protocol", "SCP/SFTP exfil attempt"),
    (r"\[MySQL\] mysqldump", "T1005", "Data from Local System", "mysqldump data exfil attempt"),
    (r"\[MongoDB\] find.*employees|w2|contract", "T1530", "Data from Cloud Storage", "MongoDB sensitive data access"),

    # Impact
    (r"(DROP DATABASE|DROP TABLE|TRUNCATE|DELETE FROM)", "T1485", "Data Destruction", "Destructive SQL query"),
    (r"\[MongoDB\].*(drop|dropDatabase|deleteMany)", "T1485", "Data Destruction", "MongoDB destructive command"),
    (r"\[Redis\].*(FLUSHALL|FLUSHDB)", "T1485", "Data Destruction", "Redis flush — data destruction"),
    (r"rm\s+-rf\s+/", "T1485", "Data Destruction", "rm -rf / destructive command"),

    # Cloud / IMDS
    (r"169\.254\.169\.254", "T1552.005", "Cloud Instance Metadata API", "IMDS metadata endpoint probed"),
    (r"(aws|gcloud|az)\s+", "T1526", "Cloud Service Discovery", "Cloud CLI invoked"),
]


def tag_session(commands: List[str]) -> List[dict]:
    """
    Run all commands against MITRE rules.
    Returns deduplicated list of triggered techniques.
    """
    seen = set()
    results = []
    full_text = "\n".join(commands).lower()

    for pattern, tid, tname, desc in RULES:
        if tid in seen:
            continue
        if re.search(pattern, full_text, re.IGNORECASE):
            seen.add(tid)
            results.append({
                "technique_id": tid,
                "technique_name": tname,
                "description": desc,
            })

    return results


def score_sophistication(commands: List[str], techniques: List[dict]) -> int:
    """
    1–10 sophistication score per session.
    Higher = more deliberate, targeted, technique-diverse attacker.
    """
    score = 1
    cmd_text = " ".join(commands).lower()

    # Points for volume
    if len(commands) >= 5:
        score += 1
    if len(commands) >= 15:
        score += 1

    # Points for technique diversity
    score += min(3, len(techniques) // 2)

    # Bonus for specific advanced behaviors
    if "histfile=/dev/null" in cmd_text or "histsize=0" in cmd_text:
        score += 1  # anti-forensics
    if "/dev/tcp/" in cmd_text:
        score += 1  # bash reverse shell
    if "169.254.169.254" in cmd_text:
        score += 1  # cloud IMDS probe
    if "config set" in cmd_text and "redis" in cmd_text:
        score += 1  # Redis RCE attempt
    if any(x in cmd_text for x in ["slaveof", "replicaof"]):
        score += 1  # Redis replication abuse
    if "load data" in cmd_text or "into outfile" in cmd_text:
        score += 1  # MySQL file RCE
    if len(set(commands)) / max(len(commands), 1) > 0.8:
        score += 1  # low repetition = deliberate

    return min(10, score)
