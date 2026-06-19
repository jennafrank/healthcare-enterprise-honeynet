"""
FakeShell — Cascade Medical Center
Hospital Linux server: cascade-emr-prod-01
Running Epic EMR backend, clinical systems, medical device interfaces.
No Easter eggs. Pure observation.
"""

import asyncio
import random
import time
from datetime import datetime, timedelta

FAKE_HOSTNAME = "cascade-emr-prod-01"
FAKE_KERNEL = "Linux cascade-emr-prod-01 5.15.0-107-generic #117-Ubuntu SMP Mon Apr 29 07:40:38 UTC 2024 x86_64"
DOMAIN = "cascademedical.local"
MERIDIAN_IP = "10.3.0.18"   # Meridian HR VM — real private IP (update at deploy time)

MOTD = """\r
Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-107-generic x86_64)\r
\r
 *** Cascade Medical Center — EMR Production Server ***\r
 *** AUTHORIZED ACCESS ONLY. All sessions monitored. ***\r
 *** IT Security: security@cascademedical.internal   ***\r
\r
  System load:  0.{load}         Processes: {procs}\r
  Memory usage: {mem}%            IP:        10.0.0.{ip}\r
  Disk /:       {disk}% of {disksize}GB\r
\r
Last login: {last_login} from 10.0.0.{last_ip}\r
Epic EMR services: RUNNING | HL7 bridge: RUNNING | PACS link: RUNNING\r
\r
"""

FAKE_PROCESSES = """USER         PID %CPU %MEM    VSZ    RSS TTY   STAT START   TIME COMMAND
root           1  0.0  0.1  170124 11400 ?     Ss   May12   3:11 /sbin/init
epic        1204  1.8 18.4 8421304 749812 ?    Ssl  May12 884:22 /opt/epic/bin/epicd --config /etc/epic/prod.conf
mysql       1388  0.6 12.1 2841204 493120 ?    Ssl  May12 301:44 /usr/sbin/mysqld
mssql       1492  0.8  9.3 1924048 378944 ?    Ssl  May12 218:33 /opt/mssql/bin/sqlservr
elasticsearch 1601 0.4 11.2 4821048 456012 ? Sl  May12 144:21 /usr/share/elasticsearch/bin/elasticsearch
hl7         1712  0.1  1.4  312048  57344 ?    S    May12  44:12 python3 /opt/cascade/hl7/bridge.py
pacs        1821  0.2  2.1  481024  85444 ?    S    May12  88:04 java -jar /opt/pacs/merge-pacs.jar
root        2201  0.0  0.2  224556  8144 ?     S    May12   8:44 /usr/sbin/sshd -D
root        2304  0.0  0.1  168444  6144 ?     S    Jun03   0:12 /usr/sbin/crond
clinadm     3301  0.0  0.4  312048 17244 pts/0  S    08:14   0:02 -bash
"""

FAKE_NETSTAT = """Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:23              0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:443             0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:1433            0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:2575            0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:3389            0.0.0.0:*               LISTEN
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:5900            0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:8080            0.0.0.0:*               LISTEN
tcp        0      0 0.0.0.0:9200            0.0.0.0:*               LISTEN
"""

FAKE_HOSTS = f"""127.0.0.1   localhost
127.0.1.1   cascade-emr-prod-01
10.0.0.4    meridian-hrprod-01 meridian-hrprod-01.meridianhr.local
10.0.0.5    cascade-emr-prod-01 cascade-emr-prod-01.cascademedical.local
10.0.0.10   cascade-dc01 dc01.cascademedical.local
10.0.0.11   cascade-db-primary epic-db-prod
10.0.0.12   cascade-pacs pacs-prod
10.0.0.13   cascade-backup backup01
10.0.0.20   cascade-fs01 fs01
10.0.0.100  cascade-mgmt-01
"""

FAKE_HISTORY = [
    "sudo systemctl status epic",
    "tail -f /var/log/epic/epicd.log",
    "mysql -u epic_admin -p epic_emr",
    "sqlcmd -S localhost -U sa -P 'Casc@de_MSSQL_2024!'",
    "curl -X GET http://localhost:9200/_cluster/health",
    "curl -X GET http://localhost:9200/_cat/indices",
    "cd /opt/epic/bin && ./epicd status",
    "cat /etc/epic/prod.conf",
    "ls -la /opt/cascade/",
    "python3 /opt/cascade/hl7/bridge.py --test",
    "ssh clinadm@10.0.0.10",
    "scp patient_export.csv backup01:/backup/daily/",
    "grep -r 'ERROR' /var/log/epic/ | tail -50",
    "df -h",
    "free -m",
    "ps aux | grep epic",
    "systemctl restart hl7-bridge",
    "cat /opt/cascade/config/db.conf",
    "openssl s_client -connect pacs-prod:443",
    "netstat -tlnp | grep LISTEN",
]

