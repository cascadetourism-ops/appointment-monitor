import logging
from datetime import datetime
import time
import sys

# Configure logging to write to both file and console with proper formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("visa_bot.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Configuration Parameters (Set to 10 seconds)
CHECK_INTERVAL_SECONDS = 10  
MAX_THRESHOLD_DATE = datetime.strptime("2026-12-12", "%Y-%m-%d")

def check_abu_dhabi():
    """Simulates checking Abu Dhabi slots. Replace with your actual API/Selenium logic."""
    logging.info("Checking slots for: Abu Dhabi (Facility ID: abu_dhabi_code_here)...")
    # TODO: Implement your actual fetching logic here
    logging.info("No valid appointment slots found for Abu Dhabi.")
    return None

def check_dubai():
    """Simulates checking Dubai slots. Replace with your actual API/Selenium logic."""
    logging.info("Checking slots for: Dubai (Facility ID: dubai_code_here)...")
    
    # --- MOCK DATA (Replace this block with your actual web-scraping or API response) ---
    found_date_str = "2027-07-20"
    available_count = 3
    current_threshold = datetime.now().strftime("%Y-%m-%d")
    # ---------------------------------------------------------------------------------
    
    slot_date = datetime.strptime(found_date_str, "%Y-%m-%d")
    logging.info(f"[Dubai] Found slot: {found_date_str} ({available_count} available) | Max threshold: {current_threshold}")
    
    if slot_date > MAX_THRESHOLD_DATE:
        logging.info(f"Dubai: Slot found on {found_date_str}, exceeds your 120-day window.")
    else:
        logging.info(f"SUCCESS! Valid Dubai slot found on {found_date_str}!")
        # Trigger your alert mechanism here (Telegram, Twilio, Email, etc.)
        
    return slot_date

def main_loop():
    logging.info("Starting continuous visa slot checking script (every 10 seconds)...")
    
    while True:
        loop_start = time.time()
        
        try:
            # Execute checks for facilities safely
            check_abu_dhabi()
            check_dubai()
            
        except Exception as err:
            # Catch-all for any unexpected anomalies or network errors to prevent script crashes
            logging.critical(f"An unexpected error occurred: {err}", exc_info=True)
            
        # Calculate elapsed time to ensure exact 10-second spacing regardless of how long checks take
        elapsed = time.time() - loop_start
        sleep_time = max(0, CHECK_INTERVAL_SECONDS - elapsed)
        time.sleep(sleep_time)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        logging.info("Script manually stopped by user. Exiting gracefully.")
