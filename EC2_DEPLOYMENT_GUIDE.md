# 🚀 AWS EC2 Production Deployment Guide — Yetzo Backend (SAKK Group)

**Target Production Architecture:**
- **Backend API & WebSockets:** `https://sak.yetzo.com`
- **Web Frontend:** `https://yetzo.com` & `https://www.yetzo.com`
- **ASGI Server:** Daphne (Channels + DRF)
- **Database:** NeonDB Cloud PostgreSQL with PostGIS
- **Cache & Tasks:** Redis + Celery
- **Web Server & SSL:** Nginx + Let's Encrypt Certbot
- **Founder / Parent Group:** **SAKK Group**

---

## Table of Contents
1. [AWS EC2 Instance Provisioning & Security Groups](#1-aws-ec2-instance-provisioning--security-groups)
2. [DNS Configuration (A Record for sak.yetzo.com)](#2-dns-configuration-a-record-for-sakyetzocom)
3. [Server Initial Setup & Swap Configuration](#3-server-initial-setup--swap-configuration)
4. [Install System Packages, GDAL & Redis](#4-install-system-packages-gdal--redis)
5. [Clone Repository & Python Virtual Environment](#5-clone-repository--python-virtual-environment)
6. [Configure Production Environment Variables (.env)](#6-configure-production-environment-variables-env)
7. [Database Migrations & Collect Static Files](#7-database-migrations--collect-static-files)
8. [Create Systemd Service for Daphne ASGI](#8-create-systemd-service-for-daphne-asgi)
9. [Create Systemd Service for Celery Background Workers](#9-create-systemd-service-for-celery-background-workers)
10. [Configure Nginx Reverse Proxy with WebSocket Support](#10-configure-nginx-reverse-proxy-with-websocket-support)
11. [Setup Let's Encrypt SSL Certificate (HTTPS)](#11-setup-lets-encrypt-ssl-certificate-https)
12. [Firewall (UFW) & Live Health Check](#12-firewall-ufw--live-health-check)
13. [Future Deployment / Update Script](#13-future-deployment--update-script)

---

## 1. AWS EC2 Instance Provisioning & Security Groups

### Step 1.1: Launch Instance in AWS Console
1. Log in to [AWS Management Console](https://console.aws.amazon.com/ec2/).
2. Select your preferred region (e.g., `ap-south-1` Mumbai or `us-east-1` N. Virginia).
3. Click **Launch Instances**:
   - **Name:** `Yetzo-Backend-Production`
   - **AMI:** `Ubuntu Server 24.04 LTS` (or `22.04 LTS`) (64-bit x86).
   - **Instance Type:** `t3.medium` (2 vCPU, 4 GiB RAM) is **recommended** for running Daphne + Celery + GDAL smoothly. *(Minimum: `t3.small` 2 GiB RAM with Swap)*.
   - **Key Pair:** Create a new key pair or select existing (e.g. `yetzo-ec2-key.pem`). Download and save it securely.
   - **Storage:** 25 GB to 30 GB `gp3` SSD.

### Step 1.2: Configure Security Group (Firewall Rules)
Under **Network Settings**, create a Security Group named `yetzo-backend-sg` with the following **Inbound Rules**:

| Type | Protocol | Port Range | Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| **SSH** | TCP | `22` | `My IP` (or `0.0.0.0/0`) | Secure Terminal Access |
| **HTTP** | TCP | `80` | `0.0.0.0/0` | Web Traffic & Certbot Verification |
| **HTTPS** | TCP | `443` | `0.0.0.0/0` | Encrypted Web & WebSocket Traffic |

### Step 1.3: Allocate and Associate an Elastic IP (Critical)
*If you don't use an Elastic IP, your public IP will change every time the EC2 instance stops or restarts.*
1. In EC2 Dashboard, go to **Network & Security** > **Elastic IPs**.
2. Click **Allocate Elastic IP address** > **Allocate**.
3. Select the allocated IP, click **Actions** > **Associate Elastic IP address**.
4. Choose your `Yetzo-Backend-Production` instance and click **Associate**.
5. Note down this **Elastic Public IP** (e.g., `54.x.x.x`).

---

## 2. DNS Configuration (A Record for sak.yetzo.com)

1. Open your DNS Provider (GoDaddy, Namecheap, Cloudflare, AWS Route 53, etc.) where `yetzo.com` is hosted.
2. Add an **A Record**:
   - **Type:** `A`
   - **Host / Name:** `sak`
   - **Value / Destination:** `<Your-EC2-Elastic-IP>`
   - **TTL:** `300` (5 minutes) or `Automatic`
3. Verify DNS propagation from your terminal:
   ```bash
   ping sak.yetzo.com
   # Or using nslookup
   nslookup sak.yetzo.com
   ```
   *Confirm it resolves to your Elastic IP before installing SSL in Step 11.*

---

## 3. Server Initial Setup & Swap Configuration

Connect to your EC2 instance from your terminal:
```bash
chmod 400 yetzo-ec2-key.pem
ssh -i yetzo-ec2-key.pem ubuntu@<Your-EC2-Elastic-IP>
```

### Configure 2GB Swap Memory (Prevents Out-Of-Memory errors during builds)
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

---

## 4. Install System Packages, GDAL & Redis

Update OS packages and install Python, PostGIS/GDAL runtime libraries, Redis, Nginx, and Certbot:

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    redis-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    ufw
```

### Start & Enable Redis
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
# Verify redis is responding:
redis-cli ping
# Output should be: PONG
```

---

## 5. Clone Repository & Python Virtual Environment

### Step 5.1: Create Project Directory & Clone
```bash
sudo mkdir -p /var/www/YetzoBackend
sudo chown -R ubuntu:ubuntu /var/www/YetzoBackend

git clone https://github.com/Zarvani/YetzoBackend.git /var/www/YetzoBackend
cd /var/www/YetzoBackend
```

### Step 5.2: Create and Activate Virtualenv
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

### Step 5.3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

## 6. Configure Production Environment Variables (.env)

Create the production environment file at `/var/www/YetzoBackend/django_core/.env`:

```bash
nano /var/www/YetzoBackend/django_core/.env
```

Paste the following production configuration:

```env
# =============================================================================
# YETZO BACKEND PRODUCTION ENVIRONMENT (.env) - SAKK GROUP
# =============================================================================

# 1. CORE DJANGO CONFIGURATION
DEBUG=False
SECRET_KEY=y-t-z-0-s-a-k-k-987234098234-super-production-secret-key-change-this!
ALLOWED_HOSTS=sak.yetzo.com,yetzo.com,www.yetzo.com,127.0.0.1,localhost

# 2. CORS & CSRF DOMAINS
CORS_ALLOWED_ORIGINS=https://yetzo.com,https://www.yetzo.com,https://sak.yetzo.com
CSRF_TRUSTED_ORIGINS=https://yetzo.com,https://www.yetzo.com,https://sak.yetzo.com

# 3. DATABASE (NeonDB PostgreSQL Cloud with PostGIS)
DATABASE_URL=postgis://neondb_owner:npg_pgvit1QUkXr7@ep-little-wave-b5sp3qo4.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require

# 4. HTTPS & SECURITY SETTINGS
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# 5. CACHE & CELERY (Local Redis)
REDIS_URL=redis://127.0.0.1:6379/0

# 6. PAYMENT GATEWAYS (Razorpay Live Keys)
RAZORPAY_KEY_ID=rzp_live_your_actual_key_id
RAZORPAY_KEY_SECRET=your_actual_razorpay_secret

# 7. SMS / OTP (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_SERVICE_SID=your_service_sid

# 8. MEDIA CLOUD STORAGE (Cloudinary)
CLOUDINARY_CLOUD_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# 9. FIREBASE CREDENTIALS
FIREBASE_SERVICE_ACCOUNT_PATH=/var/www/YetzoBackend/yetzofirebase.json
```

Secure the `.env` file permissions:
```bash
chmod 600 /var/www/YetzoBackend/django_core/.env
```

---

## 7. Database Migrations & Collect Static Files

Run migrations and static file gathering from within the virtualenv:

```bash
cd /var/www/YetzoBackend/django_core
source /var/www/YetzoBackend/venv/bin/activate

# Collect Django static files
python manage.py collectstatic --noinput

# Run any pending database migrations
python manage.py migrate

# (Optional) Create Django Superuser Admin Account
python manage.py createsuperuser
```

---

## 8. Create Systemd Service for Daphne ASGI

Daphne runs your Django ASGI server (supporting both REST HTTP requests and live `/ws/` WebSockets) on `127.0.0.1:8000`.

Create the systemd service file:
```bash
sudo nano /etc/systemd/system/yetzo-backend.service
```

Paste the following service definition:

```ini
[Unit]
Description=Yetzo Backend Daphne ASGI Server (SAKK Group)
After=network.target redis-server.service

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/YetzoBackend/django_core
EnvironmentFile=/var/www/YetzoBackend/django_core/.env
ExecStart=/var/www/YetzoBackend/venv/bin/daphne \
    -b 127.0.0.1 \
    -p 8000 \
    config.asgi:application

Restart=always
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Reload systemd, start and enable the backend service:
```bash
sudo systemctl daemon-reload
sudo systemctl start yetzo-backend
sudo systemctl enable yetzo-backend

# Check service status:
sudo systemctl status yetzo-backend
```

---

## 9. Create Systemd Service for Celery Background Workers

Create the Celery worker service for asynchronous order processing, SMS/OTP, and notifications:

```bash
sudo nano /etc/systemd/system/yetzo-celery.service
```

Paste the following:

```ini
[Unit]
Description=Yetzo Celery Worker Service (SAKK Group)
After=network.target redis-server.service yetzo-backend.service

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/YetzoBackend/django_core
EnvironmentFile=/var/www/YetzoBackend/django_core/.env
ExecStart=/var/www/YetzoBackend/venv/bin/celery -A config worker --loglevel=info --concurrency=2

Restart=always
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Reload and start Celery:
```bash
sudo systemctl daemon-reload
sudo systemctl start yetzo-celery
sudo systemctl enable yetzo-celery

# Check service status:
sudo systemctl status yetzo-celery
```

---

## 10. Configure Nginx Reverse Proxy with WebSocket Support

Create an Nginx server block for `sak.yetzo.com`:

```bash
sudo nano /etc/nginx/sites-available/sak.yetzo.com
```

Paste the following configuration:

```nginx
upstream daphne_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name sak.yetzo.com;

    client_max_body_size 50M;

    # Static Files Directory
    location /static/ {
        alias /var/www/YetzoBackend/django_core/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # WebSocket Connections (/ws/)
    location /ws/ {
        proxy_pass http://daphne_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }

    # HTTP REST API & Django Admin
    location / {
        proxy_pass http://daphne_backend;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;

        proxy_connect_timeout 60s;
        proxy_read_timeout 120s;
    }
}
```

Enable the site and verify Nginx syntax:
```bash
# Enable site block
sudo ln -s /etc/nginx/sites-available/sak.yetzo.com /etc/nginx/sites-enabled/

# Remove default site if present
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## 11. Setup Let's Encrypt SSL Certificate (HTTPS)

Execute Certbot to automatically configure SSL for `sak.yetzo.com`:

```bash
sudo certbot --nginx -d sak.yetzo.com
```

- When prompted:
  - Enter your administrative email (e.g. `admin@yetzo.com`).
  - Agree to Terms of Service (`Y`).
  - Choose whether to share email with EFF (`N` or `Y`).
- Certbot will automatically inject SSL certificates and rewrite `sak.yetzo.com` to enforce HTTPS.

Test automatic certificate renewal:
```bash
sudo certbot renew --dry-run
```

---

## 12. Firewall (UFW) & Live Health Check

### Enable UFW Firewall
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

### Live Production Health Checks
Test your live backend endpoints from your local machine or terminal:

1. **System Health Ping Check:**
   ```bash
   curl -I https://sak.yetzo.com/api/v1/system/ping/
   ```
   *Expected Response: `HTTP/2 200` with JSON status `healthy`.*

2. **Django Admin Portal:**
   Visit in your browser: `https://sak.yetzo.com/admin/`

3. **Check Live Logs if needed:**
   ```bash
   # Daphne Backend Logs:
   sudo journalctl -u yetzo-backend -f

   # Celery Worker Logs:
   sudo journalctl -u yetzo-celery -f

   # Nginx Error Logs:
   sudo tail -f /var/log/nginx/error.log
   ```

---

## 13. Future Deployment / Quick Update Script

Whenever you push new backend commits to GitHub, deploy them seamlessly with this 1-step update script:

Save as `/var/www/YetzoBackend/deploy.sh`:
```bash
cat << 'EOF' > /var/www/YetzoBackend/deploy.sh
#!/bin/bash
set -e

echo "=== [1/5] Fetching Latest Code from Git ==="
cd /var/www/YetzoBackend
git pull origin main

echo "=== [2/5] Updating Dependencies ==="
source /var/www/YetzoBackend/venv/bin/activate
pip install -r requirements.txt

echo "=== [3/5] Applying Database Migrations ==="
cd /var/www/YetzoBackend/django_core
python manage.py migrate --noinput

echo "=== [4/5] Collecting Static Files ==="
python manage.py collectstatic --noinput

echo "=== [5/5] Restarting Services ==="
sudo systemctl restart yetzo-backend
sudo systemctl restart yetzo-celery
sudo systemctl reload nginx

echo "=== Deployment Completed Successfully! ==="
EOF

chmod +x /var/www/YetzoBackend/deploy.sh
```

To update in future:
```bash
/var/www/YetzoBackend/deploy.sh
```
