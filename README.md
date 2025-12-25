# 📡 Router & Kuota Monitor API

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-API-black?logo=flask)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Stable-success)

---
![Preview](https://raw.githubusercontent.com/4LIF27/Tormonitor/refs/heads/main/1766629920640.jpg)
![Preview](https://raw.githubusercontent.com/4LIF27/Tormonitor/refs/heads/main/1766629920640.jpg)
## 🇮🇩 Deskripsi (Bahasa Indonesia)

**Router & Kuota Monitor API** adalah aplikasi berbasis **Flask** untuk:
- 📶 Monitoring status & kualitas sinyal router LTE/4G (HNAP SOAP)
- 📊 Analisis kualitas jaringan otomatis
- 📦 Mengecek kuota & paket **Tri (3) Indonesia** via BIMA API
- 🌐 Menyediakan REST API JSON untuk dashboard / frontend

Cocok untuk **home server, Raspberry Pi, router LTE, dan dashboard monitoring jaringan**.

---

## 🇬🇧 Description (English)

**Router & Quota Monitor API** is a **Flask-based application** designed to:
- 📶 Monitor LTE/4G router status using HNAP SOAP
- 📊 Automatically evaluate signal quality
- 📦 Check Tri (3 Indonesia) data quota via BIMA API
- 🌐 Provide clean JSON REST endpoints for dashboards

Perfect for **network monitoring dashboards and home servers**.

---

## ✨ Features

### 📡 Router Monitoring
- Signal Strength
- SINR, RSRQ, RSSI, CQI
- LTE Band & Bandwidth
- Cell ID, eNB ID, PCI, TAC
- CPU & RAM Usage
- Router Uptime
- WAN IPv4

### 📊 Signal Quality Rating
Automatic classification:
- **EXCELLENT**
- **VERY GOOD**
- **GOOD**
- **FAIR**
- **POOR**

### 📦 Tri (3) Quota Checker
- MSISDN
- Balance
- Active period
- Package list
- Total / Remaining quota
- Usage percentage
- Package expiry date

---

## 🏗️ System Architecture

```text
┌──────────────┐
│   Browser    │
│  Dashboard   │
└──────┬───────┘
       │ HTTP / JSON
       ▼
┌─────────────────────┐
│    Flask Server     │
│     app.py :8000    │
├─────────┬───────────┤
│ /status │ /kuota    │
└────┬────┴────┬──────┘
     │         │
     ▼         ▼
┌─────────┐ ┌─────────────────┐
│ Router  │ │  BIMA TRI API    │
│ HNAP    │ │  HTTPS REST      │
│ SOAP    │ └─────────────────┘
└─────────┘


---

🛠️ Tech Stack

Python 3.x

Flask

Requests

XML (HNAP SOAP)

dotenv (.env)

REST API (JSON)

Docker (optional)



---

📂 Project Structure

.
├── app.py
├── templates/
│   └── index.html
├── requirements.txt
├── Dockerfile
├── .env
└── README.md


---

⚙️ Environment Configuration

Create .env file:

# ROUTER CONFIG
ROUTER_IP=192.168.1.1
HNAP_AUTH=xxxxxxxxxxxxxxxx
HNAP_COOKIE_SESSION=xxxxxxxxxxxxxxxx
HNAP_SESSION_ID=xxxxxxxxxxxxxxxx

# TRI / BIMA CONFIG
TRI_BEARER=BearerTokenHere
TRI_MSISDN=628xxxxxxxxxx
TRI_CALLPLAN=xxxxxxxx
TRI_SECRET=xxxxxxxx

⚠️ Never commit .env to public repositories!


---

🚀 Run Without Docker

Install Dependencies

pip install -r requirements.txt

Run Server

python app.py

Access

Web Dashboard

http://localhost:8000/

Router Status API

http://localhost:8000/api/status

Quota API

http://localhost:8000/api/kuota



---

🐳 Run With Docker

Dockerfile

FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["python", "app.py"]

Build & Run

docker build -t router-monitor .
docker run -d -p 8000:8000 --env-file .env router-monitor

---

⚠️ Disclaimer

This project is for educational and personal use only.
Use responsibly and comply with ISP and device policies.


---

⭐ Support

If this project helps you:

⭐ Star this repository

🍴 Fork & improve

🛠️ Pull requests are welcome!
