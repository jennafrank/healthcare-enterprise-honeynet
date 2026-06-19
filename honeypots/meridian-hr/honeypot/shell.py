"""
FakeShell — Meridian HR Solutions internal server simulation.
No Easter eggs. Every command logged. Realistic corporate Linux environment.
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from .db import DB
from .logger import HoneypotLogger
from .meridian_hr_realism import ssh_latency, generate_noise_lines


FAKE_HOSTNAME = "meridian-hrprod-01"
FAKE_OS_BANNER = "Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-112-generic x86_64)"
FAKE_KERNEL = "Linux meridian-hrprod-01 5.15.0-112-generic #122-Ubuntu SMP Thu May 23 07:48:21 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux"

FAKE_USERS = [
    "root:x:0:0:root:/root:/bin/bash",
    "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin",
    "syslog:x:104:110::/home/syslog:/usr/sbin/nologin",
    "meridian:x:1000:1000:Meridian Admin,,,:/home/meridian:/bin/bash",
    "hradmin:x:1001:1001:HR Administrator,,,:/home/hradmin:/bin/bash",
    "payroll:x:1002:1002:Payroll Service Account,,,:/home/payroll:/bin/bash",
    "dbbackup:x:1003:1003:Database Backup,,,:/home/dbbackup:/bin/bash",
    "deploy:x:1004:1004:Deploy Bot,,,:/home/deploy:/bin/bash",
    "sftp_user:x:1005:1005:SFTP Only,,,:/home/sftp_user:/usr/sbin/nologin",
]

FAKE_SHADOW = [
    "root:$6$rounds=656000$REDACTED$hashedpasswordplaceholder:19450:0:99999:7:::",
    "meridian:$6$rounds=656000$salt123$hashedplaceholder:19450:0:99999:7:::",
    "hradmin:$6$hr2024$REDACTED:19450:0:99999:7:::",
    "payroll:$6$pay$REDACTED:19450:0:99999:7:::",
]

FAKE_HISTORY = [
    "sudo systemctl restart mysql",
    "tail -f /var/log/mysql/error.log",
    "cd /opt/meridian/payroll",
    "python3 process_payroll.py --month=2024-05",
    "mysqldump -u root -p meridian_hr > /backup/hr_backup_$(date +%Y%m%d).sql",
    "ls -la /opt/meridian/",
    "cat /opt/meridian/config/db.conf",
    "redis-cli ping",
    "mongo --eval 'db.stats()'",
    "df -h",
    "systemctl status nginx",
    "sudo apt update && sudo apt upgrade -y",
    "crontab -l",
    "ps aux | grep python",
    "netstat -tlnp",
    "cat /etc/hosts",
    "scp hr_export.csv deploy@10.0.1.45:/data/imports/",
]

FAKE_CRONTAB = """# Meridian HR Production Crontab
# m h  dom mon dow   command
0 2 * * * /opt/meridian/scripts/db_backup.sh >> /var/log/backup.log 2>&1
*/15 * * * * /opt/meridian/scripts/health_check.sh
0 6 * * 1-5 python3 /opt/meridian/payroll/daily_sync.py
0 0 1 * * python3 /opt/meridian/payroll/monthly_report.py --output=/data/reports/
30 23 * * * /opt/meridian/scripts/rotate_logs.sh
"""

FAKE_DB_CONF = """[database]
host = 127.0.0.1
port = 3306
name = meridian_hr
user = meridian_app
password = M3r1d1@n_Prod_2024!
pool_size = 20
timeout = 30

[redis]
host = 127.0.0.1
port = 6379
password = R3d1s_Sess10n_Key!
db = 0

