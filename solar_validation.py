import hashlib
import os
import time

import requests

USERNAME = os.getenv("solar_validation_username")
PASSWORD = os.getenv("solar_validation_password")
COMPANY_KEY = "bnrl_frRFjEz8Mkn"
BASE_URL = "https://web.shinemonitor.com/public/"

PLANTID = os.getenv("solar_validation_plantid")
PN = "Q2022042840671"
DEVCODE = "632"
SN = "KSY0222HT0966"
DEVADDR = "1"


def _auth():
    salt = str(int(time.time() * 1000))
    action = "auth"
    pwd_sha1 = hashlib.sha1(PASSWORD.encode("utf-8")).hexdigest()
    sign_str = f"{salt}{pwd_sha1}&action={action}&usr={USERNAME}&company-key={COMPANY_KEY}"
    sign = hashlib.sha1(sign_str.encode("utf-8")).hexdigest()

    params = {
        "sign": sign,
        "salt": salt,
        "action": action,
        "usr": USERNAME,
        "company-key": COMPANY_KEY,
    }
    resp = requests.get(BASE_URL, params=params, timeout=10).json()
    if resp.get("err") != 0:
        raise RuntimeError(f"Solar login failed: {resp.get('desc')}")
    return resp["dat"]["secret"], resp["dat"]["token"]


def _query_today_pv(secret, token):
    action = "queryTodayDevicePvCharts"
    pns = f"{PN},{PN},{PN}"
    devcodes = f"{DEVCODE},{DEVCODE},{DEVCODE}"
    sns = f"{SN},{SN},{SN}"
    devaddrs = f"{DEVADDR},{DEVADDR},{DEVADDR}"

    salt = str(int(time.time() * 1000))
    business_params = (
        f"&plantid={PLANTID}&pns={pns}&sort=&devcodes={devcodes}&sns={sns}&devaddrs={devaddrs}"
        f"&i18n=en_US&lang=en_US"
    )
    sign_str = f"{salt}{secret}&action={action}{business_params}"
    sign = hashlib.sha1(sign_str.encode("utf-8")).hexdigest()

    params = {
        "sign": sign,
        "salt": salt,
        "token": token,
        "action": action,
        "plantid": PLANTID,
        "pns": pns,
        "sort": "",
        "devcodes": devcodes,
        "sns": sns,
        "devaddrs": devaddrs,
        "i18n": "en_US",
        "lang": "en_US",
    }
    resp = requests.get(BASE_URL, params=params, timeout=10).json()
    if resp.get("err") != 0:
        raise RuntimeError(f"Solar query failed: {resp.get('desc')}")
    return resp["dat"]


def get_solar_energy_today():
    secret, token = _auth()
    dat = _query_today_pv(secret, token)
    if not dat:
        return None
    return float(dat[0]["val"])


if __name__ == "__main__":
    print(get_solar_energy_today())
