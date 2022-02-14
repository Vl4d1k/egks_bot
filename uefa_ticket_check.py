import requests
import time
import telebot
from lxml import html
import logging
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "app.log"

SECONDS_IN_HOUR = 3600

API_TOKEN = '1626684862:AAH-eStEOsno4d7Sfxk4NoUTHzi5LPcp09M'

AUTHOR_ID = 423227532

BOT_TIMEOUT = 5

def main():
    bot = telebot.TeleBot(API_TOKEN)
    logger = get_logger("logger")
    while True:
        try:
            res = requests.get('http://uefa.com/tickets')
            tree = html.fromstring(res.text)
            more_info = tree.xpath('/html/body/div[2]/div/div/div[2]/section/div/div/div/div[1]/div/div[2]/div[4]/div/div[2]/div[1]/a/text()')
            if 'More information' != more_info[-1]:
                logger.info('Tickets is avalianle now.')
                bot.send_message(AUTHOR_ID, 'Ticket is avalianle now. Visit http://uefa.com/tickets')
            logger.info('Tickets is NOT avalianle.')
            time.sleep(SECONDS_IN_HOUR/2)
        except Exception as ex:
            logger.info('Exception occurred.')
            bot.send_message(AUTHOR_ID, 'Can`t find info block. Visit http://uefa.com/tickets')
            time.sleep(BOT_TIMEOUT)

def get_logger(logger_name):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG)
   logger.addHandler(get_file_handler())
   logger.propagate = False
   return logger

def get_file_handler():
   file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
   file_handler.setFormatter(FORMATTER)
   return file_handler

if __name__ == '__main__':
    main()