[mongo]
uri = mongodb://meridian_mongo:M0ng0_HR_2024!@127.0.0.1:27017/meridian_docs
"""

FAKE_LS_HOME = """total 64
drwxr-x--- 8 meridian meridian 4096 Jun  3 08:22 .
drwxr-xr-x 9 root     root     4096 May 12 14:00 ..
-rw------- 1 meridian meridian  847 Jun  3 08:22 .bash_history
-rw-r--r-- 1 meridian meridian  220 Jan  1  2024 .bash_logout
-rw-r--r-- 1 meridian meridian 3526 Jan  1  2024 .bashrc
drwx------ 2 meridian meridian 4096 May 12 14:02 .ssh
-rw------- 1 meridian meridian   38 Jun  1 09:15 .mysql_history
drwxrwxr-x 3 meridian meridian 4096 May 12 14:10 backups
drwxr-xr-x 2 meridian meridian 4096 Jun  3 07:44 scripts
-rw-r--r-- 1 meridian meridian  512 May 30 16:00 notes.txt
"""

FAKE_NOTES = """TODO:
- Update payroll DB password (IT requested rotation by EOQ)
- Check with finance re: Q2 export permissions
- SFTP credentials for ADP integration: sftp_user / Adp_Sftp_2024
- Remind team: prod DB is NOT to be accessed directly, use app layer
- Follow up on MongoDB replica set config
"""

FAKE_SSH_KEYS = """-rw------- 1 meridian meridian  411 May 12 14:02 authorized_keys
-rw------- 1 meridian meridian 2602 May 12 14:02 id_rsa
-rw-r--r-- 1 meridian meridian  571 May 12 14:02 id_rsa.pub
"""

FAKE_AUTHORIZED_KEYS = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7xK... hradmin@meridian-mgmt-01
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDz9p... deploy@ci-runner-prod
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCmVx... jsmith@meridian-laptop-04
"""

FAKE_PROCESSES = """USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.1 168624 11284 ?        Ss   May12   2:14 /sbin/init
mysql        812  0.4  8.3 1842356 337212 ?      Ssl  May12 218:43 /usr/sbin/mysqld
redis       1044  0.1  0.4  65304 16888 ?        Ssl  May12  44:12 redis-server 127.0.0.1:6379
mongod      1112  0.3  6.1 1624044 249680 ?      Ssl  May12 132:08 /usr/bin/mongod --config /etc/mongod.conf
www-data    2201  0.0  0.5 224556 22144 ?         S   May12   8:44 nginx: worker process
meridian    3304  0.1  1.2 312448 50900 ?         S   08:01   0:44 python3 /opt/meridian/payroll/daemon.py
meridian    3308  0.0  0.4 188032 18432 ?         S   08:01   0:02 python3 /opt/meridian/scripts/health_check.sh
root        3412  0.0  0.1  14988  5248 ?         S   08:22   0:00 sshd: meridian [priv]
meridian    3415  0.0  0.1  15112  4992 pts/0     Ss   08:22   0:00 -bash
"""

FAKE_NETSTAT = """Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      1344/sshd
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN      812/mysqld
tcp        0      0 127.0.0.1:6379          0.0.0.0:*               LISTEN      1044/redis-server
tcp        0      0 0.0.0.0:27017           0.0.0.0:*               LISTEN      1112/mongod
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      2200/nginx
tcp        0      0 0.0.0.0:443             0.0.0.0:*               LISTEN      2200/nginx
tcp6       0      0 :::22                   :::*                    LISTEN      1344/sshd
"""

MOTD = """\r
Welcome to Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-112-generic x86_64)\r
\r
 * Meridian HR Solutions — Production Server (hrprod-01)\r
 * AUTHORIZED ACCESS ONLY. All sessions are logged and monitored.\r
 * For support: sysops@meridianhr.internal | Ext. 4412\r
\r
  System information as of {date}\r
\r
  System load:  0.{load}         Processes:           {procs}\r
  Usage of /:   {disk}% of {disksize}GB   Users logged in:     1\r
  Memory usage: {mem}%            IPv4 address for eth0: 10.0.1.{ip_last}\r
\r
Last login: {last_login} from 10.0.1.{last_ip}\r
\r
"""


