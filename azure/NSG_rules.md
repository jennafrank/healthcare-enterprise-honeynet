# Azure NSG Rules

## Meridian HR NSG

| Priority | Name | Port | Protocol | Source | Action |
|----------|------|------|----------|--------|--------|
| 100 | Allow-SSH-Mgmt | 2223 | TCP | Your IP | Allow |
| 110 | Allow-Dashboard | 8080 | TCP | Your IP | Allow |
| 120 | Allow-Unified | 9090 | TCP | Your IP | Allow |
| 200 | Allow-SSH-Honey | 22 | TCP | Any | Allow |
| 210 | Allow-Kerberos | 88 | TCP/UDP | Any | Allow |
| 220 | Allow-LDAP | 389 | TCP | Any | Allow |
| 230 | Allow-SMB | 445 | TCP | Any | Allow |
| 240 | Allow-Redis | 6379 | TCP | Any | Allow |
| 250 | Allow-MongoDB | 27017 | TCP | Any | Allow |
| 65000 | DenyAllInbound | * | * | Any | Deny |

## Cascade Medical NSG

| Priority | Name | Port | Protocol | Source | Action |
|----------|------|------|----------|--------|--------|
| 100 | Allow-SSH-Mgmt | 2223 | TCP | Your IP | Allow |
| 110 | Allow-Dashboard | 8080 | TCP | Your IP | Allow |
| 200 | Allow-RDP | 3389 | TCP | Any | Allow |
| 210 | Allow-MSSQL | 1433 | TCP | Any | Allow |
| 220 | Allow-VNC | 5900 | TCP | Any | Allow |
| 230 | Allow-Telnet | 23 | TCP | Any | Allow |
| 240 | Allow-SSH-Honey | 22 | TCP | Any | Allow |
| 250 | Allow-HL7 | 2575 | TCP | Any | Allow |
| 260 | Allow-SMTP | 25 | TCP | Any | Allow |
| 65000 | DenyAllInbound | * | * | Any | Deny |

## Important Notes

- Dashboard ports (8080, 9090) should be restricted to your IP only — these show attacker data and have no auth
- SMB port 445 conflicts with host Samba. If the host runs Samba, remove `445:445` from docker-compose and use `4450:445` instead, then update the NSG rule accordingly
- The honeypot ports (22, 3389, etc.) should be open to `Any` — that's the point
- Management SSH (2223) must be open to your IP before exposing port 22 to the internet, or you'll lose access
