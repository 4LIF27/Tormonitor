from flask import Flask, jsonify, render_template
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv
from requests.exceptions import RequestException
import os
import warnings

# ================= INIT =================
load_dotenv()
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

app = Flask(__name__, template_folder="templates")
session = requests.Session()
session.verify = False

# ================= ROUTER CONFIG =================
ROUTER_IP = os.getenv("ROUTER_IP")

HNAP_STATUS_URL = f"http://{ROUTER_IP}/HNAP1/GetDeviceSettings"
HNAP_CLIENT_URL = f"http://{ROUTER_IP}/HNAP1/GetClientInfo"

HNAP_HEADERS_STATUS = {
    "Content-Type": "text/xml; charset=UTF-8",
    "SOAPAction": '"http://purenetworks.com/HNAP1/GetDeviceSettings"',
    "User-Agent": "Mozilla/5.0"
}

HNAP_HEADERS_CLIENT = {
    "Content-Type": "text/xml; charset=UTF-8",
    "Cookie": f"session_id={os.getenv('HNAP_COOKIE_SESSION')}",
    "HNAP_AUTH": os.getenv("HNAP_AUTH"),
    "SOAPAction": '"http://purenetworks.com/HNAP1/GetClientInfo"',
    "User-Agent": "Mozilla/5.0"
}

HNAP_COOKIES = {
    "session_id": os.getenv("HNAP_SESSION_ID")
}

SOAP_STATUS = """<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
 <soap:Body>
  <GetDeviceSettings xmlns="http://purenetworks.com/HNAP1/" />
 </soap:Body>
</soap:Envelope>
"""

SOAP_CLIENT = """<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
 <soap:Body>
  <GetClientInfo xmlns="http://purenetworks.com/HNAP1/" />
 </soap:Body>
</soap:Envelope>
"""

NS = {
    "soap": "http://schemas.xmlsoap.org/soap/envelope/",
    "hnap": "http://purenetworks.com/HNAP1/"
}

# ================= HELPER =================
def get(root, tag, default="0"):
    el = root.find(f".//hnap:{tag}", NS)
    return el.text.strip() if el is not None and el.text else default

def quality(v, rules):
    try:
        v = int(v)
    except:
        return "POOR"
    for limit, label in rules:
        if v >= limit:
            return label
    return "POOR"

def to_mb(v):
    if not v:
        return 0
    v = v.upper()
    if v.endswith("GB"):
        return float(v[:-2]) * 1024
    if v.endswith("MB"):
        return float(v[:-2])
    return 0

# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("index.html")

# ================= STATUS =================
@app.route("/api/status")
def api_status():
    try:
        r = session.post(
            HNAP_STATUS_URL,
            headers=HNAP_HEADERS_STATUS,
            cookies=HNAP_COOKIES,
            data=SOAP_STATUS,
            timeout=5
        )
        r.raise_for_status()
        root = ET.fromstring(r.text)

        d = {
            "signal": get(root,"signal_value"),
            "sinr": get(root,"sinr_value"),
            "rsrq": get(root,"rsrq_value"),
            "rssi": get(root,"rssi_value"),
            "cqi": get(root,"cqi_value"),
            "band": get(root,"band_value"),
            "bw": get(root,"bandwidth_value"),
            "cellid": get(root,"cellid_value"),
            "enb": get(root,"enbid_value"),
            "pci": get(root,"pci_value"),
            "tac": get(root,"tac_value"),
            "cpu": get(root,"cpu_use"),
            "ram": get(root,"memory_use"),
            "uptime": get(root,"system_uptime"),
            "ipv4": get(root,"wan_ipv4_value")
        }

        d["signal_status"] = quality(d["signal"],[(90,"EXCELLENT"),(75,"VERY GOOD"),(60,"GOOD"),(40,"FAIR")])
        d["sinr_status"]   = quality(d["sinr"],[(20,"EXCELLENT"),(13,"VERY GOOD"),(7,"GOOD"),(0,"FAIR")])
        d["rsrq_status"]   = quality(d["rsrq"],[(10,"EXCELLENT"),(8,"VERY GOOD"),(6,"GOOD"),(4,"FAIR")])
        d["rssi_status"]   = quality(d["rssi"],[(70,"EXCELLENT"),(60,"VERY GOOD"),(50,"GOOD"),(40,"FAIR")])
        d["cqi_status"]    = quality(d["cqi"],[(13,"EXCELLENT"),(11,"VERY GOOD"),(8,"GOOD"),(6,"FAIR")])

        return jsonify(d)

    except (RequestException, ET.ParseError) as e:
        return jsonify({
            "error": "ROUTER_UNREACHABLE",
            "message": str(e)
        }), 503

# ================= KUOTA =================
@app.route("/api/kuota")
def api_kuota():
    url = "https://bima.tri.co.id/apibima/profile/account"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {os.getenv('TRI_BEARER')}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "X-MSISDN": os.getenv("TRI_MSISDN")
    }

    payload = {
        "imei": "WebSelfcare",
        "language": "0",
        "callPlan": os.getenv("TRI_CALLPLAN"),
        "msisdn": os.getenv("TRI_MSISDN"),
        "secretKey": os.getenv("TRI_SECRET"),
        "subscriberType": "Prepaid"
    }

    try:
        r = session.post(url, headers=headers, json=payload, timeout=10)
        r.raise_for_status()
        raw = r.json()
        p = raw["data"]

        profile = {
            "msisdn": p["msisdn"],
            "tipe": p["subscriberType"],
            "saldo": p["balance"],
            "masa_aktif": p["validity"]
        }

        paket = []
        for g in p.get("packageProductGroupList", []):
            for c in g.get("content", []):
                total = to_mb(c.get("allocated"))
                sisa  = to_mb(c.get("remaining"))
                persen = round((sisa / total) * 100, 2) if total > 0 else 0

                paket.append({
                    "nama": c.get("title"),
                    "total": c.get("allocated"),
                    "sisa": c.get("remaining"),
                    "terpakai": c.get("consumed"),
                    "persen": persen,
                    "berlaku": datetime.strptime(
                        c["validityRaw"], "%Y%m%d%H%M%S"
                    ).strftime("%d %B %Y")
                })

        return jsonify({
            "profile": profile,
            "paket": paket
        })

    except (RequestException, KeyError, ValueError) as e:
        return jsonify({
            "error": "BIMA_API_ERROR",
            "message": str(e)
        }), 503

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)