class FakeShell:
    def __init__(self, chan, session_id: int, username: str, db: DB, hplogger: HoneypotLogger):
        self.chan = chan
        self.session_id = session_id
        self.username = username
        self.db = db
        self.hplogger = hplogger
        self.cwd = f"/home/{username}"
        self.is_root = username == "root"
        self.input_buffer = ""
        self.command_count = 0

    def motd(self) -> str:
        now = datetime.utcnow()
        last = now - timedelta(days=random.randint(1, 5), hours=random.randint(1, 12))
        return MOTD.format(
            date=now.strftime("%a %b %d %H:%M:%S UTC %Y"),
            load=random.randint(10, 45),
            procs=random.randint(180, 240),
            disk=random.randint(38, 62),
            disksize=random.choice([200, 500, 1000]),
            mem=random.randint(42, 71),
            ip_last=random.randint(10, 60),
            last_login=last.strftime("%a %b %d %H:%M:%S %Y"),
            last_ip=random.randint(2, 50),
        )

    def prompt(self) -> str:
        user = "root" if self.is_root else self.username
        symbol = "#" if self.is_root else "$"
        short_cwd = self.cwd.replace(f"/home/{self.username}", "~")
        return f"\r\n{user}@{FAKE_HOSTNAME}:{short_cwd}{symbol} "

    async def handle_input(self, data: str):
        for char in data:
            if char in ("\r", "\n"):
                cmd = self.input_buffer.strip()
                self.input_buffer = ""
                if cmd:
                    self.chan.write("\r\n")
                    await self._dispatch(cmd)
                self.chan.write(self.prompt())
            elif char == "\x7f":  # backspace
                if self.input_buffer:
                    self.input_buffer = self.input_buffer[:-1]
                    self.chan.write("\b \b")
            elif char == "\x03":  # ctrl-c
                self.input_buffer = ""
                self.chan.write("^C")
                self.chan.write(self.prompt())
            elif char == "\x04":  # ctrl-d
                self.chan.write("\r\nlogout\r\n")
                self.chan.close()
            else:
                self.input_buffer += char
                self.chan.write(char)

    async def _dispatch(self, raw_cmd: str):
        self.command_count += 1
        parts = raw_cmd.split()
        cmd = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        # Log everything
        self.db.log_command(self.session_id, raw_cmd)
        self.hplogger.log_event("command", {
            "session_id": self.session_id,
            "command": raw_cmd,
            "command_number": self.command_count,
        })

        await ssh_latency()

        # Command dispatch
        handlers = {
            "ls": self._cmd_ls,
            "ll": self._cmd_ls,
            "dir": self._cmd_ls,
            "cd": self._cmd_cd,
            "pwd": self._cmd_pwd,
            "cat": self._cmd_cat,
            "whoami": self._cmd_whoami,
            "id": self._cmd_id,
            "hostname": self._cmd_hostname,
            "uname": self._cmd_uname,
            "ps": self._cmd_ps,
            "top": self._cmd_top,
            "htop": self._cmd_top,
            "ifconfig": self._cmd_ifconfig,
            "ip": self._cmd_ip,
            "netstat": self._cmd_netstat,
            "ss": self._cmd_netstat,
            "history": self._cmd_history,
            "sudo": self._cmd_sudo,
            "su": self._cmd_su,
            "env": self._cmd_env,
            "printenv": self._cmd_env,
            "export": self._cmd_export,
            "echo": self._cmd_echo,
            "date": self._cmd_date,
            "uptime": self._cmd_uptime,
            "df": self._cmd_df,
            "free": self._cmd_free,
            "crontab": self._cmd_crontab,
            "wget": self._cmd_wget,
            "curl": self._cmd_curl,
            "chmod": self._cmd_chmod,
            "chown": self._cmd_chown,
            "find": self._cmd_find,
            "grep": self._cmd_grep,
            "mkdir": self._cmd_mkdir,
            "touch": self._cmd_touch,
            "rm": self._cmd_rm,
            "mv": self._cmd_mv,
            "cp": self._cmd_cp,
            "ssh": self._cmd_ssh,
            "ssh-keygen": self._cmd_ssh_keygen,
            "scp": self._cmd_scp,
            "python3": self._cmd_python,
            "python": self._cmd_python,
            "mysql": self._cmd_mysql,
            "mysqldump": self._cmd_mysqldump,
            "redis-cli": self._cmd_redis,
            "mongo": self._cmd_mongo,
            "mongosh": self._cmd_mongo,
            "systemctl": self._cmd_systemctl,
            "service": self._cmd_service,
            "apt": self._cmd_apt,
            "apt-get": self._cmd_apt,
            "yum": self._cmd_apt,
            "ping": self._cmd_ping,
            "nmap": self._cmd_nmap,
            "nc": self._cmd_nc,
            "netcat": self._cmd_nc,
            "passwd": self._cmd_passwd,
            "adduser": self._cmd_adduser,
            "useradd": self._cmd_adduser,
            "screen": self._cmd_screen,
            "tmux": self._cmd_screen,
            "lscpu": self._cmd_lscpu,
            "exit": self._cmd_exit,
            "logout": self._cmd_exit,
            "clear": self._cmd_clear,
            "help": self._cmd_help,
        }

        # Handle piped commands — still log, run first part
        pipe_cmd = cmd
        if "|" in raw_cmd:
            pipe_cmd = raw_cmd.split("|")[0].strip().split()[0]

        handler = handlers.get(pipe_cmd) or handlers.get(cmd)
        if handler:
            await handler(args, raw_cmd)
        else:
            self.chan.write(f"-bash: {cmd}: command not found")

    # ─── Command Implementations ───────────────────────────────────────────────

    async def _cmd_ls(self, args, raw):
        path = args[0] if args and not args[0].startswith("-") else self.cwd
        flag_l = "-l" in raw or "-la" in raw or "-al" in raw or "ll" in raw.split()[0]

        if path in (".", self.cwd, f"/home/{self.username}", "~"):
            self.chan.write(FAKE_LS_HOME if flag_l else "backups  notes.txt  scripts")
        elif path == "/home/meridian/.ssh" or (self.cwd.endswith(".ssh")):
            self.chan.write(FAKE_SSH_KEYS if flag_l else "authorized_keys  id_rsa  id_rsa.pub")
        elif "/opt/meridian" in path or path == "/opt":
            self.chan.write("config  logs  payroll  reports  scripts  uploads" if not flag_l else
                "total 48\r\ndrwxr-xr-x 6 meridian meridian 4096 Jun  3 07:00 .\r\n"
                "drwxr-xr-x 8 root     root     4096 May 12 14:00 ..\r\n"
                "drwxr-xr-x 2 meridian meridian 4096 Jun  2 11:22 config\r\n"
                "drwxrwxr-x 2 meridian meridian 4096 Jun  3 08:01 logs\r\n"
                "drwxr-xr-x 4 meridian meridian 4096 May 30 09:14 payroll\r\n"
                "drwxr-x--- 2 meridian meridian 4096 Jun  1 16:00 reports\r\n"
                "drwxr-xr-x 3 meridian meridian 4096 May 12 14:05 scripts\r\n"
                "drwxrwxr-x 2 meridian meridian 4096 Jun  3 07:44 uploads")
        elif path in ("/backup", "/backups", "backups"):
            self.chan.write(
                "hr_backup_20240601.sql.gz  hr_backup_20240602.sql.gz  hr_backup_20240603.sql.gz\r\n"
                "payroll_export_2024-05.csv  payroll_export_2024-04.csv"
            )
        elif path in ("/etc",):
            self.chan.write("hosts  hostname  passwd  shadow  crontab  ssh  mysql  redis  mongod.conf  nginx")
        elif path == "/var/log":
            self.chan.write("auth.log  syslog  mysql  nginx  meridian.log  backup.log")
        else:
            self.chan.write(f"ls: cannot access '{path}': No such file or directory")

    async def _cmd_cd(self, args, raw):
        if not args or args[0] in ("~", f"/home/{self.username}"):
            self.cwd = f"/home/{self.username}"
        elif args[0] == "/":
            self.cwd = "/"
        elif args[0].startswith("/"):
            self.cwd = args[0]
        elif args[0] == "..":
            parts = self.cwd.rstrip("/").rsplit("/", 1)
            self.cwd = parts[0] if parts[0] else "/"
        else:
            self.cwd = f"{self.cwd.rstrip('/')}/{args[0]}"

    async def _cmd_pwd(self, args, raw):
        self.chan.write(self.cwd)

    async def _cmd_cat(self, args, raw):
        if not args:
            self.chan.write("cat: missing operand")
            return
        target = " ".join(args)
        # Normalize path
        if not target.startswith("/"):
            target = f"{self.cwd.rstrip('/')}/{target}"

        if "passwd" in target and "shadow" not in target:
            self.chan.write("\r\n".join(FAKE_USERS))
        elif "shadow" in target:
            if not self.is_root:
                self.chan.write("cat: /etc/shadow: Permission denied")
            else:
                self.chan.write("\r\n".join(FAKE_SHADOW))
        elif "db.conf" in target or "config" in target and "db" in target:
            self.chan.write(FAKE_DB_CONF)
            self.db.flag_high_interest(self.session_id, "cat db.conf — credentials exposed")
        elif "notes.txt" in target:
            self.chan.write(FAKE_NOTES)
            self.db.flag_high_interest(self.session_id, "cat notes.txt — SFTP creds in notes")
        elif "authorized_keys" in target:
            self.chan.write(FAKE_AUTHORIZED_KEYS)
        elif "id_rsa" in target and "pub" not in target:
            self.chan.write("cat: /home/meridian/.ssh/id_rsa: Permission denied")
        elif "auth.log" in target:
            self.chan.write(self._fake_auth_log())
        elif "backup" in target and ".sql" in target:
            await asyncio.sleep(1.2)
            self.chan.write("-- MySQL dump 10.13  Distrib 8.0.36, for Linux (x86_64)\r\n"
                            "-- Meridian HR Solutions — hr_db\r\n"
                            "-- [BINARY DATA — pipe through zcat to decompress]\r\n")
        elif "hosts" in target:
            self.chan.write("127.0.0.1   localhost\r\n"
                            "127.0.1.1   meridian-hrprod-01\r\n"
                            "10.0.1.10   meridian-db-primary\r\n"
                            "10.0.1.11   meridian-db-replica\r\n"
                            "10.0.1.45   meridian-deploy\r\n"
                            "10.0.1.100  meridian-mgmt-01\r\n"
                            "10.0.0.101  cascade-emr-prod-01    cascade-emr-prod-01.cascademedical.local")
        else:
            self.chan.write(f"cat: {target}: No such file or directory")

    def _fake_auth_log(self):
        now = datetime.utcnow()
        lines = generate_noise_lines(count=20, host=FAKE_HOSTNAME, anchor=now)
        lines.append(
            f"{now.strftime('%b %d %H:%M:%S')} {FAKE_HOSTNAME} sshd[3412]: "
            "Accepted password for meridian from 10.0.1.100 port 54022 ssh2"
        )
        return "\r\n".join(lines)

    async def _cmd_whoami(self, args, raw):
        self.chan.write("root" if self.is_root else self.username)

    async def _cmd_id(self, args, raw):
        if self.is_root:
            self.chan.write("uid=0(root) gid=0(root) groups=0(root)")
        else:
            uid = 1000 + ["meridian","hradmin","payroll","dbbackup","deploy"].index(self.username) if self.username in ["meridian","hradmin","payroll","dbbackup","deploy"] else 1000
            self.chan.write(f"uid={uid}({self.username}) gid={uid}({self.username}) groups={uid}({self.username}),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),110(lxd)")

    async def _cmd_hostname(self, args, raw):
        self.chan.write(FAKE_HOSTNAME)

    async def _cmd_uname(self, args, raw):
        if "-a" in raw:
            self.chan.write(FAKE_KERNEL)
        else:
            self.chan.write("Linux")

    async def _cmd_ps(self, args, raw):
        self.chan.write(FAKE_PROCESSES)

    async def _cmd_top(self, args, raw):
        self.chan.write("[top/htop unavailable in this terminal session — use 'ps aux' for process list]")

    async def _cmd_ifconfig(self, args, raw):
        self.chan.write(
            "eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\r\n"
            "        inet 10.0.0.101  netmask 255.255.255.0  broadcast 10.0.0.255\r\n"
            "        inet6 fe80::20d:3aff:fe4b:cccc  prefixlen 64  scopeid 0x20<link>\r\n"
            "        ether 00:0d:3a:4b:cc:cc  txqueuelen 1000  (Ethernet)\r\n"
            "        RX packets 982441  bytes 1406229812 (1.3 GiB)\r\n\r\n"
            "lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536\r\n"
            "        inet 127.0.0.1  netmask 255.0.0.0\r\n"
        )

    async def _cmd_ip(self, args, raw):
        if "addr" in raw or "a" in args:
            await self._cmd_ifconfig(args, raw)
        elif "route" in raw or "r" in args:
            self.chan.write("default via 10.0.0.1 dev eth0 proto dhcp src 10.0.0.101 metric 100\r\n"
                            "10.0.0.0/24 dev eth0 proto kernel scope link src 10.0.0.101")
        else:
            self.chan.write("Usage: ip [addr|route|link]")

    async def _cmd_netstat(self, args, raw):
        self.chan.write(FAKE_NETSTAT)

    async def _cmd_history(self, args, raw):
        lines = [f"  {i+1}  {cmd}" for i, cmd in enumerate(FAKE_HISTORY)]
        self.chan.write("\r\n".join(lines))

    async def _cmd_sudo(self, args, raw):
        if not args:
            self.chan.write("usage: sudo command")
            return
        if args[0] == "su" or (args[0] == "-" and len(args) == 1):
            self.is_root = True
            self.chan.write("[sudo] password for meridian: ")
            await asyncio.sleep(0.8)
            self.chan.write("\r\nroot@{FAKE_HOSTNAME}:/# ")
        elif args[0] in ("systemctl", "apt", "apt-get"):
            # Pass through to real handler
            await self._dispatch(" ".join(args))
        else:
            self.is_root = True
            await self._dispatch(" ".join(args))

    async def _cmd_su(self, args, raw):
        await asyncio.sleep(0.6)
        self.is_root = True
        self.chan.write(f"Password: \r\nroot@{FAKE_HOSTNAME}:{self.cwd}# ")
        self.db.flag_high_interest(self.session_id, "su — escalation attempt succeeded")

    async def _cmd_env(self, args, raw):
        self.chan.write(
            f"SHELL=/bin/bash\r\nTERM=xterm-256color\r\nUSER={self.username}\r\n"
            "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\r\n"
            "HOME=/home/meridian\r\nLANGUAGE=en_US:en\r\nLANG=en_US.UTF-8\r\n"
            "DB_HOST=127.0.0.1\r\nDB_NAME=meridian_hr\r\n"
            "DB_PASS=M3r1d1@n_Prod_2024!\r\n"  # Intentionally juicy
            "REDIS_URL=redis://:R3d1s_Sess10n_Key!@127.0.0.1:6379/0\r\n"
            "MONGO_URI=mongodb://meridian_mongo:M0ng0_HR_2024!@127.0.0.1:27017/meridian_docs\r\n"
            "LOGNAME=meridian\r\nSSH_TTY=/dev/pts/0\r\n"
        )
        self.db.flag_high_interest(self.session_id, "env — environment variables with credentials exposed")

    async def _cmd_export(self, args, raw):
        # Log anti-forensics behavior
        if "HISTFILE=/dev/null" in raw or "HISTSIZE=0" in raw:
            self.db.flag_high_interest(self.session_id, f"anti-forensics: {raw}")
        self.chan.write("")  # Silent success

    async def _cmd_echo(self, args, raw):
        content = raw[5:].strip() if raw.startswith("echo") else ""
        self.chan.write(content.strip('"').strip("'"))

    async def _cmd_date(self, args, raw):
        self.chan.write(datetime.utcnow().strftime("%a %b %d %H:%M:%S UTC %Y"))

    async def _cmd_uptime(self, args, raw):
        self.chan.write(f" {datetime.utcnow().strftime('%H:%M:%S')} up {random.randint(30,180)} days, {random.randint(1,23)}:{random.randint(10,59)},  1 user,  load average: 0.{random.randint(10,45)}, 0.{random.randint(10,45)}, 0.{random.randint(10,45)}")

    async def _cmd_df(self, args, raw):
        self.chan.write(
            "Filesystem      Size  Used Avail Use% Mounted on\r\n"
            "/dev/sda1       500G  187G  293G  39% /\r\n"
            "tmpfs            16G     0   16G   0% /dev/shm\r\n"
            "/dev/sdb1       2.0T  892G  1.1T  45% /backup\r\n"
        )

    async def _cmd_free(self, args, raw):
        self.chan.write(
            "               total        used        free      shared  buff/cache   available\r\n"
            "Mem:        16384000     8847232     1923040      224512     5613728     7049024\r\n"
            "Swap:        4096000      102400     3993600"
        )

    async def _cmd_crontab(self, args, raw):
        if "-l" in args:
            self.chan.write(FAKE_CRONTAB)
        elif "-e" in args:
            self.chan.write("[crontab editor not available in this session — use 'crontab -l' to view]")
        else:
            self.chan.write(FAKE_CRONTAB)

    async def _cmd_wget(self, args, raw):
        if not args or args[0].startswith("-"):
            self.chan.write("wget: missing URL")
            return
        url = args[-1]
        self.db.flag_high_interest(self.session_id, f"wget ingress tool transfer: {url}")
        filename = url.split("/")[-1] or "index.html"
        self.chan.write(f"--{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}--  {url}\r\n")
        await asyncio.sleep(1.5)
        self.chan.write(f"Resolving {url.split('/')[2]}... connection timed out.\r\n"
                        "wget: unable to resolve host address — check firewall rules")

    async def _cmd_curl(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"curl: {raw}")
        if "169.254.169.254" in raw:  # IMDS endpoint
            self.chan.write('{"computeMetadata":{"v1":{"instance":{"id":8234762341,"machineType":"Standard_B2s","zone":"us-east-1a"}}}}')
            self.db.flag_high_interest(self.session_id, "CRITICAL: IMDS metadata endpoint probed")
        else:
            self.chan.write("curl: (6) Could not resolve host: name resolution blocked")

    async def _cmd_chmod(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"chmod: {raw}")
        self.chan.write("")

    async def _cmd_chown(self, args, raw):
        self.chan.write("")

    async def _cmd_find(self, args, raw):
        if "password" in raw or "passwd" in raw or "secret" in raw or "key" in raw or "cred" in raw:
            self.db.flag_high_interest(self.session_id, f"find credential search: {raw}")
            await asyncio.sleep(1.5)
            self.chan.write(
                "/opt/meridian/config/db.conf\r\n"
                "/home/meridian/notes.txt\r\n"
                "/home/meridian/.mysql_history\r\n"
                "/etc/mysql/debian.cnf\r\n"
                "/var/log/meridian.log"
            )
        elif ".ssh" in raw or "id_rsa" in raw:
            self.db.flag_high_interest(self.session_id, f"find SSH key search: {raw}")
            self.chan.write("/home/meridian/.ssh/id_rsa\r\n/home/meridian/.ssh/authorized_keys")
        else:
            await asyncio.sleep(0.8)
            self.chan.write("")

    async def _cmd_grep(self, args, raw):
        if "password" in raw or "pass" in raw or "secret" in raw:
            self.db.flag_high_interest(self.session_id, f"grep credential search: {raw}")
        self.chan.write("")

    async def _cmd_mkdir(self, args, raw):
        self.chan.write("")

    async def _cmd_touch(self, args, raw):
        self.chan.write("")

    async def _cmd_rm(self, args, raw):
        if "-rf" in raw and ("/" in args or "/" in raw.split("-rf")[-1].strip()):
            self.db.flag_high_interest(self.session_id, f"rm -rf destructive command: {raw}")
        self.chan.write("")

    async def _cmd_mv(self, args, raw):
        self.chan.write("")

    async def _cmd_cp(self, args, raw):
        self.chan.write("")

    async def _cmd_ssh(self, args, raw):
        if args:
            self.db.flag_high_interest(self.session_id, f"lateral movement attempt: ssh {' '.join(args)}")
        self.chan.write("ssh: connect to host: Network unreachable")

    async def _cmd_ssh_keygen(self, args, raw):
        self.db.flag_high_interest(self.session_id, "ssh-keygen — persistence attempt")
        await asyncio.sleep(1.2)
        self.chan.write(
            "Generating public/private rsa key pair.\r\n"
            "Enter file in which to save the key (/home/meridian/.ssh/id_rsa): \r\n"
            "/home/meridian/.ssh/id_rsa already exists.\r\n"
            "Overwrite (y/n)? "
        )
        await asyncio.sleep(30)  # Hang waiting for input
        self.chan.write("\r\nOperation cancelled.")

    async def _cmd_scp(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"scp exfil attempt: {raw}")
        self.chan.write("scp: Connection closed")

    async def _cmd_python(self, args, raw):
        version = "3.10.12" if "python3" in raw else "2.7.18"
        self.chan.write(
            f"Python {version} (default, Nov 14 2022, 12:59:47) [GCC 11.4.0] on linux\r\n"
            'Type "help", "copyright", "credits" or "license" for more information.\r\n'
            ">>> "
        )
        await asyncio.sleep(60)
        self.chan.write("\r\n[Session timeout]\r\n")

    async def _cmd_mysql(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"mysql client invoked: {raw}")
        await asyncio.sleep(1.0)
        if "-p" in raw or "--password" in raw:
            self.chan.write(
                "Welcome to the MySQL monitor.  Commands end with ; or \\g.\r\n"
                "Your MySQL connection id is 4821\r\n"
                "Server version: 8.0.36 MySQL Community Server - GPL\r\n\r\n"
                "mysql> "
            )
        else:
            self.chan.write("ERROR 1045 (28000): Access denied for user (using password: NO)")

    async def _cmd_mysqldump(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"mysqldump exfil attempt: {raw}")
        await asyncio.sleep(2.0)
        self.chan.write("mysqldump: Got error: 1044: Access denied for user to database 'meridian_hr'")

    async def _cmd_redis(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"redis-cli: {raw}")
        if "ping" in raw:
            self.chan.write("PONG")
        elif "keys" in raw:
            await asyncio.sleep(0.5)
            self.chan.write(
                "1) \"session:user:8821\"\r\n2) \"session:user:8819\"\r\n"
                "3) \"session:token:payroll_api\"\r\n4) \"cache:hr_report_2024q1\"\r\n"
                "5) \"auth:jwt_secret\""
            )
            self.db.flag_high_interest(self.session_id, "redis keys enumeration — JWT secret visible")
        elif "get" in raw:
            self.chan.write('"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJpYXQiOjE3MTcwMDAwMDB9.FAKE_SIGNATURE"')
        elif "config" in raw:
            self.chan.write("(error) NOAUTH Authentication required")
        else:
            self.chan.write("OK")

    async def _cmd_mongo(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"mongo client: {raw}")
        await asyncio.sleep(1.0)
        self.chan.write(
            "Connecting to: mongodb://127.0.0.1:27017/meridian_docs\r\n"
            "MongoDB server version: 7.0.4\r\n"
            "> "
        )
        await asyncio.sleep(60)

    async def _cmd_systemctl(self, args, raw):
        if not args:
            self.chan.write("No unit specified.")
            return
        action = args[0]
        unit = args[1] if len(args) > 1 else ""
        if action == "status":
            self.chan.write(f"● {unit} - Service\r\n   Active: active (running) since May 12\r\n   Main PID: {random.randint(800,4000)}")
        elif action in ("stop", "disable"):
            self.db.flag_high_interest(self.session_id, f"systemctl {action} {unit} — service disruption")
            self.chan.write(f"Failed to {action} {unit}: Access denied")
        else:
            self.chan.write("")

    async def _cmd_service(self, args, raw):
        await self._cmd_systemctl(list(reversed(args)), raw)

    async def _cmd_apt(self, args, raw):
        await asyncio.sleep(0.8)
        self.chan.write(
            "Reading package lists... Done\r\n"
            "Building dependency tree... Done\r\n"
            "E: Could not open lock file /var/lib/dpkg/lock-frontend - open (13: Permission denied)\r\n"
            "E: Unable to acquire the dpkg frontend lock — are you root?"
        )

    async def _cmd_ping(self, args, raw):
        target = args[0] if args else "localhost"
        self.chan.write(f"PING {target}: Network unreachable")

    async def _cmd_nmap(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"nmap network scan: {raw}")
        await asyncio.sleep(3.0)
        self.chan.write(
            "Starting Nmap 7.80 ( https://nmap.org )\r\n"
            "Note: Host seems down. If it is really up, but blocking our ping probes, try -Pn\r\n"
            "Nmap done: 0 hosts up scanned in 3.22 seconds"
        )

    async def _cmd_nc(self, args, raw):
        self.db.flag_high_interest(self.session_id, f"netcat: {raw} — possible C2 or reverse shell")
        await asyncio.sleep(5.0)
        self.chan.write("(UNKNOWN) []: Connection timed out")

    async def _cmd_passwd(self, args, raw):
        self.chan.write(f"Changing password for {self.username}.\r\nCurrent password: ")
        await asyncio.sleep(1.0)
        self.chan.write("\r\nNew password: ")
        await asyncio.sleep(1.0)
        self.chan.write("\r\nRetype new password: ")
        await asyncio.sleep(1.0)
        self.chan.write("\r\npasswd: password updated successfully")
        self.db.flag_high_interest(self.session_id, "passwd — password change attempt")

    async def _cmd_adduser(self, args, raw):
        user = args[0] if args else "newuser"
        self.db.flag_high_interest(self.session_id, f"adduser/useradd — persistence: {user}")
        self.chan.write(f"useradd: Permission denied.\r\nuseradd: cannot lock /etc/passwd; try again later.")

    async def _cmd_screen(self, args, raw):
        self.db.flag_high_interest(self.session_id, "screen/tmux — persistence/detach attempt")
        self.chan.write("[screen/tmux not available on this host]")

    async def _cmd_lscpu(self, args, raw):
        self.chan.write(
            "Architecture:                    x86_64\r\nCPU(s):                          2\r\n"
            "Model name:                      Intel(R) Xeon(R) Platinum 8272CL CPU @ 2.60GHz\r\n"
            "CPU MHz:                         2593.905\r\nL3 cache:                        36608K"
        )

    async def _cmd_exit(self, args, raw):
        self.chan.write("\r\nlogout\r\n")
        await asyncio.sleep(0.3)
        self.chan.close()

    async def _cmd_clear(self, args, raw):
        self.chan.write("\033[2J\033[H")

    async def _cmd_help(self, args, raw):
        self.chan.write(
            "Available commands: ls, cd, pwd, cat, whoami, id, hostname, uname, ps, ifconfig,\r\n"
            "ip, netstat, history, env, crontab, wget, curl, find, grep, mysql, redis-cli, mongo,\r\n"
            "systemctl, ssh, scp, python3, chmod, rm, mkdir, screen, nmap, ping, passwd, exit"
        )
