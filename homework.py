import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='homework.log', filemode='w'
)

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    yptoken = PRAKTIKUM_TOKEN
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {yptoken}'}
    current_timestamp = current_timestamp or int(time.time())
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    logging.info('Message sent')
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp
    logging.debug('Bot started')

    while True:
        try:
            homework = get_homeworks(current_timestamp)['homeworks']
            if len(homework) != 0:
                send_message(parse_homework_status(homework[0]))
                time.sleep(20 * 60)  # Опрашивать раз в 20 минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            send_message(f'Бот упал с ошибкой: {e}')
            logging.error(f'Bot crashed: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
