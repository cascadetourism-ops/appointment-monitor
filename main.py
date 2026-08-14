import os
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# -------------------------------------------------------------------------
# CONFIGURATION SETTINGS
# -------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID_HERE"

# DEFINE THE RELATIVE MONITORING WINDOW IN DAYS
MONITOR_WINDOW_DAYS = 120

def send_telegram_alert(message_text):
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
    target_url = "https://usvisascheduling.com"
    
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

    cookies = {
        'ai_user': '594HVDlaap7MiF4y9x08uF|2026-08-11T08:48:28.850Z',
        'Dynamics365PortalAnalytics': '5ttfoMuzzn-07C8cgItxojNaKa_knbsEoqfZJuGGqFKGRYa5kTPR4_NbewCHgpPVmzdSxi5eDYzi1Y5chRiyq7f6Qi2JoQYrv92krC6suk5AQj_6IDIN-dRj0e6NdEa4N7eBhwm2GM_71H5tYnNJVg2',
        'ARRAffinity': '3cd56cc2b0db1eb96628d469bd51aadad1fbc26e09c3764d456c7d963180807d',
        'ARRAffinitySameSite': '3cd56cc2b0db1eb96628d469bd51aadad1fbc26e09c3764d456c7d963180807d',
        'ASLBSA': '000315a33c7d52976037145025442cb05084d205a07ef0fb0e9b1d090c276b403c4f',
        'ASLBSACORS': '000315a33c7d52976037145025442cb05084d205a07ef0fb0e9b1d090c276b403c4f',
        '_cfuvid': 'WgAzyCTLqud7A5U_qIP.lmym3kY1fT5HTI_qYb0Lg0A-1786631214.014867-1.0.1.1-gXJ9nxm07r4VKGsACrR9NZ2hEsSa1Yyn.JNPPcWcyn8',
        'ASP.NET_SessionId': 'bd0lhjxtcateo1zgbzwuh3e5',
        'timezoneoffset': '-240',
        'isDSTSupport': 'false',
        'isDSTObserved': 'false',
        'ContextLanguageCode': 'en-US',
        'timeZoneCode': '165',
        '__RequestVerificationToken': 'KlS77Xp4wGeTSmgu-5rOlVeDlhC5LY3FuOzLtse0-zjFuWExy_MjZdy3NIQySiR-kk6giC4I-4gMNtuDCW109qHn0Sa-HO_U5UVq79grMEY1',
        'cf_clearance': 'TOUOjssYFKXs8nc_4wS66aCvsMrpjUugmElkVdAKRCw-1786695019-1.2.1.1-pYxvN.FfZtCVWCE4IzsgKYCmt9yeI9uUhgidSoD.J80yxu.GSs0LknzkM.2fce2stBVp6MeJguq.hTCgHijHzm2CU8asBjr7VN9ea3xjkkJT1WdWSPM.ziuOQaxK85JBCGUpoEJc2gPZDgVO4Qs5zUj1Ke1HAKI6VFFRAlrnuvtBSaAJ4oGdDa6uGGOchr6E2VzbdIX_QgarOk1bxSJcSfIfPWFToDk4iUgs3zxuUpbU4nM4W0gXypHPcfWzRgQCNWUGIdhbU4zGScBrlqy20MT6Ynwb2hsJb11gk.GOx5Btw_32vcCbPYgv6VV.l6LbfzQ5Iyc2uRNAcVTZ8s2l_5p58pAeP1DYo1mzxnW9yjDkUIXo8guodjMicWfQ5Dwsp7xmxqsTKWFqOXFHmQq.cO6d.uvHMq8hvo0yCRbVCy7P8pSpouYUtrS68eIoaxl14bqqIt0GTcKw4Omr1U1aSw',
        '__cf_bm': '5wJ9utqUy9e1zmEoQ4K.gtcy6EsiJWoUObnXHX9nf9E-1786695019.603141-1.0.1.1-Q5RdoXQKSFSmQFnu5i3KAznrZ3GEF7C3gbxwHRlS7mx7UwVT3gB3.xCBzuvOG35yFNe5Ws.WN7lPscMzQUBsskAD6JMuUSvEo11_5EkWDDoaAl1OCGrbZfHLrlv5yivz',
        'ppuid': '60d59ff9-4212-f111-8342-001dd80b70e9',
        '.AspNet.ApplicationCookie': 'PmBtPJ78asMK8aouOzrI7C2Tdwq9o5cl9WI8aGwCIDo9x2KgxliiLv-mxaJLMX3uhPrBSLfiGfVNwTokA-PK-nSyv8q_sq23MpX9PoulDunH-gJFCHWs-PWPXDbcO594T9xgc3NmOor415XhTwfPn_EADjojpWELkerI_TduKsKkhWyBCQOBMF5g6GztUzW8xAjlGXqFFbewFnGlauAlZNg4bXn7tYcMO6W8xFTcViXO497kMZWJhdUHmT0v9yEWgu4YTydIGGQCm1x9qAGojXB4MgjjOTWIimgP9h1613Dbz8KswghcEtdbcqDbETqsfpXDq6fbb-yKqUqbD9ByZq2ynuLIV4oZGVkncqyD7Zhn4aq6nyUOSD1-4cHCEGps-1tjkZMpcTefqtyX2ikH_dz9cV4vP1nwaV71Yx8FlwzItf3gxc8GUeP1CsflerhnPNkr6hl7_PZT4sp-MXje__GfOSrDX2kbfuwufwtizXUEU4PC9mRfduR9vNLjGiWBcdxXcHJIUYYscIO4dB1RvpciIwDhBynkGj65z34nOYsVEbSkOezXWcBCqUmpis1w5Xy3A5BjpA-ywl6LS24IEmMgXaJkzUJ7wh3ycaGC0gJr15foMyp-2riJfYQOyKZ5upvlwnKpUXNYl_ZN5j-Orcs09nY7gleYkIfI6NHm4WDCtx2-Wtuk7GSVYJ2JSPuheqeazKk0lLMWZMpvpalLVzKNxxTIqCi9wP-PYRB05xmItTe5OTNjsjoVvIkqr9dScdFGNoclMdtX72A7PJKuYce0nqq_Y37g2NsCS3Ucn1u6KvHjxL9POnQHm6OF05swL4D5LAaMeqQjZCV-GeeDJTix5yqs4MmPBi07FxH5rGvBy9qGDcddn6zJ5GLpxmhD52E7UNi04_7L7qIfA__qFqvxUwm72DC90tsqTrPCk3VIcK4j_-S2WWg1R4bFgE1oTtOvfCto1f3Y6W_nNGA4XvaOux7umren-EQn8PrdnHJZTMbJ_oyvSh-cz9vlG6P5cp6s-1j-S4OrTYA-mLwxVOv9PtS2SrSbi0jrj_zeJQ7JHchmwkIllJoV3qhZj1xhOmiPd7ALHm1WT4jaauKKi3dyZzCGTs3cuFSnkZkusRiFG8AQw019FdR3S0qauuAfoAIQaSE2iEiCGVQDumHqrW8ylrUHLSHx4QD1-X4s-55glcEz0Lub1t7VHHEMU8NDDsf4lrI94esNjU5Me3GtxUuOTHNHnsMrHlPBJBJAoKwwyy1fGjUVx7903SCs5m3V93Yako8Sz1NVJYk1otIXFb1xgM0L8YCsvR3v_rnNP41gk_JOw1-hgobGdLEq3ASAbkg1-BLy0BzpOL7nYfjgabW_I-WNWS9WCcrpoJjyhiEN07oxUT2DNtDleMJyia8BcAQ74R5_DoMf24oseFtRddZOvuFfrd8WXMbeLldytcQwiZQwwhFGA0uhkHMyPvVwQ8UWjWear7Me9LMjoj6l-GGa-PNbQywcmYqBDzZYH2vBC7I9C23slaJuUbul8OSvX7F8Q7npRS3rxFJn94sA8n_skES28fTdOu3z8JbP_X25G5m1LRBQLi8Gsy6Xlff6HiW72fJMRzp433YVE7n0JvffhGGwVYunZQ15m6y-zWUYew5fa2KRKhoy7Qk6taVpuzl4ICu6d1OCo43yNDyzS5HRMnRdXtzHB_odHs0ZWqHI5wHilIEzRCcYdBoCu9ffp9PvgzzEMx4jNrbS3KAZ_UV5mplXfoGAk9DLheGI6qz9RFsDkNMdKoSoD_HeM7_l63Jx_iWLJe8_QZkQ1Q5uy6wQuHAF_YjaC9P8PdFeQz4C1m6TOj7YioxKPS52AF8Yre0gI0yS6R2fqAU7EHRWquOgeGg0Amh4zQ37gx9ztDs5IGvTTwFfW2ezKHFzOBH2Eh3R6tD_fSNRqK1Qy0pFO0zvQDIwictdoFPf88Gnj40xQjKQG8suySyCnAjWmYwdMDALgvDCL0IFSG4MHutBsc6iiICgd_e4Ge51j_ntk0hQkemo8T3vJeUEuzj1dlgQhtU_TwMoeiyD9qAbzkJnQBx21FpbMJ2t40poDTgclSJ306CcWyPUN-ouMSkD_FKtkR_RHZEu90e6x-fPIKgvODbscaioPy2uNL6w7lxhqjPoAAcjjfpjmHuUXkD7NFtK6Tioaz4vMOYe5Sumq8ZjYFgGhoHM7nwJc_cZiIvkl8zIL_voCp1vKIq-wytJrdlFP_u21bAKR69LPMz4q4-EoMEHcAJVNPp86KepdaTAXL77cWQJkROi0NE7v9SpnSMchHyMDseBMoJ-_XGTkuQrWCAkR2rlXTmL40GQR-oBhoZTTXusgyWaOqEjm0crERR2HtwvmxVYft77I6igXvPit7iucaIb-cebp56aQvSY2o0kBm7Q3nA6JUS1jG8gOyghJWw1-OG3VvnOI3t_bFNcC4l6GnK-1sDo3a-EVze4Fn7zLFQRbAVtvmx99ywdNs9xx1LScc8ozZcgMWT23eYsNqe2hELRN2oosQ_VjriF0rrVUYv3mBH-Ti_qH7hdTuVJy9Mf9r71PoSroTegx7YVUhuRzA2e7lBgeMGgVGibbmlPAV21FujD95gDrnD9l9NvKWYUDsXkZkIkxWPkV6phwLOLFulS7PkTxZ2ii43L74oL0HYCmQWxAhZbTNNXD5atvZ7Ay7HTZQWzcnkeucRHyTu_d2gdVjPxc603VjQGiACmLq4olgNzFnDmhHbqNtvrwGcpZwrtNwJDS6MzUKA4rN6qZIAhKAhbSA9cIrDPNzkjwgFtOyZCZHF14Ton4exL6dg_u7XQzPUZk9rm9BhRBpuguPe2pQ-9l-_IWqOC7sYDXsDA34065JqKVWqiSWFpfwm2Lt2Y5UEoHogrjxHxmS66bM9ZVIfdJgHGwb6ZIzmqAUxlLZovLXlSmmwygR8bJ4Is9knE6k78AVxcTRpd2LBGBmUbiAo8IyC9mF-7sOTWAfEp4jYoIXjMH0zHtfF0en1ZhTHamX9SFJIVtKeBZE5wG5j8sSFquL662ZcTZS9uZzCve3QZldMRK9W5cxhCDJFiZY9dLGEpM9LL3c4LsJ6m0I-5nKDMKZnNhfSCltIhdgbWl2Vq9qeLqY3B9g1PXqTSsPN9r28jSEj4eV55_oBdiz1hveOJty54K27b7Nu1YZOsN1fgDbqK96oT2PVd_opwJQQwqGdnIrjeoR3OOJnRQ2ylVH18FFskNXcjqGDygLMSKduny0pZUD_Z3AMxXj1EHjmxlVu2cXelc8_G8mC3DtsMKhzJswbDGY_fSGRHAmuyHTn0-axZuLR98fDByOwcdhmTP8eH-TTuR2ZL80p3tcGOgUOOGa5JoW7kak0mEyyejy1wv3ueA1io347-LTsXuTW6Ef0J8ZQMEMLJ4I5YmpzUXiJxMp3cmWZWiyhSKcEjsNpQb3mTf-MgJw4KyJk_UFi5jfS0iKjkX_fUgpfWMhVAFyjN6ZQLfKde_EfZW3ZJ7Fz3l02ITDQIU3E1LTD8kPoHq_dxLm2eyPPo7e7Bh7O401T-cPZGsjqlfSzOK6_O9zrYOiyeW4k83aJyOAqZjCAbrHU_hYQdobq8gmM6NsrMrQjxso9CCqOuRCwmxFTVxAGzJ0fN2tZ0e4fdXb_iIJ2rmnFyaXsHq30E_k5m27ilhmkqRlm6iuazYGCiMaqSYBTzLSBmM-uiQAhM7PGsOgUOH7MjNyT-AP8sV_5s--0ISvi8ny2bSFtKeKG0XhPfdlikD8LeuohE7ajDjwh2lzF46B9bD2RW1m4PkgKge_KPArHjHQWNQCG9SWIuxBnPgYZ1-42E5Xs_oDRy5BpMSheoG2L3g8FOEM8BYirYZPULAbj57oXJqb8byNyRvE9wYDsTPQyOegtjJ4xe"
    
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
        'sec-fetch-site': 'same-origin',    'traceparent': '00-9c0ec741b23e41ec84aa9df677081634-825ea0ee5823492e-01, 00-b97a717ce629404ca91822329146f7da-a7b1198bc7984de3-01',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}

