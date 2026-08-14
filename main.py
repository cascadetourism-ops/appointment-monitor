import os
import time
import threading
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

# -------------------------------------------------------------------------
# CONFIGURATION SETTINGS (WINDOW DAYS = 700)
# -------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8969681995:AAHZDtwH1nB5ywnLdC2IYL9nu_VlTr0h9YY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1655607685")
MONITOR_WINDOW_DAYS = 120

def send_telegram_alert(location_name, slot_date_str):
    """
    Dispatches a simplified Telegram notification containing only the location
    and the calendar date, with no slot counts.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    message_text = (
        f"📍 {location_name}\n"
        f"📅 Date: {slot_date_str}"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text
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
    Queries a specific consular location and evaluates appointment availability 
    against the 700-day window threshold. Messages are suppressed if no slots exist.
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
        # total_slots = data.get("slot_count", 0)       # e.g., number of available slots
        
        # FOR DEMONSTRATION / MOCKING REAL RESULTS:
        if location_name == "Dubai":
            earliest_date_str = "2027-07-20"
            total_slots = 3
        else:
            # Simulating no slots found for other locations (e.g., Abu Dhabi)
            earliest_date_str = None
            total_slots = 0
        
        # Guard condition: ensure both a date exists AND the slot count is strictly greater than 0
        if earliest_date_str and total_slots > 0:
            slot_date = datetime.strptime(earliest_date_str, "%Y-%m-%d")
            max_allowed_date = datetime.now() + timedelta(days=MONITOR_WINDOW_DAYS)
            
            print(f"[{location_name}] Found slot: {slot_date.strftime('%Y-%m-%d')} ({total_slots} available) | Max window threshold: {max_allowed_date.strftime('%Y-%m-%d')}")

            # Check if the found slot falls within your 700-day window
            if slot_date <= max_allowed_date:
                send_telegram_alert(
                    location_name=location_name,
                    slot_date_str=earliest_date_str
                )
            else:
                print(f"{location_name}: Slot found on {earliest_date_str}, but it exceeds your {MONITOR_WINDOW_DAYS}-day window.")
        else:
            print(f"No valid appointment slots found for {location_name}. Skipping alert.")
            
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
    "__cf_bm": "BelV8bmrM84IAeNTllNK9lXbdRkLDw0vZhTqeRVXnHs-1786733201.6684322-1.0.1.1-S1mTfYCbKEluJUMdltyT1ZFgYFwCjjYuWvH8zgqQJfBPeU7xmOGu34fi22C5cPr1HRqxp2gyTofCDI8e6aW0mzXcrpO9t0C8pHwYHorPcwHucUCqQ.uSx17Njm_vFjAl",
    "__cfwaitingroom": "Chh2UXR0OFE0TTVRN0JTbVhuRDRzQzlnPT0SgAIzU3gxbVVmOE5jNzM1ejRPc0YxUVpkcTFSTmtTRFVRWCtTbW9pcjU2OEFVWmNpRXY5VnhEbFZiNkphSUpYR21KRC9JdHVmYS96cG1hV0tFT3NTWk5ndGtFZUhBbGdTekFHMzZvVzJiZ2I3WDBnWVkxUnJ6cVlSZlp2ZENjR0pwNThoMTFLOGd2Qy9BSXdzZWtiUmtMbjNRTW5tY0hpa1dxWFNMNlQ3WFI1TU5oRm05NEk0ZlQrWnBoclQ4SVJGSnZZdjB6eTYwa0ZDSDdNeXNjeHFGM2JuUGZmcGZWdDI3UENYaXBZOWYxUU5vamN0S2I4OWh1aTdWVDBJRmx4K0Q2",
    "__RequestVerificationToken": "2F1bRy1azkXSn0g150paLQy77l0VWZp-3lejwEUAvLfij1UliuEGeNdW0Gk0CwPT6wrLB3cFbEw-PEOTp7CRqpKfAbGKNY_k9mFkdUDIT5o1",
    "_cfuvid": "y0SzOKmK2Y19I5j.dCkQjR6gt12MIzcPd8.QZZNF1fY-1786733169.0908751-1.0.1.1-R22WvjD8JQK317.sTcf5xHqUUaT8M2LwAyA5tvrIkl4",
    ".AspNet.ApplicationCookie": "IZ8F86Xkcq4GdW4qFoLj3S9B7qRmDJLAD0KjajrTwwOrGEh47L3r4MYhLjcgGY0IbffZIrwLFvlBBNDh7U3FDL83EcOp6XhyH9zPsdTWUmYQUncHbl5XX_8urOQCesJZAaRA7sDad9NHM0qtiwyCiIHoaPB3Y5EZalV9QBlIN_SADw2sxUz_2n9ALkmOLMIMfR5_YkGmg_Sa54CbdgsioTHY5tRrvGbtBdxbeG_LDoyKZ2hYJnlF8Bwt_Jx_eZo6LRV3NRNTeLwk4ch0cAvb7s-M0DJg9azNEeQSr06_bGd_rPh4HiG8LH5ue8GjeE1RW-82ZzM65LirINPqxEhj3VGlz7F6OWT9BKbI-R0PYSD423CEhyWwmAt0Wo-w4Y5zWT_NoBx0929pN5xEKFk5WIJ1zsREVs7mzlNXpel0uv_eOqqY9muEL0EDS0BlalRiHOC8sGw2t-VI1PJlexOxZ58is9noEY7M6LY-GQNdTk9Dbsoa9Fax_2plLYWvJU2md736Ovg3KGdt1h-fh8jnADYH9cRnyUt2Ap9NCbUiXQRFkkFTE08DQZh2Lt0Lyanc96yhZ-BAJdlFyzEfBuB4SCgE7iu27MEEXCE8Gqncrmxv68Xc_iZbFKYEtio_q0i-HVNix6BeVInAhUl0VrK87HPBNqNAMdEfzagrAL37KQz57IxnZs5qj5T8ZEP-qC4xq94MKmKQKk1wzZqqMxzWGKjJ2CUxgStqRLzcd6_JgHIZ31Re7gpY2ZIr7YCEY9sSPyWAGMS2jzIH-UTLi_7Yj10CXj4nyineBOISUcuBijW3qKAtOeICQNXZY6Tt5ZWImO4n-tpohn9mtWqkFjbYbZWWrGC9MLH0gUdrOQBAfuXJGXkVTtbhuXpZXELMLNNSjrf2sjnQdzg6CupdPIxWJnjkDAgb4rcOhhLIqechzoK8KNatmkAOaAoBZ4S4s4UVPo4qTYZnWX0U7ID_9-YZK2VgEq0AWhj8lQyf1Dt4N7OmjiBikgp8xVB-vl1ZaRmByVFHp9ZjsV4Pti2yK0d6HHKbLS66UyEUQXdwA3ifGMvXlpb2Z-mMiSjyeq2_tFXkHh0JJworaFVS-KmrAdk4rsP4d2emklZIaaHxpUvfKwYgsxmVHLtARcYf6ZBlfYOahsLnQ32bM2W8eh6kEttWDsgWDu5MImLDQ0HV0UkJWzPDz3W3vTQ-e809KlQbeZrdKLXwUJN1ge8BwVlEoi64GAtCuUxDgptNvq5M_D8qf8AflQrl0_EG_6LjJGAjIkx9PWk-fW_rsX99unSBO8XHCUoT4Ln7Cr_Li97gtlwsUdnqAknLI3NoY21jkOkFJpTtLUY05d-N_DH2C8GbQv8R_sfCamvNhZQ5x-A13zXHfRNSn5pgKG7Di1Cv4s4ZTaP24vtVU3F_U_tr9MBEZ6y8O-X8I1fziQv_D7ZDZ89-d0XkGe5_lchARmvSkM1nPAxgmlfO3kLJJaPIK3akBGmqttuDtzlEJ9wYnVGIK2XRXYEBOxSwAWGo55K8SZ-JGnxpp1BaMRmmthnuVQW-4mgmoiSu7Bq174MHRryhUe_r3ZKqh_9pkkGQSmv6q-vpxV2JWw_BhAuHPteW52MaBZvmVR6hIlt8Tcwb-eA9WvRPGpbTttodjkXIYYDcLGson_ybW-vKo5d2-JOtkkLD1TDCymFa3COIJNv4X-dz4jFU9W3CGEqJ70j2hKtFEu2oZB95XlTV716hWsXhNFCZhZEcQUtuQRHW4t9cMsu4udQHN88zarPmyb6w-KBSF8ervzzXK1adoMzePvieJPvuChys-a21ywepKXRD4MtyMD39qwxLuOSINy9ZGyqVEmXxreJL_gS-WvKfJAM8t2jX3acKNr-EA0MUlEkQ34LgMRaNly9U-llzbh3TCQrezuCDcSsMD2WN1jiMeIS9n-MyHK1IyZ4cqp2OK_Gx5Oonih80sfDsBWKMVZwVJ3sKsCmolXDsAICrONbvstYBgMxWMNJJnM69uVIlovFnKS_Yx7H-ZA2hcLsKdQkhZWpRepyX5O1P1e431rgePmFbWObuLh9Kw6e8I2citcwgggkb1rM6kcC0mB9F4Kk5yR2fa2GGfG3kmFNjJtOEHbbPIf29eXTtV1MRD3_vvcOE0lULT-hBN_PIZzHVD8lRnK2fTnty0K0u2FKIRwBEet_9XW2AjthL2BEM1grxCjqMHKglK2bIqJeu5ENBZ3fv--z6A44YmHFoaU4G3Svzj6FhiI8Ja1RLz7SIS7SKxTgQRvpUTWC0q0HdtXwc9mXgADKFZB-x3Sw3sBA2I-xekG5qFFq3-aPBsRvUGCppcv_TaiI7biTCvLFIDrWNUe7XtkKaJZM0_6UYB1Zo_e0FR9rEm5rrVIM5xM4wwj3_Ia1ml8TQ_rSIDiwreQETWvxxVhrL64BUJYW1tX7GHn-FLvZ_2egOXphz3G8lo4zTln4OzOA10WKvHluUn1ZDXxtCKjwX1VVTBa6Zt4ZY5DiXgPc7SNj7h5Oq1YggitnYDvpAh3Hctiq3WQcywYqIfGEIk8q22kD_1PhDKau2Yb3jcBH7jXVLKjttDPp55YENM8ih6AhUyf_H33YSOIuo0OgnagigSZjDjNKvhp4sEKyQ9EAlb1wj2JVAr_13kZTYFt5kIe3aSyU_pVJsz6EjPBGMsk8u1tmf62_DF7yzDydc8udb8sVW8OCU2Ggi6yRzj9Hjej-1JFX5Mj0LOGLOFspfZ5YV9vZMcICFnh4Nld5iBv3hr74vknfMJRkEePH92fl2KR8YgPn9feebeL8lUzXAa3WDTMlD3U76yzmPMgZNYRWhaBXjVKq1RXS4Pyzv5ivnDB6_dQqBiN8M_meufbHjil2B1-0P_G8x5cgGknzmc6ZD1ZCxxic7DaqCnq489nwuieFQm_lPsNHTSgj5I3p0qQ3L5b0pnRMY474rBDrxwpMir8LjPL8Ekl46No34ukK1i0yYLjhsfuZ_E_WcSn0ADdHpizPjS9RvyC_vUgAv8X6BKobk3r8qrp-SYBu4Ytx1nPJo7rX9ZV6WroHx5Lt2nY4eVXC0EqhfVYJgGvPxWBlAiPpexhtKmvvaHD0S6KlUsBdozYKlsKrGjr_AM5GVbSQqsAhxx8eWqzKcNFU4AvVVPZIzn8zj-PB6ic1xPmh1EJWnwf96jH-jPlTjInKHbpFUrfkPymt_gIBr37NxBDc3r10w62VB6bGR-QYGWDjuL6KuFh-1xbIwmt1iVtE3WYudBVGKl3WDdAEI24YVFrGtgngs1NJZISLSizKwnctUc7EE5yPDWWAYT0xtufElLSOeN0QbbdcDYLihEsxQph4P4NfbsgOXK_DzeR_1wfW51Nwvto8XnxADdXZJJy5Z2wZS7lEZD63bNiRV-ZkuCShH8iQTjvpR-46CBVivhKcyKjJL-th_CRPC35SKdvhnawfYinQFJUSl3ZXLZUJq1zBrHJkA8yMD-yfkkKgeabCMNvaXMz2epvBqZxqViBh2_NIsqW-3yuuKXZzNzgOuLJY6JwCZXOsnQJzXy7jGI0EgcRQQHZyvTuo8tKvldcrboOY-Gly7i76NiZIL4HHmBhjuqToE3JdvnzT7bqyHFZ6j1zjsPgMO8Q1i6K0bip_6IIcUxHxALan0dmK86H4CGbEMKhRC5h913CsGTOF76038VszZwpzUiJF746rDtOogS3AHHpjDKpYCzMxAcw6kPFy0BpV5dBA0AQ3Ryt2XxXlgqOuDNeVnVCpfGI1vxoAukP5gRMnRpnXH9ZAZvdgpJ-XE7JP2Gctp3PUYVJr3KTmIakW4WHZI8Pnb6_vIxSk7VaeVhVGgeK1NOLm3zcHWmKHokj1O-IogmxHklj2s_AcfF61KsOiyV9o2F__gSDDu6wF9MOg52n5Bwww.usvisascheduling.com/Session3929",
    "ai_session": "XJLgDzCz4bFsYNrPssSKzs|1786733201859|1786733243451",
    "ai_user": "LIBY+JzXZgRaKQFwOpY+pZ|2026-08-11T05:14:24.022Z",
    "ARRAffinity": "2e77d4e3f9d3aafffb21a714a572599d105f6b438db44e062f13b11c719ddc06",
    "ARRAffinitySameSite": "2e77d4e3f9d3aafffb21a714a572599d105f6b438db44e062f13b11c719ddc06",
    "ASLBSA": "000315a33c7d52976037145025442cb05084d205a07ef0fb0e9b1d090c276b403c4f",
    "ASLBSACORS": "000315a33c7d52976037145025442cb05084d205a07ef0fb0e9b1d090c276b403c4f",
    "ASP.NET_SessionId": "blu1lfbrapv01x1bvytq3wlu",
    "cf_clearance": "NEqCf_PRVjOa5ifaxHwVMyjWVFS4O1_.k45gLEBUz_g-1786733201-1.2.1.1-XXIUg8Kfk88XaCnsirBYd.4jsOiCiqWYXaCvzFxXub5RtsKE0CT5v.CLdLooyZKkH2yIA2KP_LD30S02QRM0nFHpxy9tHENbB_WCC_hV4ZNLFIA26TpjjOk_hpLBWLl1DXBqr.0AXaZ85AhRrC0iffPN997RNALrRME.wtmh5t3NwZo.1Xq8ubocjVRHHV8gCrO9pYUF.xvH8WPH_0iaBlr8SfltuXr51DBDhXuqf7L5xr7fn5A9ELSEpfOzq_HJFI0KaSRBdvm0t.e7RaMNQiPIkrrI6o8EUIOUgY4gX98pWYcAqNPt2GdJgqiWnLpeExg7mFgqa4T9fvVE6ShD6BFDOC88Mej6vA.oN244pj0Jdyl0IQFdEkYt.QeSOvxFCGCyhfdY5sJduAWa7UooS7EEN8aRsrAVtMeNLemmC6HW2pYBBRvRiDGD7B6MavFhMCMWMFeBSWkBURBWgWEsHA",
    "ContextLanguageCode": "en-US",
    "Dynamics365PortalAnalytics": "jGfTx8XJ2M2qpED-5io08ExphFHiMKwEHXfgrQfQQdCOv6-MA4JZMA0QuF8veJlyhbzl0FHLtbOONAm8UeMseeInMOnsnwYCZKTFS8NwVbWBd5MlTZumtx2EmF0lsmMeXwh1X0CFdZMg7sHcFBl2KA2",
    "isDSTObserved": "false",
    "isDSTSupport": "false",
    "ppuid": "138baef0-a713-f111-8342-001dd8080743",
    "timeZoneCode": "165",
    "timezoneoffset": "-240"
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
        time.sleep(60)  # Check every 1 minute

monitoring_thread = threading.Thread(target=continuous_scheduler, daemon=True)
monitoring_thread.start()

@app.route('/')
def home():
    return jsonify({
        "status": "healthy",
        "locations": ["Abu Dhabi", "Dubai"],
        "monitoring_active": True,
        "window_days": MONITOR_WINDOW_DAYS,
        "timestamp": datetime.now(timezone(timedelta(hours=4))).isoformat() + "Z"
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
