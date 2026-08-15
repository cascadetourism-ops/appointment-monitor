import os
import sys
import time
import json
import random
import signal
import logging
import threading
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor

# -------------------------------------------------------------------------
# STRUCTURED LOGGING SETUP
# -------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = Flask(__name__)

# -------------------------------------------------------------------------
# CONFIGURATION SETTINGS & VALIDATION
# -------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8969681995:AAHZDtwH1nB5ywnLdC2IYL9nu_VlTr0h9YY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1655607685")
MONITOR_WINDOW_DAYS = int(os.environ.get("MONITOR_WINDOW_DAYS", 120))
POLL_INTERVAL_BASE = int(os.environ.get("POLL_INTERVAL_BASE", 10))  # Native 10 seconds

STATE_FILE = "monitor_state.json"

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logging.critical("Fatal Error: Telegram credentials are not properly configured.")
    sys.exit(1)

# Thread-safe global variables for session state
state_lock = threading.Lock()
shared_session_cookies = {
    '__cf_bm': 'YOUR_CF_BM_COOKIE_HERE',
    '.AspNet.ApplicationCookie': 'YOUR_ACTIVE_SESSION_COOKIE_STRING_HERE'
}

# Exponential Backoff & Circuit Breaker Tracking
consecutive_errors = 0
backoff_multiplier = 1
circuit_open_until = 0
is_running = True

# -------------------------------------------------------------------------
# PERSISTENT STATE MANAGEMENT (JSON FILE CACHE WITH AUTO-RECOVERY)
# -------------------------------------------------------------------------
def load_state():
    default_state = {"last_alerted_dates": {}, "last_checked": None}
    if os.path.exists(STATE_FILE):
        try:
            # Check if file is empty (0 bytes) to prevent JSONDecodeError
            if os.path.getsize(STATE_FILE) == 0:
                logging.warning("State file is empty. Initializing default state.")
                save_state(default_state)
                return default_state
                
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logging.error("State file was corrupted or malformed. Resetting state.")
            save_state(default_state)
            return default_state
        except Exception as e:
            logging.error(f"Failed to load state file: {e}")
    return default_state

def save_state(state_data):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state_data, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save state file: {e}")

# -------------------------------------------------------------------------
# CIRCUIT BREAKER UTILITIES
# -------------------------------------------------------------------------
def check_circuit_breaker():
    global circuit_open_until
    if time.time() < circuit_open_until:
        remaining = int(circuit_open_until - time.time())
        logging.warning(f"Circuit breaker is OPEN. Pausing checks for another {remaining} seconds...")
        return False
    return True

def trip_circuit_breaker(lockout_minutes=15):
    global circuit_open_until
    circuit_open_until = time.time() + (lockout_minutes * 60)
    logging.error(f"🚨 Circuit breaker tripped! Halting slot checks for {lockout_minutes} minutes.")
    send_telegram_alert(f"🚨 Security block detected. Circuit breaker tripped. Pausing checks for {lockout_minutes} mins.")

