# telegram.py
import requests

def send_telegram_message(token, chat_id, message):
    """Send a message to a Telegram chat."""
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message}
    requests.post(url, json=payload)

