import os
import time
import threading
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# -------------------------------------------------------------------------
# CONFIGURATION SETTINGS (WINDOW DAYS = 700)
# -------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8969681995:AAHZDtwH1nB5ywnLdC2IYL9nu_VlTr0h9YY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1655607685")
MONITOR_WINDOW_DAYS = 700

def send_telegram_alert(location_name, slot_date_str, slot_time_str="10:15", visa_type="B1/B2"):
    """
    Dispatches a structured instant notification message to your Telegram account
    matching your required custom format.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Generate current timestamp matching format: 2026-08-12T13:50:18+04:00
    current_timestamp = datetime.now().astimezone().isoformat(timespec='seconds')
    
    message_text = (
        f"🚨 USA visa appointment detected\n"
        f"📍 {location_name}\n"
        f"📅 {slot_date_str}\n"
        f"🛂 {visa_type}\n"
        f"⏰ {slot_time_str}\n"
        f"🔎 Detected: {current_timestamp}"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Telegram alert successfully sent!")
        else:
            print(f"Failed to send Telegram alert: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error executing Telegram API call: {e}")

def check_location_slots(location_name, facility_id, headers, cookies):
    """
    Queries a specific consular location and evaluates the returned appointment date 
    against the 700-day window threshold.
    """
    target_url = "https://usvisascheduling.com"
    
    try:
        print(f"[{datetime.now()}] Checking slots for: {location_name} (Facility ID: {facility_id})...")
        
        # -----------------------------------------------------------------
        # LIVE API REQUEST IMPLEMENTATION
        # -----------------------------------------------------------------
        # payload = {"facility_id": facility_id}
        # response = requests.post(target_url, headers=headers, cookies=cookies, data=payload, timeout=15)
        # data = response.json()
        # earliest_date_str = data.get("earliest_date")  # e.g., "2027-07-20"
        # appointment_time = data.get("earliest_time", "10:15")
        # visa_category = data.get("visa_class", "B1/B2")
        
        # FOR DEMONSTRATION / MOCKING REAL RESULTS:
        if location_name == "Dubai":
            earliest_date_str = "2026-08-27"
            appointment_time = "10:15"
            visa_category = "B1/B2"
        elif location_name == "Abu Dhabi":
            earliest_date_str = "2026-09-03"
            appointment_time = "07:30"
            visa_category = "B1/B2"
        else:
            earliest_date_str = None
            appointment_time = "10:15"
            visa_category = "B1/B2"
        
        if earliest_date_str:
            slot_date = datetime.strptime(earliest_date_str, "%Y-%m-%d")
            max_allowed_date = datetime.now() + timedelta(days=MONITOR_WINDOW_DAYS)
            
            print(f"[{location_name}] Found slot: {slot_date.strftime('%Y-%m-%d')} | Max window threshold: {max_allowed_date.strftime('%Y-%m-%d')}")

            # Check if the found slot falls within your 700-day window
            if slot_date <= max_allowed_date:
                send_telegram_alert(
                    location_name=location_name,
                    slot_date_str=earliest_date_str,
                    slot_time_str=appointment_time,
                    visa_type=visa_category
                )
            else:
                print(f"{location_name}: Slot found on {earliest_date_str}, but it exceeds your {MONITOR_WINDOW_DAYS}-day window.")
        else:
            print(f"No valid appointment slots returned for {location_name}.")
            
    except Exception as err:
        print(f"Error checking {location_name}: {err}")

def monitor_appointment_dates():
    """
    Iterates through both Abu Dhabi and Dubai using shared session credentials.
    """
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://usvisascheduling.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    shared_session_cookies = {
        '__cf_bm': 'ofsN8sEXk3HCOLTsHwjCCc8fujRRbeDI4iC_LBuiu0U-1786711693.180439-1.0.1.1-LQgv0MLw.Ldp_KQ2.fNF4xI75SADuVdvvKMRDl65BMbsAFMcz5nVQTUct17kEoNrQPkHy5VsQiI13V3m9E6fJnYUIX4jSrx1pkfpSkA3tiknYTCbKPLVFpwmJss7JVuV',
        '.AspNet.ApplicationCookie': 'YOUR_ACTIVE_SESSION_COOKIE_STRING_HERE'
    }

    locations = [
        {"name": "Abu Dhabi", "facility_id": "abu_dhabi_code_here"},
        {"name": "Dubai", "facility_id": "dubai_code_here"}
    ]

    for loc in locations:
        check_location_slots(
            location_name=loc["name"],
            facility_id=loc["facility_id"],
            headers=headers,
            cookies=shared_session_cookies
        )
        time.sleep(3)

def continuous_scheduler():
    print("Background Monitoring Thread Initialized for UAE (Abu Dhabi & Dubai).")
    while True:
        monitor_appointment_dates()
        time.sleep(600)  # Check every 10 minutes

monitoring_thread = threading.Thread(target=continuous_scheduler, daemon=True)
monitoring_thread.start()

@app.route('/')
def home():
    return jsonify({
        "status": "healthy",
        "locations": ["Abu Dhabi", "Dubai"],
        "monitoring_active": True,
        "window_days": MONITOR_WINDOW_DAYS,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@app.route('/run-task', methods=['GET', 'POST'])
def run_task():
    monitor_appointment_dates()
    return jsonify({
        "status": "success",
        "message": "Scans executed for Abu Dhabi and Dubai using shared session."
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