FAKE_DB_CONF = """[epic_database]
host     = 10.0.0.11
port     = 3306
name     = epic_emr
user     = epic_app
password = Ep1c@CMC_Pr0d_2024!
pool     = 50

[mssql]
host     = localhost
port     = 1433
user     = sa
password = Casc@de_MSSQL_2024!
database = CascadeEMR

[elasticsearch]
host     = localhost
port     = 9200
user     = elastic
password = El@stic_CMC2024!
index    = patients,labs,radiology,pharmacy

[hl7_bridge]
listen_port = 2575
target_host = epic-db-prod
target_port = 2576
auth_token  = HL7_Tok3n_CMC_Pr0d!

[pacs]
host     = 10.0.0.12
dicom_port = 104
web_port   = 8080
user     = svc_pacs
password = P@cs_Casc4de2024!
"""

FAKE_EPIC_CONF = """# Epic EMR Production Configuration
# Cascade Medical Center

[server]
instance     = CASCADE-PROD
environment  = production
port         = 8443
workers      = 16
log_level    = INFO
log_path     = /var/log/epic/

[database]
primary      = 10.0.0.11:3306
replica      = 10.0.0.11:3307
db_name      = epic_emr
db_user      = epic_app
db_pass      = Ep1c@CMC_Pr0d_2024!

[integrations]
hl7_host     = 0.0.0.0
hl7_port     = 2575
pacs_host    = 10.0.0.12
pacs_port    = 104

[auth]
ldap_server  = 10.0.0.10
ldap_base    = DC=cascademedical,DC=local
ldap_user    = svc_ldap
ldap_pass    = LDAP_Casc@de2024!
mfa_required = true
session_timeout = 900
"""

FAKE_SHADOW = [
    "root:$6$rounds=656000$CASCADE$hashed:19450:0:99999:7:::",
    "clinadm:$6$clin$hashed:19450:0:99999:7:::",
    "epic:$6$epic$hashed:19450:0:99999:7:::",
    "hl7svc:$6$hl7$hashed:19450:0:99999:7:::",
    "svc_backup:$6$bk$hashed:19450:0:99999:7:::",
]

FAKE_CRONTAB = """# Cascade Medical Center — Production Crontab
0 2 * * * /opt/cascade/scripts/db_backup.sh >> /var/log/backup.log 2>&1
0 3 * * * /opt/cascade/scripts/epic_cache_clear.sh
*/5 * * * * /opt/cascade/scripts/hl7_watchdog.sh
0 6 * * 1-5 python3 /opt/cascade/scripts/lab_sync.py
0 0 1 * * /opt/cascade/scripts/monthly_report.py
30 22 * * * /opt/cascade/scripts/pacs_cleanup.sh
0 4 * * 0 /opt/cascade/scripts/full_backup.sh
"""

FAKE_LS_OPT = """total 48
drwxr-xr-x 8 root    root    4096 May 12 14:00 .
drwxr-xr-x 4 root    root    4096 May 12 09:00 ..
drwxr-xr-x 6 epic    epic    4096 Jun  3 08:01 epic
drwxr-xr-x 4 clinadm clinadm 4096 May 30 11:22 cascade
drwxr-xr-x 3 pacs    pacs    4096 May 12 14:10 pacs
drwxr-xr-x 2 hl7svc  hl7svc  4096 Jun  2 22:01 hl7
drwxr-xr-x 3 mssql   mssql   4096 May 12 14:00 mssql
drwxr-xr-x 2 elastic elastic 4096 May 12 14:00 elasticsearch
"""

ELASTIC_INDICES = """{
  "health" : "green",
  "status" : "open",
  "index" : "patients",
  "uuid" : "abc123FAKE",
  "pri" : 3,
  "rep" : 1,
  "docs.count" : "48821",
  "docs.deleted" : "0",
  "store.size" : "2.4gb"
}
{
  "health" : "green",
  "status" : "open",
  "index" : "lab_results",
  "docs.count" : "182441",
  "store.size" : "8.1gb"
}
{
  "health" : "green",
  "status" : "open",
  "index" : "radiology_reports",
  "docs.count" : "29812",
  "store.size" : "1.8gb"
}
{
  "health" : "green",
  "status" : "open",
  "index" : "pharmacy_orders",
  "docs.count" : "94221",
  "store.size" : "3.2gb"
}"""

ELASTIC_PATIENT_HIT = """{
  "_index": "patients",
  "_id": "MRN-482821",
  "_source": {
    "mrn": "MRN-482821",
    "name": "Margaret Williams",
    "dob": "1958-04-12",
    "ssn": "***-**-4821",
    "insurance_id": "INS-88219944",
    "diagnosis": "Type 2 Diabetes Mellitus",
    "attending": "Dr. Sarah Chen",
    "admit_date": "2024-05-29"
  }
}"""


