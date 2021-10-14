# ! /usr/bin/python
# -*- coding: utf-8 -*-

"""This script starts bot and sends info about egds."""

import requests
from bs4 import BeautifulSoup
import logging
import time
import telebot

API_TOKEN = ''
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
BOT_INTERVAL = 10
BOT_TIMEOUT = 5

logging.basicConfig(filename='python_bot_log.txt', datefmt='%d/%m/%Y %I:%M:%S', filemode='w',format=LOG_FORMAT, level=logging.INFO)

def bot_polling():
    global bot
    logging.info('Starting bot polling now')
    while True:
        try:
            logging.info('New bot instance started')
            bot = telebot.TeleBot(API_TOKEN)
            bot_actions()
            bot.polling(none_stop=True, interval=BOT_INTERVAL,
                        timeout=BOT_TIMEOUT)
        except Exception as ex:
            logging.info(
                'Bot polling failed, restarting in {} sec. Error: {}'.format(BOT_TIMEOUT, ex))
            bot.stop_polling()
            time.sleep(BOT_TIMEOUT)
        else:
            bot.stop_polling()
            logging.info('Bot polling loop finished')
            break

def bot_actions():

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, 'Привет, чтобы получить данные о карте ЕГКС просто отправь боту ее номер.')
        logging.info(f'Said hi to user with id: [{message.chat.id}]')
    
    @bot.message_handler(content_types=['text'])
    def get_egks_info(message):
        
        card_number = message.text
        chat_id = message.chat.id

        input_message = message.text.replace("\n", " | ")
        logging.info(f'User [{chat_id}] send message: [{input_message}]')

        if (not card_number.isdecimal()):
            logging.info(f'Not valid card number [{card_number}] from user [{chat_id}].')
            bot.send_message(chat_id=chat_id, text='Номер карты должен состоять только из чисел')
            return
        
        if (len(card_number) != 6 and len(card_number) != 9):
            logging.info(f'Not valid card number [{card_number}] from user [{chat_id}].')
            bot.send_message(chat_id=chat_id, text='Номер карты должен состоять из 6 либо 9 символов')
            return

        response = requests.post(f'https://www.egks.ru/card?number={message.text}', verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        result_message = str(soup.find('p')).replace('<br/>', '\n').replace('<p>', '').replace('</p>', '')
        if (len(result_message) == 0):
            bot.send_message(chat_id=chat_id, text=f'Карта с номером {message.text} не найдена либо неактивна')
        else:
            bot.send_message(chat_id=chat_id, text=result_message)

        result_message = result_message.replace("\n", " | ")
        logging.info(f'Send message: [{result_message}] to [{chat_id}]')

if __name__ == '__main__':
    bot_polling()
