import os
import time
import threading
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# -------------------------------------------------------------------------
# CONFIGURATION SETTINGS
# Safely reads from Environment Variables; falls back to defaults
# -------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8969681995:AAHZDtwH1nB5ywnLdC2IYL9nu_VlTr0h9YY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1655607685")
MONITOR_WINDOW_DAYS = 120

def send_telegram_alert(message_text):
    """
    Dispatches an instant notification message to your Telegram account.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
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

def monitor_appointment_dates():
    """
    Queries the scheduling endpoint and checks if any available slot 
    falls within the MONITOR_WINDOW_DAYS timeframe.
    """
    target_url = "https://usvisascheduling.com"
    
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://usvisascheduling.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    cookies = {
        '__cf_bm': 'ofsN8sEXk3HCOLTsHwjCCc8fujRRbeDI4iC_LBuiu0U-1786711693.180439-1.0.1.1-LQgv0MLw.Ldp_KQ2.fNF4xI75SADuVdvvKMRDl65BMbsAFMcz5nVQTUct17kEoNrQPkHy5VsQiI13V3m9E6fJnYUIX4jSrx1pkfpSkA3tiknYTCbKPLVFpwmJss7JVuV'
    }

    try:
        print(f"[{datetime.now()}] Requesting target scheduling endpoint...")
        
        # NOTE: Uncomment the line below when making actual requests to the target endpoint.
        # response = requests.get(target_url, headers=headers, cookies=cookies, timeout=15)
        # data = response.json()
        
        # --- REAL PARSING LOGIC EXAMPLE ---
        # Assuming the API returns a JSON key like "earliest_date" in "YYYY-MM-DD" format:
        # earliest_date_str = data.get("earliest_date")
        
        # For demonstration (since live endpoint structure varies and requires active auth sessions):
        earliest_date_str = None  # Change this or connect to real parsed response data
        
        if earliest_date_str:
            slot_date = datetime.strptime(earliest_date_str, "%Y-%m-%d")
            max_allowed_date = datetime.now() + timedelta(days=MONITOR_WINDOW_DAYS)
            
            # Check if the found slot is within your 120-day window
            if slot_date <= max_allowed_date:
                send_telegram_alert(f"⚠️ *US Visa Slot Found!*\nAn open slot is available on: {earliest_date_str}")
            else:
                print(f"Slot found on {earliest_date_str}, but it is outside your {MONITOR_WINDOW_DAYS}-day window.")
        else:
            print("No slots currently available or waiting for valid response data.")
            
    except Exception as err:
        print(f"Error during portal check: {err}")

def continuous_scheduler():
    """
    Runs indefinitely in a background thread to trigger checks without blocking Flask.
    """
    print("Background Monitoring Thread Initialized.")
    while True:
        monitor_appointment_dates()
        # Interval check execution pause (e.g., checks every 10 minutes)
        time.sleep(600)

# Start background monitoring before running the server instance
monitoring_thread = threading.Thread(target=continuous_scheduler, daemon=True)
monitoring_thread.start()

@app.route('/')
def home():
    """
    Basic health check routing node for live monitoring metrics.
    """
    return jsonify({
        "status": "healthy",
        "monitoring_active": True,
        "window_days": MONITOR_WINDOW_DAYS,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@app.route('/run-task', methods=['GET', 'POST'])
def run_task():
    """
    Dedicated endpoint for external cron job services to trigger checks.
    """
    monitor_appointment_dates()
    
    return jsonify({
        "status": "success",
        "message": "Appointment scan executed.",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
