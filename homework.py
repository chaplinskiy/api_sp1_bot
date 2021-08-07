import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
PRAKTIKUM_URL = 'https://praktikum.yandex.ru/api/'
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='homework.log', filemode='w'
)

logger = logging.getLogger(__name__)

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    try:
        homework_name = homework['homework_name']
        if homework['status'] == 'rejected':
            verdict = 'К сожалению, в работе нашлись ошибки.'
        elif homework['status'] == 'approved':
            verdict = 'Ревьюеру всё понравилось, работа зачтена!'
        else:
            verdict = 'Ни апрува, ни реджекта, а незнамо что!'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except Exception as e:
        logger.error(f'У нас какие-то проблемки: {e}')
        return f'{e}'


def get_homeworks(current_timestamp):
    yptoken = PRAKTIKUM_TOKEN
    url = f'{PRAKTIKUM_URL}user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {yptoken}'}
    current_timestamp = current_timestamp or int(time.time())
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
        return homework_statuses.json()
    except ConnectionError as e:
        logger.error(f'Возможны проблемы с доступностью API: {e}')
        return f'{e}'


def send_message(message):
    logger.info('Message sent')
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp
    logger.debug('Bot started')

    while True:
        try:
            homework = get_homeworks(current_timestamp).get('homeworks')
            if len(homework) > 0:
                send_message(parse_homework_status(homework[0]))
                time.sleep(20 * 60)  # Опрашивать раз в 20 минут

        except Exception as e:
            send_message(f'Бот упал с ошибкой: {e}')
            logger.error(f'Ошибочка вышла: {e}')
            # Не будем дергать судьбу за Хероку, передернем раз в 5 минут
            # (а не раз в 5 секунд, как раньше)
            time.sleep(5 * 60)


if __name__ == '__main__':
    main()
