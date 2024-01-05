# telegram.py
import schedule
import time
import requests
from dotenv import load_dotenv
import os


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def send_telegram_message(token, chat_id, message):
    """Send a message to a Telegram chat."""
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message}
    requests.post(url, json=payload)


def run_telegram_bot(analysis_function):
    def scheduled_analysis():
        analysis_result = analysis_function()
        # 메시지 구성
        message_parts = []
        
        if analysis_result is None:
            message = "No suitable coins found."  # 분석 결과가 None일 때의 메시지
        elif not isinstance(analysis_result, dict):
            message = f"Unexpected result format: {analysis_result}"
        else:
            # common_bb_symbols와 intersected_symbols를 가져옵니다.
            common_bb_symbols = analysis_result.get('common_bb_symbols', [])
            common_rsi_symbols = analysis_result.get('common_rsi_symbols', [])
            intersected_symbols = analysis_result.get('intersected_symbols', [])

            # 메시지 구성
            message_parts = []
            if common_bb_symbols:
                bb_symbols_message = "Common Bollinger Band Extreme Symbols: " + ", ".join(common_bb_symbols)
                message_parts.append(bb_symbols_message)
            
            if common_rsi_symbols:
                rsi_symbols_message = "Common RSI Extreme Symbols: " + ", ".join(common_rsi_symbols)
                message_parts.append(rsi_symbols_message)

            if intersected_symbols:
                intersected_message = "Symbols with both extreme BB and RSI: " + ", ".join(intersected_symbols)
                message_parts.append(intersected_message)

            # 메시지가 비어있지 않다면 합치고, 그렇지 않으면 기본 메시지 설정
            if message_parts:
                message = "\n".join(message_parts)
            else:
                message = "No significant extreme symbols found in this analysis."


        send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, message)

    schedule.every(1).second.do(scheduled_analysis)

    while True:
        schedule.run_pending()
        time.sleep(1)