cookies = {
    'ai_user': '594HVDlaap7MiF4y9x08uF|2026-08-11T08:48:28.850Z',
    'Dynamics365PortalAnalytics': '5ttfoMuzzn-07C8cgItxojNaKa_knbsEoqfZJuGGqFKGRYa5kTPR4_NbewCHgpPVmzdSxi5eDYzi1Y5chRiyq7f6Qi2JoQYrv92krC6suk5AQj_6IDIN-dRj0e6NdEa4N7eBhwm2GM_71H5tYnNJVg2',
    'ARRAffinity': '3cd56cc2b0db1eb96628d469bd51aadad1fbc26e09c3764d456c7d963180807d',
    'ARRAffinitySameSite': '3cd56cc2b0db1eb96628d469bd51aadad1fbc26e09c3764d456c7d963180807d',
    'ASLBSA': '000315a33c7d52976037145025442cb05084d205a07ef0fb0e9b1d090c276b403c4f',
    'ASLBSACORS': '000315a33c7d52976037145025442cb05084d205a07ef0fb0e9b1d090c276b403c4f',
    '_cfuvid': 'WgAzyCTLqud7A5U_qIP.lmym3kY1fT5HTI_qYb0Lg0A-1786631214.014867-1.0.1.1-gXJ9nxm07r4VKGsACrR9NZ2hEsSa1Yyn.JNPPcWcyn8',
    'ASP.NET_SessionId': 'bd0lhjxtcateo1zgbzwuh3e5',
    'timezoneoffset': '-240',
    'isDSTSupport': 'false',
    'isDSTObserved': 'false',
    'ContextLanguageCode': 'en-US',
    'timeZoneCode': '165',
    '__RequestVerificationToken': 'KlS77Xp4wGeTSmgu-5rOlVeDlhC5LY3FuOzLtse0-zjFuWExy_MjZdy3NIQySiR-kk6giC4I-4gMNtuDCW109qHn0Sa-HO_U5UVq79grMEY1',
    'cf_clearance': 'TOUOjssYFKXs8nc_4wS66aCvsMrpjUugmElkVdAKRCw-1786695019-1.2.1.1-pYxvN.FfZtCVWCE4IzsgKYCmt9yeI9uUhgidSoD.J80yxu.GSs0LknzkM.2fce2stBVp6MeJguq.hTCgHijHzm2CU8asBjr7VN9ea3xjkkJT1WdWSPM.ziuOQaxK85JBCGUpoEJc2gPZDgVO4Qs5zUj1Ke1HAKI6VFFRAlrnuvtBSaAJ4oGdDa6uGGOchr6E2VzbdIX_QgarOk1bxSJcSfIfPWFToDk4iUgs3zxuUpbU4nM4W0gXypHPcfWzRgQCNWUGIdhbU4zGScBrlqy20MT6Ynwb2hsJb11gk.GOx5Btw_32vcCbPYgv6VV.l6LbfzQ5Iyc2uRNAcVTZ8s2l_5p58pAeP1DYo1mzxnW9yjDkUIXo8guodjMicWfQ5Dwsp7xmxqsTKWFqOXFHmQq.cO6d.uvHMq8hvo0yCRbVCy7P8pSpouYUtrS68eIoaxl14bqqIt0GTcKw4Omr1U1aSw',
    '__cf_bm': '5wJ9utqUy9e1zmEoQ4K.gtcy6EsiJWoUObnXHX9nf9E-1786695019.603141-1.0.1.1-Q5RdoXQKSFSmQFnu5i3KAznrZ3GEF7C3gbxwHRlS7mx7UwVT3gB3.xCBzuvOG35yFNe5Ws.WN7lPscMzQUBsskAD6JMuUSvEo11_5EkWDDoaAl1OCGrbZfHLrlv5yivz',
    'ppuid': '60d59ff9-4212-f111-8342-001dd80b70e9',
    '.AspNet.ApplicationCookie': 'PmBtPJ78asMK8aouOzrI7C2Tdwq9o5cl9WI8aGwCIDo9x2KgxliiLv-mxaJLMX3uhPrBSLfiGfVNwTokA-PK-nSyv8q_sq23MpX9PoulDunH-gJFCHWs-PWPXDbcO594T9xgc3NmOor415XhTwfPn_EADjojpWELkerI_TduKsKkhWyBCQOBMF5g6GztUzW8xAjlGXqFFbewFnGlauAlZNg4bXn7tYcMO6W8xFTcViXO497kMZWJhdUHmT0v9yEWgu4YTydIGGQCm1x9qAGojXB4MgjjOTWIimgP9h1613Dbz8KswghcEtdbcqDbETqsfpXDq6fbb-yKqUqbD9ByZq2ynuLIV4oZGVkncqyD7Zhn4aq6nyUOSD1-4cHCEGps-1tjkZMpcTefqtyX2ikH_dz9cV4vP1nwaV71Yx8FlwzItf3gxc8GUeP1CsflerhnPNkr6hl7_PZT4sp-MXje__GfOSrDX2kbfuwufwtizXUEU4PC9mRfduR9vNLjGiWBcdxXcHJIUYYscIO4dB1RvpciIwDhBynkGj65z34nOYsVEbSkOezXWcBCqUmpis1w5Xy3A5BjpA-ywl6LS24IEmMgXaJkzUJ7wh3ycaGC0gJr15foMyp-2riJfYQOyKZ5upvlwnKpUXNYl_ZN5j-Orcs09nY7gleYkIfI6NHm4WDCtx2-Wtuk7GSVYJ2JSPuheqeazKk0lLMWZMpvpalLVzKNxxTIqCi9wP-PYRB05xmItTe5OTNjsjoVvIkqr9dScdFGNoclMdtX72A7PJKuYce0nqq_Y37g2NsCS3Ucn1u6KvHjxL9POnQHm6OF05swL4D5LAaMeqQjZCV-GeeDJTix5yqs4MmPBi07FxH5rGvBy9qGDcddn6zJ5GLpxmhD52E7UNi04_7L7qIfA__qFqvxUwm72DC90tsqTrPCk3VIcK4j-S2WWg1R4bFgE1oTtOvfCto1f3Y6W_nNGA4XvaOux7umren-EQn8PrdnHJZTMbJ_oyvSh-cz9vlG6P5cp6s-1j-S4OrTYA-mLwxVOv9PtS2SrSbi0jrj_zeJQ7JHchmwkIllJoV3qhZj1xhOmiPd7ALHm1WT4jaauKKi3dyZzCGTs3cuFSnkZkusRiFG8AQw019FdR3S0qauuAfoAIQaSE2iEiCGVQDumHqrW8ylrUHLSHx4QD1-X4s-55glcEz0Lub1t7VHHEMU8NDDsf4lrI94esNjU5Me3GtxUuOTHNHnsMrHlPBJBJAoKwwyy1fGjUVx7903SCs5m3V93Yako8Sz1NVJYk1otIXFb1xgM0L8YCsvR3v_rnNP41gk_JOw1-hgobGdLEq3ASAbkg1-BLy0BzpOL7nYfjgabW_I-WNWS9WCcrpoJjyhiEN07oxUT2DNtDleMJyia8BcAQ74R5_DoMf24oseFtRddZOvuFfrd8WXMbeLldytcQwiZQwwhFGA0uhkHMyPvVwQ8UWjWear7Me9LMjoj6l-GGa-PNbQywcmYqBDzZYH2vBC7I9C23slaJuUbul8OSvX7F8Q7npRS3rxFJn94sA8n_skES28fTdOu3z8JbP_X25G5m1LRBQLi8Gsy6Xlff6HiW72fJMRzp433YVE7n0JvffhGGwVYunZQ15m6y-zWUYew5fa2KRKhoy7Qk6taVpuzl4ICu6d1OCo43yNDyzS5HRMnRdXtzHB_odHs0ZWqHI5wHilIEzRCcYdBoCu9ffp9PvgzzEMx4jNrbS3KAZ_UV5mplXfoGAk9DLheGI6qz9RFsDkNMdKoSoD_HeM7_l63Jx_iWLJe8_QZkQ1Q5uy6wQuHAF_YjaC9P8PdFeQz4C1m6TOj7YioxKPS52AF8Yre0gI0yS6R2fqAU7EHRWquOgeGg0Amh4zQ37gx9ztDs5IGvTTwFfW2ezKHFzOBH2Eh3R6tD_fSNRqK1Qy0pFO0zvQDIwictdoFPf88Gnj40xQjKQG8suySyCnAjWmYwdMDALgvDCL0IFSG4MHutBsc6iiICgd_e4Ge51j_ntk0hQkemo8T3vJeUEuzj1dlgQhtU_TwMoeiyD9qAbzkJnQBx21FpbMJ2t40poDTgclSJ306CcWyPUN-ouMSkD_FKtkR_RHZEu90e6x-fPIKgvODbscaioPy2uNL6w7lxhqjPoAAcjjfpjmHuUXkD7NFtK6Tioaz4vMOYe5Sumq8ZjYFgGhoHM7nwJc_cZiIvkl8zIL_voCp1vKIq-wytJrdlFP_u21bAKR69LPMz4q4-EoMEHcAJVNPp86KepdaTAXL77cWQJkROi0NE7v9SpnSMchHyMDseBMoJ-_XGTkuQrWCAkR2rlXTmL40GQR-oBhoZTTXusgyWaOqEjm0crERR2HtwvmxVYft77I6igXvPit7iucaIb-cebp56aQvSY2o0kBm7Q3nA6JUS1jG8gOyghJWw1-OG3VvnOI3t_bFNcC4l6GnK-1sDo3a-EVze4Fn7zLFQRbAVtvmx99ywdNs9xx1LScc8ozZcgMWT23eYsNqe2hELRN2oosQ_VjriF0rrVUYv3mBH-Ti_qH7hdTuVJy9Mf9r71PoSroTegx7YVUhuRzA2e7lBgeMGgVGibbmlPAV21FujD95gDrnD9l9NvKWYUDsXkZkIkxWPkV6phwLOLFulS7PkTxZ2ii43L74oL0HYCmQWxAhZbTNNXD5atvZ7Ay7HTZQWzcnkeucRHyTu_d2gdVjPxc603VjQGiACmLq4olgNzFnDmhHbqNtvrwGcpZwrtNwJDS6MzUKA4rN6qZIAhKAhbSA9cIrDPNzkjwgFtOyZCZHF14Ton4exL6dg_u7XQzPUZk9rm9BhRBpuguPe2pQ-9l-_IWqOC7sYDXsDA34065JqKVWqiSWFpfwm2Lt2Y5UEoHogrjxHxmS66bM9ZVIfdJgHGwb6ZIzmqAUxlLZovLXlSmmwygR8bJ4Is9knE6k78AVxcTRpd2LBGBmUbiAo8IyC9mF-7sOTWAfEp4jYoIXjMH0zHtfF0en1ZhTHamX9SFJIVtKeBZE5wG5j8sSFquL662ZcTZS9uZzCve3QZldMRK9W5cxhCDJFiZY9dLGEpM9LL3c4LsJ6m0I-5nKDMKZnNhfSCltIhdgbWl2Vq9qeLqY3B9g1PXqTSsPN9r28jSEj4eV55_oBdiz1hveOJty54K27b7Nu1YZOsN1fgDbqK96oT2PVd_opwJQQwqGdnIrjeoR3OOJnRQ2ylVH18FFskNXcjqGDygLMSKduny0pZUD_Z3AMxXj1EHjmxlVu2cXelc8_G8mC3DtsMKhzJswbDGY_fSGRHAmuyHTn0-axZuLR98fDByOwcdhmTP8eH-TTuR2ZL80p3tcGOgUOOGa5JoW7kak0mEyyejy1wv3ueA1io347-LTsXuTW6Ef0J8ZQMEMLJ4I5YmpzUXiJxMp3cmWZWiyhSKcEjsNpQb3mTf-MgJw4KyJk_UFi5jfS0iKjkX_fUgpfWMhVAFyjN6ZQLKde_EfZW3ZJ7Fz3l02ITDQIU3E1LTD8kPoHq_dxLm2eyPPo7e7Bh7O401T-cPZGsjqlfSzOK6_O9zrYOiyeW4k83aJyOAqZjCAbrHU_hYQdobq8gmM6NsrMrQjxso9CCqOuRCwmxFTVxAGzJ0fN2tZ0e4fdXb_iIJ2rmnFyaXsHq30E_k5m27ilhmkqRlm6iuazYGCiMaqSYBTzLSBmM-uiQAhM7PGsOgUOH7MjNyT-AP8sV_5s--0ISvi8ny2bSFtKeKG0XhPfdlikD8LeuohE7ajAjwh2lzF46B9bD2RW1m4PkgKge_KPArHjHQWNQCG9SWIuxBnPgYZ1-42E5Xs_oDRy5BpMSheoG2L3g8FOEM8BYirYZPULAbj57oXJqb8byNyRvE9wYDsTPQyOegtjJ4xe'
}

