import os
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# -------------------------------------------------------------------------
# CONFIGURATION SETTINGS
# Replace these strings with your actual Telegram bot tokens and user IDs
# -------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = "8969681995:AAHZDtwH1nB5ywnLdC2IYL9nu_VlTr0h9YY"
TELEGRAM_CHAT_ID = "1655607685"

# DEFINE THE RELATIVE MONITORING WINDOW IN DAYS
MONITOR_WINDOW_DAYS = 120

def send_telegram_alert(message_text):
    """
    Dispatches an instant notification message to your Telegram account.
    """
    url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
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
            print(f"Failed to send Telegram alert: {response.status_code}")
    except Exception as e:
        print(f"Error executing Telegram API call: {e}")

def monitor_appointment_dates():
    # Target URL Endpoint from your US Visa Scheduling session profile
    target_url = "https://www.usvisascheduling.com"
    
    # Exact raw browser headers from your session intercept
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://usvisascheduling.com',
        'priority': 'u=1, i',
        'referer': 'https://usvisascheduling.com/en-US/schedule/?reschedule=true',
        'request-id': '|9c0ec741b23e41ec84aa9df677081634.825ea0ee5823492e, |b97a717ce629404ca91822329146f7da.a7b1198bc7984de3',
        'sec-ch-ua': '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"151.0.7922.109"',
        'sec-ch-ua-full-version-list': '"Not=A?Brand";v="99.0.0.0", "Google Chrome";v="151.0.7922.109", "Chromium";v="151.0.7922.109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"19.0.0"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'traceparent': '00-9c0ec741b23e41ec84aa9df677081634-825ea0ee5823492e-01, 00-b97a717ce629404ca91822329146f7da-a7b1198bc7984de3-01',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    # Live static authorization and validation cookies extracted from your profile
    cookies = {
        '__cf_bm': 'ofsN8sEXk3HCOLTsHwjCCc8fujRRbeDI4iC_LBuiu0U-1786711693.180439-1.0.1.1-LQgv0MLw.Ldp_KQ2.fNF4xI75SADuVdvvKMRDl65BMbsAFMcz5nVQTUct17kEoNrQPkHy5VsQiI13V3m9E6fJnYUIX4jSrx1pkfpSkA3tiknYTCbKPLVFpwmJss7JVuV',
        '__cfwaitingroom': 'Chg3cHJxZHZ5S3FUNW12ZnlVenZqdTdBPT0SgAIvcjJLME90MFBWaVBPWlBiS3NCeGNibVFNVFRCSVM4ZTVhdmVuNlN3Q2gxaFpPTTJJVmdYRlh0S3dRdlBBdXFFMkpLeUUwS1FzSzRiSkh4OTNZdENsUzhqT3RQaHpXb0FFdHE3SEZ4dkdzQjdLRTRwL3RiNitqa0U4aHRhWHJwL0dZWldVS3A0NTUxZFlvYW84QVlKL2gwMTBMSUNveDJtN3k5M3gyR0RQL2RkWmpuRmdNWGlQNjM1SE9mMlFXWGJuUmhDNGJmc3BvaDZpWXlFUnRiTHhFZGdrcWxpUUV0WDJuUjdGZk5Vak5tR2gzMFl5Q0p5aFFjSnVubWNwQjA2',
        '__RequestVerificationToken': 'QumOhOZ7PTVeImqIo05lMMlxWEPz5Za_PzBVWu2YsXFbUHg8wC2LRYBVLjua_kAaFib55PCLzpa58Kh-hBo4MOsezMKaI3GMDFAf-qAuacY1',
        '_cfuvid': 'WgAzyCTLqud7A5U_qIP.lmym3kY1fT5HTI_qYb0Lg0A-1786631214.014867-1.0.1.1-gXJ9nxm07r4VKGsACrR9NZ2hEsSa1Yyn.JNPPcWcyn8',
        '.AspNet.ApplicationCookie': 'RxgqEkpLD-5Vg71v4t2xvT4KPogshs6OSNPXE6m1AYCwfnERIUX7D9ff6TRyz5rJKX5cBppxxz6nGSzJAxYHt8pscIagP5J200gYjphpDAFarmtb6ImLh7uTtWYlcVslvbMkwxQCRZB9Rmr7WOLamQ2epZOJF9vc-D98SE-In0OLYaf-60AZb-NQVJrCS7WBlqkxnPbINYMuczK1mr96nklsSQeRyCo1PEKfz0O0CRLl30befkH4OR1xrk2ZEt8g1yxvE7OjzfglZ1m7sfNnIGZDy3hUsmgtNYwi3dFFb7Zq_k_uhnjA8iQF21GKd4lotS5T0I5lNiGHNUPCJFXE2TcpEyNh4H0gIvXOrvXsX-IlLI10dhDzTpRgQtsjewG5_reh6zKenOkqpeT6l8V4oZc8vT8HXlxnWx-LVHsiATdkvm7mNzqAS6K8sBQZsEAiiX0K6sl_TdEh9IcWrTLwb1fHYeGk1gpNRyOooJYmofcyHOUczldFWuqlmnKQFI6ZJLgHp558sLzPmThxeciCqJXSwTJj8jj3O2H_dlIDXA9hn9qIue5ktzsc4s657oN0pfIKI1OqZOWsNNOLc-yDoBWhT9SxLDmA9yq2KzcX-iY5b0ez2buKRsegrCih1adSKXdOytD2RLxbh4jfXh_UVQwkNmrXa-gbhXP5XZXeG7b9WAqvOv4P2-pMe7JoPBty_vzzT_5kHvezxxH5Xnm_1nhD2sKAN8V4FDiiRFNEQWlnKA4k5dQdgIMyFxLN1VWjIAaC8qCkVONg3SqvGbyPG8G5UcX2YvqLGI9HPcPozhokV1C5x5QauZb8rfRJO3ASeNzvpRtVdVs90405mW6xzW_WeRn07IHHMtt4RnTKrpShkIN1plVuHu0SZ7Y60pdT7TyNesVeRPVLqIVIhbNl520qXl0gL5250eIhb6MFv6gFpnuxu97BZt8kjwXhW1X8Q6D3rFGIJGfzcF7Qg82LQUXuq5PzNl3Y7uWwAV--agZfCe9WM-8Dm48VtUeVzWhoo73LSsSZyeSGxEbueidVHEqMsqS8IrTlNyjmzrfAEx5ECAClRewxHLB7hwUSUh80YGXt_o1yqiN0ZVcwX1m3jMqYfz6WWpw3WE_jd5cymPiAzOMYULTBaSxGKfYS0Ft_gHGq6-9pO8qSYq7ygNkRFDwGh-U_tf4a140IErZPifzg3g6xxHSro44B48XyQjjx4edU3oC8RiRt_7HFV5FXkVu51SPXYNxNXE83mJF2nZ7C7pFOP7NAD1rFT2N9SQCp9yPT-MynxnG3LyZ731yu4STRlqzovsG7m9pch5eSPBGtN0vCG5obAwnMyzpbofqmqf1MJV0BRp2vOg5SFWBNjpEKDwMLzSg2030a51DvSoiYKTILlNULlhhG2NLocArFPJZaRWluU88uh7W9SL97StbrKvOsxIKkKNVyuZ88U2xz3xMtJiASrHSE1_RqY3fMJAweTK0U5oRZxX-Ptgwq-STePbEIZeeJMNswTnd0BFCP75DAGIaLbifIZH3FsKZK_2axNj3TrGHfj6-J8kiGanKrLEAeDmmqiVU_Ug70F7oIqA5oOxeBb-GpON_YoeN2y2RihaW_ik7BNQ1W7pWUghdSSXtomAGuaIexM9vEChSq46yRoaAvfpvswiq5xusu0xo99LHcwcoxO91KvTLv2PYWScKZ4oK_z43lWFphxJ2PpWtTVA-8Xiqr0SJe7phcwgaGy1tavB8REXnafLme07eKAUIXxjWjYGeO6whyaviUZsXVcrktI-vHy69kVKAvNrDvenWq4OtEqmkUx08C0_QfgkT6-25AgTt9w5V0aw0gselSpP3ng9c4nScyTNKedZ1xEmdh4Po7ejFLUypCMu35h-0UYhGWKY_Dwbg8YWwtk6Bn5QR5VG0IAxNXnwqDP-7kxQKsf57UP70mcsvvPh_kPmfx0PNFY0EcFoPjDhQtnZ6cA7JsV9VQhs7D2ubq_JyoAOeS2v5Rg0fV0v27fkp0w6cBV6gWJ2AwwC-iK8oQQTt3sCVwUwO6_CZQFQHMvDJ9bMbEY00HjNM5GPDWxvZMqpakcbmxI-OS46tSLs1EUhKTEmAAr6V0WX7xhQc_K532G3W_jV8n7iNoWn7DgPu_YwgU_bRklQZUngBhl-sQSYqKtmcLF28scKU_1x4KvB5ijSfxBtPGiSWrQt6ZjL8sFXVBkRmS5oRS_tAWGtOjtxhZF7XTRAUfJ-ynk8Lone9ztO4sw5TbiMVWF7JVo-lYo6Dxe6JlRwPNVL9lFD6_C1S9PlwdbIZMiYnuDiNhisLPS1bt9K79OMrkZlR0V_FUtA5WhcTXLZ6rPAP2FktIyGE2RnAWDTa74vFsUmwdcs6eVM0dWCiortXYDspGndDeJHnTtMgK_vzkDJKyBsdb4eENGa0OXZCZcdgcpY6fpEydB_OXQWy08_T4gg3CgwtKpsl0McXbjNuhYqsYDso4NmkE7kPa54SOaK1DS-olg_0LemLPX5h9IISNEtGwa9GmPl8xPtHrpYRmR9yQPmJOKRbO9VJlH8V2Qi9AMkyAkydT2zIO-z55BQNSWzzoHp4KJFt83NDpqwsZAPmIp38U0DMtQ4iZDMWsFhS6BKudvNE8U3JGtozsn0ildDo1pX6LTXoYjJnMBkc2hfhVk05CJAfVdUn2N5C2Hg5BzYF1vW5ogjW1RU5lREA11ei_tI4zH8sHjAMM_DU82SOxCmYbVCh3pQh9MasbJpHlBCGsKKbCtBjAHf_8BW_hlkXcsdDwellVhf2lLtBWut9ZdWdEowYdvo0BKB0JDPmfCHpGVzSEDCi28RGk4mqhgaO-c9MrE7vIXUUw050NUY_QWaHGySwfDD2tS5j88kCBhLnxcOEfsvOnwrAB6ti4Hz3piBT8qf2QQzE3k6KFPXN51e-tJlsHp0i3ETkE5Hd4WhE86Dl6SQ0dqzYtwCXXoAv8yxsi4mQeIm49bdCKW1JnplFYtVXbJIdLHdX1maPXR8FH77bj4ffQCxfqb7p_l3viO2RmXisCaDSX5FTu4dojsHP-u-TN61ho0Z_2OXe3kAFERpuik8-ZuAhaNuontZLcrJ1dlCKUu3l1XazZ7IopmX-fdyVLvrMCWxKLmrozl6CqzqZLIci-o0IIpcexFdRgWC4bgOefvSPzcLNmKIOevv2huud1n9OPld1v7Sdi3RgOcVazrBvkGxN3yZo9ZDl5GQrzRc4dQQv_0Yo3yt7INJ26jUfjojzhUTGgotjTsUqnh2O_tyrlTG_tEz_xxL4VB_Am-gMLzTJbtjqVt40AEKB0JlTIfC3Rryd44LtA99lhQEivuKqNs7NWaa-ai3f6oJNT9iK2m0BKeH48bVVdncSQjZNrYiteL3ZzuwwzjiJRRnq48EMcCv9Htqpf4TlQWO52E-JjJCO3mUL9RhBFKr4IeVnuZrXfv3m3tEHCowpGRs2nH0ennetRCBAOxmtSBnaPv4oKCuCLCiZ8zdopyfBo7lJIMyGVg_nQSuTHGEri8U4GanIxiV7UlW6Zn07dQB_mcuV5ULez78na5q4VMkwDh7FsvJNrS4RrRkiZseIg4mjRBym9XkDfUBQImHBEm7scESb7jcZhj4GJmV_HcsZbJWdo25ylsUP7Pp-WN5eamcvloszrBVlqlDzcB6vnt0aMRSfAv61gzkNi1l9nRg1QfHhkMpvtTWtAk2Z5M-1j9YkOjm4mBHA_N1rtxN-aRC1TlXiwYsqDNjS8_NrncXZvGJnhVbMYbTtDFVnWFtrBzqSJWrCW-LpXUE2DAwlfCJ29RuUkM8mk6-Iz-pvzBLjIWJkmebli85PkA2KqV139EFpNWSl_c2nfflq2X-zfLymWEhVO8w63o_l8HAUFaNM',
        'ai_session': 'EHwzpxMgMysvNno0tcghEI|1786711692959|1786712190915',
        'ai_user': '594HVDlaap7MiF4y9x08uF|2026-08-11T08:48:28.850Z',
        'ARRAffinity': 'b7371a6831ef0d944ef98bbd9fb45206975ead8f1baca8968729b1c19e2ef33b',
        'ARRAffinitySameSite': 'b7371a6831ef0d944ef98bbd9fb45206975ead8f1baca8968729b1c19e2ef33b',
        'ASLBSA': '000315a33c7d52976037145025442cb05084d205a07ef0fb0e9b1d090c276b403c4fbcd875cb0b0decde9dc03bedde70fc342484b9ebaf1c458679ad52374dc0ac1b',
        'ASLBSACORS': '000315a33c7d52976037145025442cb05084d205a07ef0fb0e9b1d090c276b403c4fbcd875cb0b0decde9dc03bedde70fc342484b9ebaf1c458679ad52374dc0ac1b',
        'ASP.NET_SessionId': 'nw0pfxkpdyymetvkw1v352gx',
        'cf_clearance': 'ukAIOKwQgrVhqgUGcqOWhTM4XYGjDhSYdjZ6T1Hj3iw-1786711693-1.2.1.1-7GoT3_Oo8jF4hlWk.TNFBq2XyPBr30W0M7YP4_hnAgOujpiB.Yzp8hIpVgv23wy5gBP2eoO261ExB62.U7OvSTem7Hl3QQ.ocuZqeAvLpYBldLunNEkZ_N.BNBd.8llFqj8l66xNix0aAYeCM.RwNCIPQCbHBLTk8X4hR_1e.76uiJmwUZ3E65KwcQ_oQ.Zf1XN2tdjZZVuAh82nLOENPNmMyjJb9JN1e8AjKEC1N_glcBp7O.EGAj9pdCfUJZo6QfuyRfirHqjXBI8hnVablC8UVvfA_4MIHXLw6Hb8Rm9GcnysJGYitaUoD41ibR_dYdckiwamwT1HdN6wjbVcAX3qgov6l8mmLSQiHkC0z9I.nCaRVqkZJov7UGzzFB3iGWYTsohfgXwVfIeKNS5luBNoOP6s2J.pFoZOx9ABj7xyml7Jrvkx_wZRdb2knemg9zg_gbartY3Iw8deQa16Ww',
        'ContextLanguageCode': 'en-US',
        'timeZoneCode': '165',
        'timezoneoffset': '-240',
        'isDSTSupport': 'false',
        'isDSTObserved': 'false',
        'Dynamics365PortalAnalytics': 'oyADkGFFKP5WQ04byo5lwqiKFAuefZ9tVnk09K66vy-jK2JFmXPMtMAhC1yIJVHWCvun7Ey3nZsMYAPM7stp0uwVf1w2xFX3oQpC3HyzwgXXDp6enghsqIW2fwkM4ewn1e2GIoo6RHUsBKJk1Lv3VQ2',
        'ppuid': '60d59ff9-4212-f111-8342-001dd80b70e9'
    }

    # URL-encoded query body data from your session profile
    payload_data = {
        'parameters': '{"primaryId":"6495c89e-4312-f111-bb46-001dd80aa47d","applications":["6495c89e-4312-f111-bb46-001dd80aa47d","53a41f5f-4412-f111-bb46-001dd80aa47d"],"scheduleDayId":"","scheduleEntryId":"","postId":"962fd063-ccb5-ef11-b8e9-001dd80637a9","isReschedule":"true"}'
    }

    # -------------------------------------------------------------------------
    # DYNAMIC TIMELINE CALCULATIONS (Exactly 120 Days)
    # -------------------------------------------------------------------------
    print("Executing automated rolling interval calculations...")
    start_bound = datetime.utcnow()
    end_bound = start_bound + timedelta(days=MONITOR_WINDOW_DAYS)
    
    start_date_str = start_bound.strftime("%Y-%m-%d")
    end_date_str = end_bound.strftime("%Y-%m-%d")
    print(f"Dynamic tracking window range calculated: {start_date_str} to {end_date_str}")

    try:
        print("Pinging US Visa Scheduling API calendar grid...")
        # Send the POST request containing your exact payload and session cookies
        response = requests.post(target_url, headers=headers, cookies=cookies, data=payload_data, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            days_list = data.get("ScheduleDays", [])
            
            if days_list is None:
                print("Server returned an empty schedule dashboard frame (ScheduleDays is null).")
                return True, "No days active."

            # Extract date values from target tracking dictionaries
            raw_dates = [day.get("Date") for day in days_list if day.get("Date") is not None]
            print(f"Total calendar days returned by server dashboard: {raw_dates}")
            
            # Filter array loop checking for elements inside your 120-day timeframe
            matched_dates = []
            for date_text in raw_dates:
                try:
                    # Parse standard US Visa string format (YYYY-MM-DD)
                    current_date = datetime.strptime(date_text, "%Y-%m-%d")
                    if start_bound.date() <= current_date.date() <= end_bound.date():
                        matched_dates.append(date_text)
                except ValueError:
                    print(f"Skipping mismatched string format conversion: {date_text}")
            
            # -----------------------------------------------------------------
            # TIMELINE NOTIFICATION TRIGGERS
            # -----------------------------------------------------------------
            if len(matched_dates) > 0:
                print(f"🚨 TARGET ENUMERATION MATCH: Found {len(matched_dates)} open appointments!")
                alert_msg = f"🎉 *US Visa Appointment Dates Available!*\n\n"
                alert_msg += f"Tracking Target Range: `{start_date_str}` to `{end_date_str}`\n\n"
                alert_msg += "Open visa scheduling dates detected:\n"
                for date in matched_dates:
                    alert_msg += f"📅 *{date}*\n"
                alert_msg += "\nLog into usvisascheduling.com immediately to secure your spot!"
                send_telegram_alert(alert_msg)
                return True, f"Alerted for dates: {matched_dates}"
            else:
                print("Scan completed. No calendar availability matches your 120-day limit.")
                return True, "No dates available inside range."
        else:
            print(f"US Visa server returned an unhandled error state code: {response.status_code}")
            return False, f"Server Error {response.status_code}"
            
    except Exception as e:
        print(f"Error handling live data transmission loop: {e}")
        return False, str(e)

@app.route("/run-booking", methods=["POST"])
def trigger_endpoint():
    """
    Automated Cron entrypoint. Returns minimal JSON layout payload tracking 
    structures to guarantee Cron-Job.org execution profiles never break.
    """
    print("Cron-Job.org automated wake-up signal received. Running 120-day visa scan...")
    success, message = monitor_appointment_dates()
    if success:
        return jsonify({"status": "completed"}), 200
    else:
        return jsonify({"status": "failed", "reason": "internal_error"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
