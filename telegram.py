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


def run_telegram_bot(analysis_functions):
    def scheduled_analysis():
        all_timeframes_result = analysis_functions['all_timeframes']()
        top_coins_result = analysis_functions['top_coins']()

        # all_timeframes_result 결과가 없으면 함수 종료
        if not all_timeframes_result or not isinstance(all_timeframes_result, dict):
            print("No significant all-timeframes analysis results found.")
            return

        # 메시지 구성
        message_parts = []

        # top_coins_result 처리
        if top_coins_result:
            gainers_message = "Top 5 Gainers:\n" + \
                            "\n".join([f"{coin['symbol']}: {coin['change']}%" for coin in top_coins_result.get('gainers', [])])
            losers_message = "Top 5 Losers:\n" + \
                            "\n".join([f"{coin['symbol']}: {coin['change']}%" for coin in top_coins_result.get('losers', [])])
            message_parts.append(gainers_message)
            message_parts.append(losers_message)

        # 공백 라인 추가로 시각적 분리
        message_parts.append("----------------------------")

        # all_timeframes_result 결과 처리
        common_bb_symbols = all_timeframes_result.get('common_bb_symbols', [])
        common_rsi_symbols = all_timeframes_result.get('common_rsi_symbols', [])
        intersected_symbols = all_timeframes_result.get('intersected_symbols', [])

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
        message = "\n\n".join(message_parts) if message_parts else "No significant updates or unexpected result format."

        send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, message)

    schedule.every(1).second.do(scheduled_analysis)

    while True:
        schedule.run_pending()
        time.sleep(1)