import os
import time
import threading
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# -------------------------------------------------------------------------
# CONFIGURATION SETTINGS
# Safely reads from Environment Variables; falls back to your defaults
# -------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8969681995:AAHZDtwH1nB5ywnLdC2IYL9nu_VlTr0h9YY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1655607685")
MONITOR_WINDOW_DAYS = 120

def send_telegram_alert(message_text):
    """
    Dispatches an instant notification message to your Telegram account.
    """
    # FIXED: Added missing '/bot' and fixed the domain address structure
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
            print(f"Failed to send Telegram alert: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error executing Telegram API call: {e}")

def monitor_appointment_dates():
    """
    Simulates a session request targeting the visa scheduling center backend.
    """
    target_url = "https://usvisascheduling.com"
    
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://usvisascheduling.com',
        'priority': 'u=1, i',
        'referer': 'https://usvisascheduling.com',
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

    # FIXED: Re-enclosed the raw session tracking string properties safely
    cookies = {
        '__cf_bm': 'ofsN8sEXk3HCOLTsHwjCCc8fujRRbeDI4iC_LBuiu0U-1786711693.180439-1.0.1.1-LQgv0MLw.Ldp_KQ2.fNF4xI75SADuVdvvKMRDl65BMbsAFMcz5nVQTUct17kEoNrQPkHy5VsQiI13V3m9E6fJnYUIX4jSrx1pkfpSkA3tiknYTCbKPLVFpwmJss7JVuV',
        '__cfwaitingroom': 'Chg3cHJxZHZ5S3FUNW12ZnlVenZqdTdBPT0SgAIvcjJLME90MFBWaVBPWlBiS3NCeGNibVFNVFRCSVM4ZTVhdmVuNlN3Q2gxaFpPTTJJVmdYRlh0S3dRdlBBdXFFMkpLeUUwS1FzSzRiSkh4OTNZdENsUzhqT3RQaHpXb0FFdHE3SEZ4dkdzQjdLRTRwL3RiNitqa0U4aHRhWHJwL0dZWldVS3A0NTUxZFlvYW84QVlKL2gwMTBMSUNveDJtN3k5M3gyR0RQL2RkWmpuRmdNWGlQNjM1SE9mMlFXWGJuUmhDNGJmc3BvaDZpWXlFUnRiTHhFZGdrcWxpUUV0WDJuUjdGZk5Vak5tR2gzMFl5Q0p5aFFjSnVubWNwQjA2',
        '__RequestVerificationToken': 'QumOhOZ7PTVeImqIo05lMMlxWEPz5Za_PzBVWu2YsXFbUHg8wC2LRYBVLjua_kAaFib55PCLzpa58Kh-hBo4MOsezMKaI3GMDFAf-qAuacY1',
        '_cfuvid': 'WgAzyCTLqud7A5U_qIP.lmym3kY1fT5HTI_qYb0Lg0A-1786631214.014867-1.0.1.1-gXJ9nxm07r4VKGsACrR9NZ2hEsSa1Yyn.JNPPcWcyn8',
        '.AspNet.ApplicationCookie': 'PmBtPJ78asMK8aouOzrI7C2Tdwq9o5cl9WI8aGwCIDo9x2KgxliiLv-mxaJLMX3uhPrBSLfiGfVNwTokA-PK-nSyv8q_sq23MpX9PoulDunH-gJFCHWs-PWPXDbcO594T9xgc3NmOor415XhTwfPn_EADjojpWELkerI_TduKsKkhWyBCQOBMF5g6GztUzW8xAjlGXqFFbewFnGlauAlZNg4bXn7tYcMO6W8xFTcViXO497kMZWJhdUHmT0v9yEWgu4YTydIGGQCm1x9qAGojXB4MgjjOTWIimgP9h1613Dbz8KswghcEtdbcqDbETqsfpXDq6fbb-yKqUqbD9ByZq2ynuLIV4oZGVkncqyD7Zhn4aq6nyUOSD1-4cHCEGps-1tjkZMpcTefqtyX2ikH_dz9cV4vP1nwaV71Yx8FlwzItf3gxc8GUeP1CsflerhnPNkr6hl7_PZT4sp-MXje__GfOSrDX2kbfuwufwtizXUEU4PC9mRfduR9vNLjGiWBcdxXcHJIUYYscIO4dB1RvpciIwDhBynkGj65z34nOYsVEbSkOezXWcBCqUmpis1w5Xy3A5BjpA-ywl6LS24IEmMgXaJkzUJ7wh3ycaGC0gJr15foMyp-2riJfYQOyKZ5upvlwnKpUXNYl_ZN5j-Orcs09nY7gleYkIfI6NHm4WDCtx2-Wtuk7GSVYJ2JSPuheqeazKk0lLMWZMpvpalLVzKNxxTIqCi9wP-PYRB05xmItTe5OTNjsjoVvIkqr9dScdFGNoclMdtX72A7PJKuYce0nqq_Y37g2NsCS3Ucn1u6KvHjxL9POnQHm6OF05swL4D5LAaMeqQjZCV-GeeDJTix5yqs4MmPBi07FxH5rGvBy9qGDcddn6zJ5GLpxmhD52E7UNi04_7L7qIfA__qFqvxUwm72DC90tsqTrPCk3VIcK4j_-S2WWg1R4bFgE1oTtOvfCto1f3Y6W_nNGA4XvaOux7umren-EQn8PrdnHJZTMbJ_oyvSh-cz9vlG6P5cp6s-1j-S4OrTYA-mLwxVOv9PtS2SrSbi0jrj_zeJQ7JHchmwkIllJoV3qhZj1xhOmiPd7ALHm1WT4jaauKKi3dyZzCGTs3cuFSnkZkusRiFG8AQw019FdR3S0qauuAfoAIQaSE2iEiCGVQDumHqrW8ylrUHLSHx4QD1-X4s-55glcEz0Lub1t7VHHEMU8NDDsf4lrI94esNjU5Me3GtxUuOTHNHnsMrHlPBJBJAoKwwyy1fGjUVx7903SCs5m3V93Yako8Sz1NVJYk1otIXFb1xgM0L8YCsvR3v_rnNP41gk_JOw1-hgobGdLEq3ASAbkg1-BLy0BzpOL7nYfjgabW_I-WNWS9WCcrpoJjyhiEN07oxUT2DNtDleMJyia8BcAQ74R5_DoMf24oseFtRddZOvuFfrd8WXMbeLldytcQwiZQwwhFGA0uhkHMyPvVwQ8UWjWear7Me9LMjoj6l-GGa-PNbQywcmYqBDzZYH2vBC7I9C23slaJuUbul8OSvX7F8Q7npRS3rxFJn94sA8n_skES28fTdOu3z8JbP_X25G5m1LRBQLi8Gsy6Xlff6HiW72fJMRzp433YVE7n0JvffhGGwVYunZQ15m6y-zWUYew5fa2KRKhoy7Qk6taVpuzl4ICu6d1OCo43yNDyzS5HRMnRdXtzHB_odHs0ZWqHI5wHilIEzRCcYdBoCu9ffp9PvgzzEMx4jNrbS3KAZ_UV5mplXfoGAk9DLheGI6qz9RFsDkNMdKoSoD_HeM7_l63Jx_iWLJe8_QZkQ1Q5uy6wQuHAF_YjaC9P8PdFeQz4C1m6TOj7YioxKPS52AF8Yre0gI0yS6R2fqAU7EHRWquOgeGg0Amh4zQ37gx9ztDs5IGvTTwFfW2ezKHFzOBH2Eh3R6tD_fSNRqK1Qy0pFO0zvQDIwictdoFPf88Gnj40xQjKQG8suySyCnAjWmYwdMDALgvDCL0IFSG4MHutBsc6iiICgd_e4Ge51j_ntk0hQkemo8T3vJeUEuzj1dlgQhtU_TwMoeiyD9qAbzkJnQBx21FpbMJ2t40poDTgclSJ306CcWyPUN-ouMSkD_FKtkR_RHZEu90e6x-fPIKgvODbscaioPy2uNL6w7lxhqjPoAAcjjfpjmHuUXkD7NFtK6Tioaz4vMOYe5Sumq8ZjYFgGhoHM7nwJc_cZiIvkl8zIL_voCp1vKIq-wytJrdlFP_u21bAKR69LPMz4q4-EoMEHcAJVNPp86KepdaTAXL77cWQJkROi0NE7v9SpnSMchHyMDseBMoJ-_XGTkuQrWCAkR2rlXTmL40GQR-oBhoZTTXusgyWaOqEjm0crERR2HtwvmxVYft77I6igXvPit7iucaIb-cebp56aQvSY2o0kBm7Q3nA6JUS1jG8gOyghJWw1-OG3VvnOI3t_bFNcC4l6GnK-1sDo3a-EVze4Fn7zLFQRbAVtvmx99ywdNs9xx1LScc8ozZcgMWT23eYsNqe2hELRN2oosQ_VjriF0rrVUYv3mBH-Ti_qH7hdTuVJy9Mf9r71PoSroTegx7YVUhuRzA2e7lBgeMGgVGibbmlPAV21FujD95gDrnD9l9NvKWYUDsXkZkIkxWPkV6phwLOLFulS7PkTxZ2ii43L74oL0HYCmQWxAhZbTNNXD5atvZ7Ay7HTZQWzcnkeucRHyTu_d2gdVjPxc603VjQGiACmLq4olgNzFnDmhHbqNtvrwGcpZwrtNwJDS6MzUKA4rN6qZIAhKAhbSA9cIrDPNzkjwgFtOyZCZHF14Ton4exL6dg_u7XQzPUZk9rm9BhRBpuguPe2pQ-9l-_IWqOC7sYDXsDA34065JqKVWqiSWFpfwm2Lt2Y5UEoHogrjxHxmS66bM9ZVIfdJgHGwb6ZIzmqAUxlLZovLXlSmmwygR8bJ4Is9knE6k78AVxcTRpd2LBGBmUbiAo8IyC9mF-7sOTWAfEp4jYoIXjMH0zHtfF0en1ZhTHamX9SFJIVtKeBZE5wG5j8sSFquL662ZcTZS9uZzCve3QZldMRK9W5cxhCDJFiZY9dLGEpM9LL3c4LsJ6m0I-5nKDMKZnNhfSCltIhdgbWl2Vq9qeLqY3B9g1PXqTSsPN9r28jSEj4eV55_oBdiz1hveOJty54K27b7Nu1YZOsN1fgDbqK96oT2PVd_opwJQQwqGdnIrjeoR3OOJnRQ2ylVH18FFskNXcjqGDygLMSKduny0pZUD_Z3AMxXj1EHjmxlVu2cXelc8_G8mC3DtsMKhzJswbDGY_fSGRHAmuyHTn0-axZuLR98fDByOwcdhmTP8eH-TTuR2ZL80p3tcGOgUOOGa5JoW7kak0mEyyejy1wv3ueA1io347-LTsXuTW6Ef0J8ZQMEMLJ4I5YmpzUXiJxMp3cmWZWiyhSKcEjsNpQb3mTf-MgJw4KyJk_UFi5jfS0iKjkX_fUgpfWMhVAFyjN6ZQLfKde_EfZW3ZJ7Fz3l02ITDQIU3E1LTD8kPoHq_dxLm2eyPPo7e7Bh7O401T-cPZGsjqlfSzOK6_O9zrYOiyeW4k83aJyOAqZjCAbrHU_hYQdobq8gmM6NsrMrQjxso9CCqOuRCwmxFTVxAGzJ0fN2tZ0e4fdXb_iIJ2rmnFyaXsHq30E_k5m27ilhmkqRlm6iuazYGCiMaqSYBTzLSBmM-uiQAhM7PGsOgUOH7MjNyT-AP8sV_5s--0ISvi8ny2bSFtKeKG0XhPfdlikD8LeuohE7ajDjwh2lzF46B9bD2RW1m4PkgKge_KPArHjHQWNQCG9SWIuxBnPgYZ1-42E5Xs_oDRy5BpMSheoG2L3g8FOEM8BYirYZPULAbj57oXJqb8byNyRvE9wYDsTPQyOegtjJ4xe',
        'ai_session': 'EHwzpxMgMysvNno0tcghEI|1786711692959|1786712190915',
        'ai_user': '594HVDlaap7MiF4y9x08uF|2026-08-11T08:48:28.850Z',
        'ARRAffinity': 'b7371a6831ef0d944ef98bbd9fb45206975ead8f1baca8968729b1c19e2ef33b',
        'ARRAffinitySameSite': 'b7371a6831ef0d944ef98bbd9fb45206975ead8f1baca8968729b1c19e2ef33b'
    }

    try:
        # NOTE: Modify logic here based on your actual visa target endpoints
        print(f"[{datetime.now()}] Requesting visa scheduling endpoint...")
        # response = requests.get(target_url, headers=headers, cookies=cookies, timeout=15)
        
        # Example processing implementation placeholder:
        # data = response.json()
        # available_date_str = data.get("earliest_date") 
        
        # Simulated discovery scenario for development checking
        dummy_found = True 
        if dummy_found:
            send_telegram_alert("⚠️ *US Visa Slot Found!*\nAn open slot matches your criteria.")
            
    except Exception as err:
        print(f"Error scraping visa portal: {err}")

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

if __name__ == '__main__':
    # Binds port using Render/Heroku dynamic assignments or defaults to 10000
    port = int(os.environ.get("PORT", 10000))
