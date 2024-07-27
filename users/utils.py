import random
import requests
from django.conf import settings


def generate_token():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def send_sms(phone_number, message):
    url = f"{settings.INFOBIP_BASE_URL}/sms/2/text/advanced"

    headers = {
        "Authorization": f"App {settings.INFOBIP_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "messages": [
            {
                "from": settings.INFOBIP_SENDER,
                "destinations": [
                    {"to": str(phone_number)}
                ],
                "text": message
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        print(f"SMS sent. Response: {response.text}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending SMS: {e}")
        return False