payload_data = {
    'parameters': '{"primaryId":"6495c89e-4312-f111-bb46-001dd80aa47d","applications":["6495c89e-4312-f111-bb46-001dd80aa47d","53a41f5f-4412-f111-bb46-001dd80aa47d"],"scheduleDayId":"","scheduleEntryId":"","postId":"962fd063-ccb5-ef11-b8e9-001dd80637a9","isReschedule":"true"}'
}

# -------------------------------------------------------------------------
# DYNAMIC TIMELINE CALCULATIONS (Exactly 120 Days)
# -------------------------------------------------------------------------
start_bound = datetime.utcnow()
end_bound = start_bound + timedelta(days=MONITOR_WINDOW_DAYS)

start_date_str = start_bound.strftime("%Y-%m-%d")
end_date_str = end_bound.strftime("%Y-%m-%d")

print(f"Dynamic tracking window range calculated: {start_date_str} to {end_date_str}")

try:
    print("Pinging US Visa Scheduling API calendar grid...")
    response = requests.post(target_url, headers=headers, cookies=cookies, data=payload_data, timeout=20)
    
    if response.status_code == 200:
        data = response.json()
        days_list = data.get("ScheduleDays", [])
        
        if days_list is None:
            print("Server returned an empty schedule dashboard frame (ScheduleDays is null).")
            return True, "No days active."
            
        raw_dates = [day.get("Date") for day in days_list if day.get("Date") is not None]
        print(f"Total calendar days returned by server dashboard: {raw_dates}")
        
        matched_dates = []
        for date_text in raw_dates:
            try:
                current_date = datetime.strptime(date_text, "%Y-%m-%d")
                if start_bound.date() <= current_date.date() <= end_bound.date():
                    matched_dates.append(date_text)
            except ValueError:
                print(f"Skipping mismatched string format conversion: {date_text}")
                
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
