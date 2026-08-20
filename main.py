import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

from binance_fund import get_client, get_total_wallet_balance_usdt
from notifications import send_ntfy_notification
from solar_validation import get_solar_energy_today

INTERVAL_SECONDS = 5 * 60
ALERT_RANGE_LOW = 218
ALERT_RANGE_HIGH = 220

IST = ZoneInfo("Asia/Kolkata")
SOLAR_CHECK_HOUR_IST = 12
SOLAR_MIN_ENERGY = 100
SOLAR_ALERT_TOPIC = os.getenv("solar_alerter_topic")


def check_binance_fund(client, timestamp):
    total_usdt = get_total_wallet_balance_usdt(client)
    message = f"Total Unified Wallet Balance: ${total_usdt:,.2f} USDT"
    print(f"[{timestamp}] {message}")
    if total_usdt < ALERT_RANGE_LOW or total_usdt > ALERT_RANGE_HIGH:
        send_ntfy_notification(message, title="Binance Portfolio")


def check_solar_validation(timestamp):
    try:
        energy = get_solar_energy_today()
        print(f"[{timestamp}] Solar energy today: {energy}")
        if energy is None or energy < SOLAR_MIN_ENERGY:
            send_ntfy_notification(
                f"Solar energy today is {energy}, below the {SOLAR_MIN_ENERGY} threshold.",
                title="Solar Alert",
                topic=SOLAR_ALERT_TOPIC,
            )
    except Exception as e:
        print(f"[{timestamp}] Solar error: {e}")
        send_ntfy_notification(f"Solar validation error: {e}", title="Solar Alert", topic=SOLAR_ALERT_TOPIC)


def run_forever(client):
    now_ist = datetime.now(IST)
    timestamp = now_ist.strftime("%Y-%m-%d %H:%M:%S")
    check_solar_validation(timestamp)
    last_solar_run_date = now_ist.date() if now_ist.hour >= SOLAR_CHECK_HOUR_IST else None

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            check_binance_fund(client, timestamp)
        except Exception as e:
            print(f"[{timestamp}] Binance error: {e}")

        now_ist = datetime.now(IST)
        if now_ist.hour >= SOLAR_CHECK_HOUR_IST and now_ist.date() != last_solar_run_date:
            check_solar_validation(now_ist.strftime("%Y-%m-%d %H:%M:%S"))
            last_solar_run_date = now_ist.date()

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    client = get_client()
    run_forever(client)