# -------------------------------------------------------------------------
# TELEGRAM NOTIFICATIONS & COMMAND LISTENER
# -------------------------------------------------------------------------
def send_telegram_alert(message_text):
    """Dispatches any text message to the configured Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logging.info("Telegram message successfully sent!")
        else:
            logging.error(f"Failed to send Telegram message: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Error executing Telegram API call: {e}")

def telegram_command_listener():
    """Background loop that polls Telegram for interactive commands (/status, /checknow, /window)."""
    global MONITOR_WINDOW_DAYS, is_running
    logging.info("Telegram Interactive Command Listener Initialized.")
    offset = 0
    
    while is_running:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url, timeout=35)
            if response.status_code == 200:
                data = response.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    message = update.get("message", {})
                    text = message.get("text", "").strip()
                    chat_id = str(message.get("chat", {}).get("id", ""))
                    
                    if chat_id != TELEGRAM_CHAT_ID:
                        continue
                        
                    if text == "/status":
                        current_state = load_state()
                        status_msg = (
                            f"🟢 Monitor Status: ACTIVE\n"
                            f"📅 Window Days: {MONITOR_WINDOW_DAYS}\n"
                            f"🕒 Last Checked: {current_state.get('last_checked', 'Never')}\n"
                            f"📌 Tracked Slots: {json.dumps(current_state.get('last_alerted_dates', {}))}"
                        )
                        send_telegram_alert(status_msg)
                        
                    elif text == "/checknow":
                        send_telegram_alert("🔄 Manual scan triggered via Telegram command...")
                        threading.Thread(target=monitor_appointment_dates, daemon=True).start()
                        
                    elif text.startswith("/window"):
                        parts = text.split()
                        if len(parts) == 2 and parts[1].isdigit():
                            MONITOR_WINDOW_DAYS = int(parts[1])
                            send_telegram_alert(f"✅ Monitoring window updated successfully to {MONITOR_WINDOW_DAYS} days.")
                        else:
                            send_telegram_alert("⚠️ Invalid usage. Example: `/window 90`")
                            
        except Exception as e:
            if is_running:
                logging.error(f"Error in Telegram command listener: {e}")
        time.sleep(2)

# -------------------------------------------------------------------------
# CORE SLOT MONITORING LOGIC
# -------------------------------------------------------------------------
def check_location_slots(location_name, facility_id, headers):
    global consecutive_errors, backoff_multiplier, MONITOR_WINDOW_DAYS
    
    if not check_circuit_breaker():
        return False

    with state_lock:
        cookies_snapshot = shared_session_cookies.copy()

    try:
        logging.info(f"Checking slots for: {location_name} (Facility ID: {facility_id})...")
        
        # -----------------------------------------------------------------
        # LIVE API TEMPLATE (Uncomment when hooking up real endpoint)
        # -----------------------------------------------------------------
        # target_url = "https://usvisascheduling.com/api/slots"
        # response = requests.post(target_url, headers=headers, cookies=cookies_snapshot, data={"facility_id": facility_id}, timeout=15)
        #
        # if response.status_code in [401, 403] or "login" in response.url.lower():
        #     send_telegram_alert("⚠️ CRITICAL: Session cookies have expired or been blocked! Update required via /update-session.")
        #     trip_circuit_breaker(30)
        #     return False
        # if response.status_code == 429:
        #     trip_circuit_breaker(15)
        #     raise Exception("Rate limited (429 Too Many Requests)")
        #
        # data = response.json()
        # earliest_date_str = data.get("date")
        # total_slots = data.get("available_slots", 0)

        # MOCK IMPLEMENTATION
        if location_name == "Dubai":
            earliest_date_str = "2027-07-20"
            total_slots = 3
        else:
            earliest_date_str = None
            total_slots = 0
        
        consecutive_errors = 0
        backoff_multiplier = 1

        state = load_state()
        state["last_checked"] = datetime.now(timezone(timedelta(hours=4))).isoformat()
        save_state(state)

        if earliest_date_str and total_slots > 0:
            slot_date = datetime.strptime(earliest_date_str, "%Y-%m-%d")
            max_allowed_date = datetime.now() + timedelta(days=MONITOR_WINDOW_DAYS)
            
            logging.info(f"[{location_name}] Found slot: {slot_date.strftime('%Y-%m-%d')} ({total_slots} available) | Max threshold: {max_allowed_date.strftime('%Y-%m-%d')}")

            if slot_date <= max_allowed_date:
                last_sent_date = state["last_alerted_dates"].get(location_name)
                
                if last_sent_date != earliest_date_str:
                    alert_text = f"📍 {location_name}\n📅 Date: {earliest_date_str} ({total_slots} slots)"
                    send_telegram_alert(alert_text)
                    
                    state["last_alerted_dates"][location_name] = earliest_date_str
                    save_state(state)
                else:
                    logging.info(f"[{location_name}] Slot on {earliest_date_str} already alerted. Suppressing duplicate.")
            else:
                logging.info(f"{location_name}: Slot found on {earliest_date_str}, exceeds your {MONITOR_WINDOW_DAYS}-day window.")
        else:
            logging.info(f"No valid appointment slots found for {location_name}.")
        return True
            
    except Exception as err:
        consecutive_errors += 1
        backoff_multiplier = min(consecutive_errors * 2, 30)
        logging.error(f"Error checking {location_name}: {err}. Backoff active: {backoff_multiplier}x")
        if consecutive_errors >= 3:
            trip_circuit_breaker(10)
        return False

def monitor_appointment_dates():
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://usvisascheduling.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    locations = [
        {"name": "Abu Dhabi", "facility_id": "abu_dhabi_code_here"},
        {"name": "Dubai", "facility_id": "dubai_code_here"}
    ]

    with ThreadPoolExecutor(max_workers=len(locations)) as executor:
        for loc in locations:
            executor.submit(
                check_location_slots,
                location_name=loc["name"],
                facility_id=loc["facility_id"],
                headers=headers
            )

def continuous_scheduler():
    global is_running
    logging.info("Background Monitoring Thread Initialized (10s interval + Drift Correction + Jitter).")
    while is_running:
        loop_start = time.time()
        
        # Execute concurrent facility checks
        monitor_appointment_dates()
        
        # Anti-bot Jitter (Adds ±2 seconds of organic variance)
        jitter = random.uniform(-2, 2)
        target_sleep = max(2, POLL_INTERVAL_BASE + jitter) * backoff_multiplier
        
        # Drift Correction (Subtracts execution time to keep cadence sharp)
        elapsed = time.time() - loop_start
        sleep_duration = max(0, target_sleep - elapsed)
        
        logging.info(f"Sleeping for {round(sleep_duration, 2)} seconds before next cycle...")
        
        slept = 0
        while slept < sleep_duration and is_running:
            time.sleep(1)
            slept += 1

# -------------------------------------------------------------------------
# GRACEFUL SHUTDOWN HANDLER
# -------------------------------------------------------------------------
def handle_exit(signum, frame):
    global is_running
    logging.info("Shutdown signal received. Stopping threads cleanly...")
    is_running = False
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# -------------------------------------------------------------------------
# FLASK WEB ENDPOINTS
# -------------------------------------------------------------------------
@app.route('/')
def home():
    state = load_state()
    return jsonify({
        "status": "healthy",
        "locations": ["Abu Dhabi", "Dubai"],
        "monitoring_active": is_running,
        "window_days": MONITOR_WINDOW_DAYS,
        "last_checked": state.get("last_checked"),
        "timestamp": datetime.now(timezone(timedelta(hours=4))).isoformat() + "Z"
    })

@app.route('/update-session', methods=['POST'])
def update_session():
    global shared_session_cookies
    data = request.json
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400
        
    with state_lock:
        for key in shared_session_cookies.keys():
            if key in data:
                shared_session_cookies[key] = data[key]
                
    logging.info("Session cookies updated dynamically via API endpoint.")
    return jsonify({"status": "success", "message": "Session cookies updated successfully."})

@app.route('/run-task', methods=['GET', 'POST'])
def run_task():
    monitor_appointment_dates()
    return jsonify({
        "status": "success",
        "message": "Manual concurrent scans executed."
    })

if __name__ == '__main__':
    threading.Thread(target=continuous_scheduler, daemon=True).start()
    threading.Thread(target=telegram_command_listener, daemon=True).start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
