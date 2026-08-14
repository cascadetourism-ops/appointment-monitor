import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

def monitor_appointment_dates():
    # Base configuration headers (use the ones from your cURL converter)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    
    # -------------------------------------------------------------------------
    # STEP 1: Fetch fresh configuration data from your target website
    # -------------------------------------------------------------------------
    init_url = "https://example.com..." # Replace with your location/init API
    
    try:
        print("Initializing session to refresh cloud tokens...")
        init_response = requests.get(init_url, headers=headers, timeout=10)
        if init_response.status_code != 200:
            print(f"Failed session initialization: {init_response.status_code}")
            return False, "Auth refresh failed"
            
        # Extract security components if required by your target site
        # session_cookies = init_response.cookies
        
    except Exception as init_err:
        print(f"Initialization exception: {init_err}")
        return False, str(init_err)

    # -------------------------------------------------------------------------
    # STEP 2: Query the Date Availability Grid
    # -------------------------------------------------------------------------
    calendar_url = "https://example.com..." # Replace with your date API
    
    try:
        print("Scanning calendar grid for available dates...")
        response = requests.get(calendar_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            days_list = data.get("ScheduleDays", [])
            
            # Filter out null values to find real, operational dates
            valid_dates = [day.get("Date") for day in days_list if day.get("Date") is not None]
            
            if len(valid_dates) > 0:
                print(f"🚨 ALERT: Mapped appointment dates detected in system: {valid_dates}")
                
                # Learning step: You can write logic here to match your target criteria
                # e.g., if any("2026" in d for d in valid_dates): trigger_notification()
                
                return True, f"Detected active dates: {valid_dates}"
            else:
                print("Monitoring check completed. No active dates open on the grid.")
                return True, "Calendar grid is currently empty."
        else:
            print(f"Calendar query returned error: {response.status_code}")
            return False, f"HTTP Status {response.status_code}"
            
    except Exception as e:
        print(f"Error handling network execution: {e}")
        return False, str(e)

@app.route("/run-booking", methods=["POST"])
def trigger_endpoint():
    success, message = monitor_appointment_dates()
    if success:
        return jsonify({"status": "success", "detail": message}), 200
    else:
        return jsonify({"status": "failed", "error": message}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
