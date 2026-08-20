import os

import requests


def send_ntfy_notification(message, title=None, topic=None):
    topic = topic or os.getenv("NTFY_TOPIC")
    if not topic:
        return
    headers = {"Title": title} if title else {}
    requests.post(f"https://ntfy.sh/{topic}", data=message.encode("utf-8"), headers=headers, timeout=10)
