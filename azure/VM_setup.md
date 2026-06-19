# Azure VM Setup Guide

## VM Specifications

Both honeypot nodes use the same base configuration:

| Setting | Value |
|---------|-------|
| Size | Standard_B2s (2 vCPU, 4 GB RAM) |
| OS | Ubuntu 22.04 LTS (Gen2) |
| Disk | 30 GB Standard SSD |
| Region | East US 2 |
| Authentication | SSH public key |

## Deployment Steps

### 1. Create Resource Group

```bash
az group create \
  --name honeypot-rg \
  --location eastus2
```

### 2. Create Meridian HR VM

```bash
az vm create \
  --resource-group honeypot-rg \
  --name meridian-prod-01 \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username UserJen \
  --generate-ssh-keys \
  --public-ip-sku Standard
```

### 3. Create Cascade Medical VM

```bash
az vm create \
  --resource-group honeypot-rg \
  --name cascade-emr-prod-01 \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username emradmin \
  --generate-ssh-keys \
  --public-ip-sku Standard
```

### 4. Install Docker on Each VM

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
# Log out and back in
```

### 5. Clone and Deploy

```bash
git clone https://github.com/jennafrank/log-n-pacific-cyber-range.git
cd log-n-pacific-cyber-range/honeypots/meridian-hr
cp .env.example .env
docker compose up -d
```

## Port Reference

### Meridian HR
```
22     SSH honeypot + management (use 2222 or 2223 for management if separating)
88     Kerberos
389    LDAP
445    SMB
636    LDAPS
3268   Global Catalog
6379   Redis
8080   Dashboard
9090   Unified Dashboard
27017  MongoDB
```

### Cascade Medical
```
22     SSH honeypot
23     Telnet
25     SMTP
1433   MSSQL
2575   HL7
3389   RDP
5900   VNC
8080   Dashboard
```