class FakeShell:
    def __init__(self, chan, session_id, username, db, hplogger):
        self.chan = chan
        self.session_id = session_id
        self.username = username
        self.db = db
        self.hplogger = hplogger
        self.cwd = f"/home/{username}"
        self.is_root = (username == "root")
        self.input_buffer = ""
        self.command_count = 0

    def motd(self):
        now = datetime.utcnow()
        last = now - timedelta(days=random.randint(1, 4), hours=random.randint(1, 10))
        return MOTD.format(
            load=random.randint(12, 55),
            procs=random.randint(210, 280),
            mem=random.randint(48, 78),
            ip=random.randint(5, 20),
            disk=random.randint(42, 68),
            disksize=random.choice([500, 1000, 2000]),
            last_login=last.strftime("%a %b %d %H:%M:%S %Y"),
            last_ip=random.randint(2, 50),
        )

    def prompt(self):
        user = "root" if self.is_root else self.username
        sym = "#" if self.is_root else "$"
        cwd = self.cwd.replace(f"/home/{self.username}", "~")
        return f"\r\n{user}@{FAKE_HOSTNAME}:{cwd}{sym} "

    async def handle_input(self, data):
        for char in data:
            if char in ("\r", "\n"):
                cmd = self.input_buffer.strip()
                self.input_buffer = ""
                if cmd:
                    self.chan.write("\r\n")
                    await self._dispatch(cmd)
                self.chan.write(self.prompt())
            elif char == "\x7f":
                if self.input_buffer:
                    self.input_buffer = self.input_buffer[:-1]
                    self.chan.write("\b \b")
            elif char == "\x03":
                self.input_buffer = ""
                self.chan.write("^C")
                self.chan.write(self.prompt())
            elif char == "\x04":
                self.chan.write("\r\nlogout\r\n")
                self.chan.close()
            else:
                self.input_buffer += char
                self.chan.write(char)

    async def _dispatch(self, raw):
        self.command_count += 1
        parts = raw.split()
        cmd = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        self.db.log_command(self.session_id, raw)
        self.hplogger.log_event("command", {
            "session_id": self.session_id,
            "command": raw,
            "command_number": self.command_count,
        })

        await asyncio.sleep(random.uniform(0.05, 0.2))

        handlers = {
            "ls": self._ls, "ll": self._ls, "dir": self._ls,
            "cd": self._cd, "pwd": self._pwd, "cat": self._cat,
            "whoami": self._whoami, "id": self._id,
            "hostname": self._hostname, "uname": self._uname,
            "ps": self._ps, "top": self._top, "htop": self._top,
            "netstat": self._netstat, "ss": self._netstat,
            "ifconfig": self._ifconfig, "ip": self._ip,
            "history": self._history, "env": self._env,
            "export": self._export, "echo": self._echo,
            "date": self._date, "uptime": self._uptime,
            "df": self._df, "free": self._free,
            "crontab": self._crontab,
            "wget": self._wget, "curl": self._curl,
            "chmod": self._chmod, "chown": self._noop,
            "find": self._find, "grep": self._grep,
            "mkdir": self._noop, "touch": self._noop,
            "rm": self._rm, "mv": self._noop, "cp": self._noop,
            "ssh": self._ssh, "scp": self._scp,
            "sudo": self._sudo, "su": self._su,
            "python3": self._python, "python": self._python,
            "perl": self._perl,
            "mysql": self._mysql, "mysqldump": self._mysqldump,
            "sqlcmd": self._sqlcmd, "osql": self._sqlcmd,
            "curl": self._curl,
            "systemctl": self._systemctl, "service": self._service,
            "apt": self._apt, "apt-get": self._apt, "yum": self._apt,
            "ping": self._ping, "nmap": self._nmap,
            "nc": self._nc, "netcat": self._nc,
            "telnet": self._telnet,
            "passwd": self._passwd,
            "adduser": self._adduser, "useradd": self._adduser,
            "screen": self._screen, "tmux": self._screen,
            "ssh-keygen": self._ssh_keygen,
            "lscpu": self._lscpu,
            "tar": self._tar, "zip": self._zip, "unzip": self._zip,
            "openssl": self._openssl,
            "xfreerdp": self._rdp, "rdesktop": self._rdp,
            "vncviewer": self._vnc,
            "kinit": self._kinit,
            "klist": self._klist,
            "ldapsearch": self._ldapsearch,
            "exit": self._exit, "logout": self._exit,
            "clear": self._clear, "help": self._help,
        }

        pipe_cmd = raw.split("|")[0].strip().split()[0] if "|" in raw else cmd
        handler = handlers.get(pipe_cmd) or handlers.get(cmd)
        if handler:
            await handler(args, raw)
        else:
            self.chan.write(f"-bash: {cmd}: command not found")

    # ─── Commands ─────────────────────────────────────────────────────────────

    async def _ls(self, args, raw):
        path = args[0] if args and not args[0].startswith("-") else self.cwd
        long = "-l" in raw or "-la" in raw or "ll" in raw.split()[0]
        if path in (".", self.cwd, f"/home/{self.username}", "~"):
            self.chan.write("logs  scripts  .bash_history  .ssh" if not long else
                "total 32\ndrwxr-x--- 4 clinadm clinadm 4096 Jun  3 08:14 .\n"
                "drwxr-xr-x 9 root    root    4096 May 12 14:00 ..\n"
                "drwx------ 2 clinadm clinadm 4096 May 12 14:02 .ssh\n"
                "-rw------- 1 clinadm clinadm 1204 Jun  3 08:14 .bash_history\n"
                "drwxr-xr-x 2 clinadm clinadm 4096 Jun  1 11:00 scripts\n"
                "drwxr-xr-x 2 clinadm clinadm 4096 Jun  3 07:00 logs")
        elif "/opt" in path or path == "/opt":
            self.chan.write(FAKE_LS_OPT if long else "cascade  elasticsearch  epic  hl7  mssql  pacs")
        elif "/opt/cascade" in path:
            self.chan.write("config  hl7  logs  reports  scripts  uploads" if not long else
                "drwxr-xr-x 2 clinadm clinadm 4096 Jun  2 11:22 config\n"
                "drwxr-xr-x 2 hl7svc  hl7svc  4096 Jun  3 22:01 hl7\n"
                "drwxrwxr-x 2 clinadm clinadm 4096 Jun  3 08:01 logs\n"
                "drwxr-x--- 2 clinadm clinadm 4096 Jun  1 16:00 reports\n"
                "drwxr-xr-x 3 clinadm clinadm 4096 May 12 14:05 scripts\n"
                "drwxrwxr-x 2 clinadm clinadm 4096 Jun  3 07:44 uploads")
        elif "/opt/cascade/config" in path:
            self.chan.write("db.conf  epic.conf  hl7.conf  smtp.conf  ldap.conf")
        elif "/etc" in path:
            self.chan.write("hosts  hostname  passwd  shadow  crontab  ssh  mysql  epic  mssql  elasticsearch")
        elif "/var/log" in path:
            self.chan.write("auth.log  syslog  epic  mysql  mssql  elasticsearch  nginx  cascade.log  backup.log")
        elif "/backup" in path or "Backup" in path:
            self.chan.write("epic_emr_db_20240603.sql.gz  epic_emr_db_20240602.sql.gz  cascade_hr_20240603.sql.gz  config_backup_20240603.tar.gz")
        else:
            self.chan.write(f"ls: cannot access '{path}': No such file or directory")

    async def _cd(self, args, raw):
        if not args or args[0] in ("~", f"/home/{self.username}"):
            self.cwd = f"/home/{self.username}"
        elif args[0].startswith("/"):
            self.cwd = args[0]
        elif args[0] == "..":
            self.cwd = self.cwd.rstrip("/").rsplit("/", 1)[0] or "/"
        else:
            self.cwd = f"{self.cwd.rstrip('/')}/{args[0]}"

    async def _pwd(self, args, raw):
        self.chan.write(self.cwd)

    async def _cat(self, args, raw):
        if not args:
            self.chan.write("cat: missing operand"); return
        target = " ".join(args)
        if not target.startswith("/"):
            target = f"{self.cwd.rstrip('/')}/{target}"

        if "passwd" in target and "shadow" not in target:
            self.chan.write("root:x:0:0:root:/root:/bin/bash\nclinadm:x:1000:1000::/home/clinadm:/bin/bash\n"
                "epic:x:1001:1001::/home/epic:/bin/bash\nhl7svc:x:1002:1002::/home/hl7svc:/usr/sbin/nologin\n"
                "svc_backup:x:1003:1003::/home/svc_backup:/usr/sbin/nologin\n"
                "mssql:x:999:999::/var/opt/mssql:/bin/bash\nelastic:x:998:998::/home/elastic:/bin/bash")
        elif "shadow" in target:
            if not self.is_root:
                self.chan.write("cat: /etc/shadow: Permission denied")
            else:
                self.chan.write("\n".join(FAKE_SHADOW))
                self.db.flag_high_interest(self.session_id, "cat /etc/shadow as root — T1003.008")
        elif "db.conf" in target or ("config" in target and "db" in target):
            self.chan.write(FAKE_DB_CONF)
            self.db.flag_high_interest(self.session_id, "cat db.conf — ALL service credentials exposed")
        elif "epic.conf" in target:
            self.chan.write(FAKE_EPIC_CONF)
            self.db.flag_high_interest(self.session_id, "cat epic.conf — Epic EMR + LDAP credentials")
        elif "hosts" in target:
            self.chan.write(FAKE_HOSTS)
            self.db.flag_high_interest(self.session_id, "cat /etc/hosts — internal network topology revealed including Meridian HR IP")
        elif "auth.log" in target:
            self._write_fake_auth_log()
        elif "crontab" in target:
            self.chan.write(FAKE_CRONTAB)
        elif "bash_history" in target or ".history" in target:
            self.chan.write("\n".join(f"  {i+1}  {c}" for i, c in enumerate(FAKE_HISTORY)))
            self.db.flag_high_interest(self.session_id, "cat .bash_history — command history with credentials visible")
        else:
            self.chan.write(f"cat: {target}: No such file or directory")

    def _write_fake_auth_log(self):
        now = datetime.utcnow()
        lines = []
        for i in range(15):
            t = now - timedelta(minutes=i * random.randint(2, 10))
            ts = t.strftime("%b %d %H:%M:%S")
            ip = f"{random.choice(['192.168','10.0'])}.{random.randint(0,255)}.{random.randint(1,254)}"
            lines.append(f"{ts} cascade-emr-prod-01 sshd[{random.randint(2000,9999)}]: "
                         f"Failed password for invalid user {random.choice(['admin','root','epic','test'])} from {ip}")
        lines.append(f"{now.strftime('%b %d %H:%M:%S')} cascade-emr-prod-01 sshd[3301]: Accepted password for clinadm from 10.0.0.100 port 54022")
        self.chan.write("\r\n".join(reversed(lines)))

    async def _whoami(self, args, raw):
        self.chan.write("root" if self.is_root else self.username)

    async def _id(self, args, raw):
        if self.is_root:
            self.chan.write("uid=0(root) gid=0(root) groups=0(root)")
        else:
            self.chan.write(f"uid=1000({self.username}) gid=1000({self.username}) groups=1000({self.username}),4(adm),27(sudo)")

    async def _hostname(self, args, raw): self.chan.write(FAKE_HOSTNAME)
    async def _uname(self, args, raw):
        self.chan.write(FAKE_KERNEL if "-a" in raw else "Linux")

    async def _ps(self, args, raw): self.chan.write(FAKE_PROCESSES)
    async def _top(self, args, raw):
        self.chan.write("[top/htop not available — use 'ps aux' for process list]")

    async def _netstat(self, args, raw): self.chan.write(FAKE_NETSTAT)

    async def _ifconfig(self, args, raw):
        self.chan.write("eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\r\n"
            "        inet 10.0.0.5  netmask 255.255.255.0  broadcast 10.0.0.255\r\n"
            "        inet6 fe80::20d:3aff:fe4b:dddd  prefixlen 64\r\n"
            "        ether 00:0d:3a:4b:dd:dd  txqueuelen 1000\r\n")

    async def _ip(self, args, raw):
        if "addr" in raw or ("a" in args and len(args) == 1):
            await self._ifconfig(args, raw)
        elif "route" in raw or "r" in args:
            self.chan.write("default via 10.0.0.1 dev eth0 proto dhcp src 10.0.0.5 metric 100\r\n"
                "10.0.0.0/24 dev eth0 proto kernel scope link src 10.0.0.5")
        else:
            self.chan.write("Usage: ip [addr|route|link]")

    async def _history(self, args, raw):
        self.chan.write("\r\n".join(f"  {i+1}  {c}" for i, c in enumerate(FAKE_HISTORY)))

    async def _env(self, args, raw):
        self.chan.write(
            f"SHELL=/bin/bash\r\nTERM=xterm-256color\r\nUSER={self.username}\r\n"
            "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\r\n"
            "EPIC_HOME=/opt/epic\r\nEPIC_ENV=production\r\n"
            "DB_HOST=10.0.0.11\r\nDB_NAME=epic_emr\r\n"
            "DB_PASS=Ep1c@CMC_Pr0d_2024!\r\n"
            "MSSQL_SA_PASSWORD=Casc@de_MSSQL_2024!\r\n"
            "ELASTIC_PASSWORD=El@stic_CMC2024!\r\n"
            "HL7_TOKEN=HL7_Tok3n_CMC_Pr0d!\r\n"
            "LDAP_BIND_PASS=LDAP_Casc@de2024!\r\n"
        )
        self.db.flag_high_interest(self.session_id, "env — ALL service credentials in environment variables")

    async def _export(self, args, raw):
        if "HISTFILE=/dev/null" in raw or "HISTSIZE=0" in raw:
            self.db.flag_high_interest(self.session_id, f"anti-forensics: {raw} — T1070.003")

    async def _echo(self, args, raw):
        self.chan.write(raw[5:].strip().strip('"').strip("'") if raw.startswith("echo") else "")

    async def _date(self, args, raw):
        self.chan.write(datetime.utcnow().strftime("%a %b %d %H:%M:%S UTC %Y"))

    async def _uptime(self, args, raw):
        self.chan.write(f" {datetime.utcnow().strftime('%H:%M:%S')} up {random.randint(40,200)} days, "
            f"{random.randint(1,23)}:{random.randint(10,59)},  1 user,  load average: 0.{random.randint(15,55)}, 0.{random.randint(10,45)}, 0.{random.randint(10,45)}")

    async def _df(self, args, raw):
        self.chan.write("Filesystem      Size  Used Avail Use% Mounted on\r\n"
            "/dev/sda1       500G  214G  266G  45% /\r\n"
            "tmpfs            16G  2.1G   14G  14% /dev/shm\r\n"
            "/dev/sdb1       2.0T  1.1T  900G  56% /var/lib/epic\r\n"
            "/dev/sdc1       4.0T  2.8T  1.2T  71% /backup\r\n")

    async def _free(self, args, raw):
        self.chan.write("               total        used        free      shared  buff/cache   available\r\n"
            "Mem:        32768000    24847232     1923040      224512     6013728     7049024\r\n"
            "Swap:        8192000      102400     8089600")

    async def _crontab(self, args, raw):
        if "-l" in args:
            self.chan.write(FAKE_CRONTAB)
        elif "-e" in args:
            self.chan.write("[editor not available in this session]")
        else:
            self.chan.write(FAKE_CRONTAB)

    async def _wget(self, args, raw):
        if not args or args[0].startswith("-"):
            self.chan.write("wget: missing URL"); return
        url = args[-1]
        self.db.flag_high_interest(self.session_id, f"wget ingress tool transfer: {url} — T1105")
        self.chan.write(f"--{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}--  {url}\r\n")
        await asyncio.sleep(1.5)
        self.chan.write("wget: unable to resolve host — outbound connections restricted by firewall policy")

    async def _curl(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"curl: {raw}")
        if "169.254.169.254" in raw:
            self.chan.write('{"compute":{"name":"cascade-emr-prod-01","location":"eastus","vmSize":"Standard_B2ms"}}')
            self.db.flag_high_interest(self.session_id, "CRITICAL: Azure IMDS metadata probed — T1552.005")
        elif "9200" in raw or "elasticsearch" in raw.lower():
            if "_cat/indices" in raw:
                self.chan.write(ELASTIC_INDICES)
                self.db.flag_high_interest(self.session_id, "Elasticsearch index enumeration via curl — T1083")
            elif "_search" in raw or "patients" in raw:
                self.chan.write(ELASTIC_PATIENT_HIT)
                self.db.flag_high_interest(self.session_id, "CRITICAL: Elasticsearch patient data query — T1530")
            elif "_cluster" in raw:
                self.chan.write('{"cluster_name":"cascade-medical","status":"green","number_of_nodes":1}')
            else:
                self.chan.write('{"acknowledged":true}')
        else:
            self.chan.write("curl: (7) Failed to connect: Connection refused")

    async def _chmod(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"chmod: {raw} — T1222.002")

    async def _noop(self, args, raw): self.chan.write("")

    async def _find(self, args, raw):
        if any(kw in raw.lower() for kw in ["password","passwd","secret","key","cred","token","conf"]):
            self.db.flag_high_interest(self.session_id, f"find credential search: {raw} — T1552.001")
            await asyncio.sleep(1.5)
            self.chan.write("/opt/cascade/config/db.conf\r\n/opt/cascade/config/epic.conf\r\n"
                "/opt/cascade/config/ldap.conf\r\n/home/clinadm/.bash_history\r\n"
                "/etc/mysql/debian.cnf\r\n/opt/mssql/secrets/mssql.conf\r\n"
                "/var/opt/mssql/mssql.conf")
        elif ".ssh" in raw or "id_rsa" in raw:
            self.db.flag_high_interest(self.session_id, f"find SSH key search: {raw} — T1552.004")
            self.chan.write("/home/clinadm/.ssh/id_rsa\r\n/home/clinadm/.ssh/authorized_keys\r\n/root/.ssh/authorized_keys")
        else:
            await asyncio.sleep(0.8)
            self.chan.write("")

    async def _grep(self, args, raw):
        if any(kw in raw.lower() for kw in ["password","pass","secret","token","key"]):
            self.db.flag_high_interest(self.session_id, f"grep credential search: {raw} — T1552.001")
        self.chan.write("")

    async def _rm(self, args, raw):
        if "-rf" in raw:
            self.db.flag_high_interest(self.session_id, f"rm -rf: {raw} — T1485 Data Destruction")

    async def _ssh(self, args, raw):
        if args:
            target = args[0] if not args[0].startswith("-") else (args[1] if len(args) > 1 else "unknown")
            self.db.flag_high_interest(self.session_id,
                f"lateral movement SSH attempt: {target} — T1021.004" +
                (" [MERIDIAN HR VM — cross-honeypot lateral movement!]" if MERIDIAN_IP in raw else ""))
        self.chan.write("ssh: connect to host: Network unreachable")

    async def _scp(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"scp exfil attempt: {raw} — T1048")
        self.chan.write("scp: Connection closed")

    async def _sudo(self, args, raw):
        if args and args[0] in ("su", "bash", "sh", "-i", "-s"):
            self.is_root = True
            self.db.flag_high_interest(self.session_id, f"sudo escalation: {raw} — T1548.003")
        elif args:
            self.is_root = True
            await self._dispatch(" ".join(args))

    async def _su(self, args, raw):
        await asyncio.sleep(0.8)
        self.is_root = True
        self.db.flag_high_interest(self.session_id, "su escalation — T1548.003")
        self.chan.write(f"Password: \r\nroot@{FAKE_HOSTNAME}:{self.cwd}# ")

    async def _python(self, args, raw):
        self.chan.write("Python 3.10.12 (main, Nov 20 2023, 15:14:05)\r\n"
            '[GCC 11.4.0] on linux\r\nType "help" for more information.\r\n>>> ')
        await asyncio.sleep(60)

    async def _perl(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"perl interpreter: {raw} — T1059")
        self.chan.write("")

    async def _mysql(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"mysql client: {raw} — T1003")
        await asyncio.sleep(1.0)
        if "-p" in raw or "--password" in raw or "Ep1c" in raw:
            self.chan.write("Welcome to the MySQL monitor.\r\nMySQL [epic_emr]> ")
            await asyncio.sleep(60)
        else:
            self.chan.write("ERROR 1045 (28000): Access denied (using password: NO)")

    async def _mysqldump(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"mysqldump exfil: {raw} — T1005")
        await asyncio.sleep(2.0)
        self.chan.write("mysqldump: Got error: 1044: Access denied for user to database 'epic_emr'")

    async def _sqlcmd(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"MSSQL client: {raw} — T1003")
        await asyncio.sleep(1.2)
        if "-P" in raw or "Casc@de" in raw:
            self.chan.write("1> ")  # MSSQL prompt
            await asyncio.sleep(60)
        else:
            self.chan.write("Sqlcmd: Error: Microsoft ODBC Driver: Login failed for user 'sa'.")

    async def _systemctl(self, args, raw):
        if not args:
            self.chan.write("No unit specified."); return
        action, unit = args[0], (args[1] if len(args) > 1 else "")
        if action == "status":
            self.chan.write(f"● {unit} - Service\r\n   Active: active (running) since May 12\r\n   PID: {random.randint(800,4000)}")
        elif action in ("stop", "disable", "kill"):
            self.db.flag_high_interest(self.session_id, f"systemctl {action} {unit} — T1489 Service Stop")
            self.chan.write(f"Failed to {action} {unit}: Access denied")
        else:
            self.chan.write("")

    async def _service(self, args, raw):
        await self._systemctl(list(reversed(args)), raw)

    async def _apt(self, args, raw):
        await asyncio.sleep(0.8)
        self.chan.write("E: Could not open lock file /var/lib/dpkg/lock-frontend (13: Permission denied)")

    async def _ping(self, args, raw):
        target = args[0] if args else "localhost"
        if MERIDIAN_IP in raw or "meridian" in raw.lower():
            self.db.flag_high_interest(self.session_id,
                f"ping to Meridian HR VM ({MERIDIAN_IP}) — cross-honeypot recon T1018")
            await asyncio.sleep(1.0)
            self.chan.write(f"PING {target} ({MERIDIAN_IP}): 56 data bytes\r\n"
                f"64 bytes from {MERIDIAN_IP}: icmp_seq=0 ttl=64 time=0.842 ms\r\n"
                f"64 bytes from {MERIDIAN_IP}: icmp_seq=1 ttl=64 time=0.731 ms\r\n"
                f"--- {target} ping statistics ---\r\n2 packets transmitted, 2 received, 0% packet loss")
        elif "10.0.0" in raw:
            await asyncio.sleep(1.0)
            self.chan.write(f"PING {target}: 56 data bytes\r\n64 bytes from {target}: icmp_seq=0 ttl=64 time=1.24 ms")
        else:
            self.chan.write(f"PING {target}: Network unreachable")

    async def _nmap(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"nmap network scan: {raw} — T1046")
        await asyncio.sleep(3.0)
        if MERIDIAN_IP in raw or "10.0.0" in raw:
            self.db.flag_high_interest(self.session_id,
                "CRITICAL: nmap scan of internal network including Meridian HR VM — lateral movement recon T1018")
            self.chan.write(f"Starting Nmap 7.80\r\n"
                f"Nmap scan report for meridian-hrprod-01 ({MERIDIAN_IP})\r\n"
                f"Host is up (0.0008s latency).\r\n"
                f"PORT     STATE SERVICE\r\n"
                f"22/tcp   open  ssh\r\n"
                f"445/tcp  open  microsoft-ds\r\n"
                f"3306/tcp open  mysql\r\n"
                f"6379/tcp open  redis\r\n"
                f"Nmap done: 1 IP address (1 host up)")
        else:
            self.chan.write("Starting Nmap 7.80\r\nNote: Host seems down. Try -Pn\r\nNmap done: 0 hosts up")

    async def _nc(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"netcat: {raw} — possible reverse shell T1059.004")
        await asyncio.sleep(5.0)
        self.chan.write("(UNKNOWN) []: Connection timed out")

    async def _telnet(self, args, raw):
        target = args[0] if args else "unknown"
        self.db.flag_high_interest(self.session_id, f"telnet: {raw} — T1021")
        await asyncio.sleep(2.0)
        self.chan.write(f"Trying {target}...\r\ntelnet: Unable to connect to remote host: Connection timed out")

    async def _passwd(self, args, raw):
        self.chan.write(f"Changing password for {self.username}.\r\nCurrent password: ")
        await asyncio.sleep(1.0)
        self.chan.write("\r\nNew password: ")
        await asyncio.sleep(1.0)
        self.chan.write("\r\nRetype new password: \r\npasswd: password updated successfully")
        self.db.flag_high_interest(self.session_id, "passwd — T1098 credential manipulation")

    async def _adduser(self, args, raw):
        user = args[0] if args else "newuser"
        self.db.flag_high_interest(self.session_id, f"useradd {user} — T1136.001 Create Account")
        self.chan.write("useradd: Permission denied.")

    async def _screen(self, args, raw):
        self.db.flag_high_interest(self.session_id, "screen/tmux — persistence T1059.004")
        self.chan.write("[screen/tmux not available]")

    async def _ssh_keygen(self, args, raw):
        self.db.flag_high_interest(self.session_id, "ssh-keygen — persistence T1098.004")
        await asyncio.sleep(1.2)
        self.chan.write("Generating public/private rsa key pair.\r\n"
            "Enter file to save key (/home/clinadm/.ssh/id_rsa): \r\n"
            "/home/clinadm/.ssh/id_rsa already exists.\r\n"
            "Overwrite (y/n)? ")
        await asyncio.sleep(30)

    async def _lscpu(self, args, raw):
        self.chan.write("Architecture: x86_64\r\nCPU(s): 2\r\n"
            "Model name: Intel(R) Xeon(R) Platinum 8272CL CPU @ 2.60GHz\r\nCPU MHz: 2593.905")

    async def _tar(self, args, raw):
        if "-c" in raw or "--create" in raw:
            self.db.flag_high_interest(self.session_id, f"tar archive creation — possible staging T1560: {raw}")
        self.chan.write("")

    async def _zip(self, args, raw):
        if "zip" in raw.split()[0]:
            self.db.flag_high_interest(self.session_id, f"zip/unzip — T1560: {raw}")
        self.chan.write("")

    async def _openssl(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"openssl: {raw} — crypto tool")
        if "s_client" in raw:
            host = [a for a in args if "connect" not in a and "-" not in a]
            self.chan.write(f"CONNECTED(00000003)\r\nCertificate chain... [truncated]\r\nclosed")
        else:
            self.chan.write("")

    async def _rdp(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"RDP client: {raw} — T1021.001")
        self.chan.write("[RDP client not available in this terminal]")

    async def _vnc(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"VNC client: {raw} — T1021.005")
        self.chan.write("[VNC client not available in this terminal]")

    async def _kinit(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"kinit Kerberos ticket request: {raw} — T1558")
        await asyncio.sleep(1.0)
        self.chan.write("kinit: KDC reply did not match expectations while getting initial credentials")

    async def _klist(self, args, raw):
        self.db.flag_high_interest(self.session_id, "klist — Kerberos ticket enumeration T1558")
        self.chan.write("Credentials cache: API:...\r\nPrincipal: clinadm@CASCADEMEDICAL.LOCAL\r\n"
            "Issued             Expires            Principal\r\n"
            f"{datetime.utcnow().strftime('%b %d %H:%M:%S')}  {(datetime.utcnow()+timedelta(hours=10)).strftime('%b %d %H:%M:%S')}  krbtgt/CASCADEMEDICAL.LOCAL@CASCADEMEDICAL.LOCAL")

    async def _ldapsearch(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"ldapsearch — AD enumeration T1087.002: {raw}")
        await asyncio.sleep(1.5)
        self.chan.write("# extended LDIF\r\n# LDAPv3\r\n# base <DC=cascademedical,DC=local>\r\n"
            "dn: CN=clinadm,OU=Users,DC=cascademedical,DC=local\r\n"
            "cn: clinadm\r\nsAMAccountName: clinadm\r\nmemberOf: CN=Domain Admins,DC=cascademedical,DC=local\r\n"
            "\r\n# 7 entries found")

    async def _exit(self, args, raw):
        self.chan.write("\r\nlogout\r\n")
        await asyncio.sleep(0.3)
        self.chan.close()

    async def _clear(self, args, raw):
        self.chan.write("\033[2J\033[H")

    async def _help(self, args, raw):
        self.chan.write("Commands: ls cd pwd cat whoami id hostname uname ps netstat ifconfig "
            "history env crontab find grep mysql sqlcmd curl wget ssh scp nmap ping nc "
            "telnet systemctl chmod passwd kinit klist ldapsearch openssl python3 exit")
