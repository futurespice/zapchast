import random
import requests
from django.conf import settings
import logging
import re

logger = logging.getLogger(__name__)


def generate_token(length=6):
    """Generate a random numeric token of specified length."""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def send_sms(phone_number, message):
    """Send an SMS using the Infobip API."""
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
        response.raise_for_status()
        logger.info(f"SMS sent successfully. Response: {response.text}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending SMS: {e}")
        return False


def standardize_phone_number(phone_number):
    """
    Standardize the phone number to the Kyrgyzstan format.
    Assumes the number is a Kyrgyzstan number if no country code is provided.
    """
    # Remove any non-digit characters
    phone_number = re.sub(r'\D', '', phone_number)

    # If the number starts with 0, remove it
    if phone_number.startswith('0'):
        phone_number = phone_number[1:]

    # If the number doesn't start with 996, add it
    if not phone_number.startswith('996'):
        phone_number = '996' + phone_number

    # Ensure the number has the correct length (should be 12 digits including country code)
    if len(phone_number) != 12:
        raise ValueError("Invalid phone number length")

    return '+' + phone_number


def is_valid_phone_number(phone_number):
    """
    Validate phone number format for Kyrgyzstan.
    Returns True if the phone number is valid, False otherwise.
    """
    pattern = r'^\+996\d{9}$'
    return bool(re.match(pattern, phone_number))


def mask_phone_number(phone_number):
    """
    Mask the middle part of the phone number for privacy.
    Example: +996123456789 becomes +996***56789
    """
    if len(phone_number) != 13:  # +996 followed by 9 digits
        return phone_number
    return phone_number[:5] + '*' * 3 + phone_number[-5:]


# Temporary function for testing without actual SMS sending
def mock_send_sms(phone_number, message):
    """
    A mock function to simulate sending SMS for testing purposes.
    Always returns True and logs the message.
    """
    logger.info(f"Mock SMS sent to {phone_number}: {message}")
    return True

# Use this line to replace the real send_sms function with the mock version for testing
# send_sms = mock_send_sms