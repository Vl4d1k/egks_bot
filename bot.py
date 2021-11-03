# ! /usr/bin/python
# -*- coding: utf-8 -*-

"""This script starts bot and sends info about egds."""

import requests
from bs4 import BeautifulSoup
import logging
import time
import telebot
import os
from requests.packages import urllib3
from dotenv import load_dotenv
from telebot import types

# todo исправить логирование
# todo вынести проверку автора в декоратор
# todo сделать автодеплой на сервер
# todo обновление баланса по крону
# todo добавить базу
# todo получение информации о карте по фото

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')

BOT_INTERVAL = int(os.getenv('BOT_INTERVAL'))
BOT_TIMEOUT = int(os.getenv('BOT_TIMEOUT'))

AUTHOR_ID = int(os.getenv('AUTHOR_ID'))

log_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log.log')
logging.basicConfig(filename=log_path,
                    filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    bot_polling()


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
                f'Bot polling failed, restarting in {BOT_TIMEOUT} sec. Error: {ex}')
            bot.stop_polling()
            time.sleep(BOT_TIMEOUT)
        else:
            bot.stop_polling()
            logging.info('Bot polling loop finished')
            break


def bot_actions():

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(
            message, 'Привет, чтобы получить данные о карте ЕГКС просто отправь боту ее номер в формате:\n xxx xxx xxx либо xxx xxx (без префикса из 000). Если у вас есть вопросы по боту,вы можете написать разработчику в телеграмме @vlad1k11 или на электронную почту: vlad1k121@yandex.ru.')
        logging.info(
            f'Said hi to user [{message.from_user.username}] with id: [{message.chat.id}]')

    @bot.message_handler(commands=['help'])
    def help(message):
        bot.reply_to(message, 'Если у вас есть вопросы по боту,вы можете написать разработчику в телеграмме @vlad1k11 или на электронную почту: vlad1k121@yandex.ru.')
        logging.info(
            f'Send help message to user [{message.from_user.username}] with id: [{message.chat.id}]')

    @bot.message_handler(commands=['sendmessage'])
    def send_message(message):
        if (message.from_user.id != AUTHOR_ID):
            return

        args = message.text.split()
        recipient_id = args[1]
        if (recipient_id.isdecimal()):
            bot.send_message(AUTHOR_ID, 'not valid recipient id')
            return

        text = ' '.join(args[2:])
        bot.send_message(recipient_id, text)

    @bot.message_handler(commands=["getuser"])
    def get_user(message):
        if (message.from_user.id != AUTHOR_ID):
            return

        args = message.text.split()
        if (len(args) != 2):
            bot.send_message(AUTHOR_ID, 'not valid command')
            return

        user_id = args[1]
        user_info = bot.get_chat_member(user_id, user_id).user
        bot.send_message(AUTHOR_ID, "Id: " + str(user_info.id) + "\nFirst Name: " + str(user_info.first_name) +
                         "\nLast Name: " + str(user_info.last_name) + "\nUsername: @" + str(user_info.username))

    @bot.message_handler(content_types=['text'])
    def get_egks_info(message):

        card_number = message.text.replace(" ", "")
        chat_id = message.chat.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        username = message.from_user.username

        logging.info(
            f'{first_name} {last_name} [{username}] [{chat_id}] send message: [{message.text}].')

        if (not card_number.isdecimal()):
            logging.info(
                f'Not valid card number [{card_number}] from user [{chat_id}].')
            bot.send_message(
                chat_id=chat_id, text='Номер карты должен состоять только из чисел')
            return

        if (len(card_number) != 6 and len(card_number) != 9):
            logging.info(
                f'Not valid card number [{card_number}] from user [{chat_id}].')
            bot.send_message(
                chat_id=chat_id, text='Номер карты должен состоять из 6 либо 9 символов')
            return

        response = requests.post(
            f'https://www.egks.ru/card?number={card_number}', verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        result_message = str(soup.select_one('div p:nth-of-type(2)')
                            ).replace('<br/>', '\n').replace('<p>', '').replace('</p>', '')
        if (len(result_message) == 0 or result_message == 'None'):
            result_message = soup.select_one('h3').getText()
            bot.send_message(chat_id=chat_id, text=result_message)
        else:
            markup = types.ReplyKeyboardMarkup()
            markup.add(types.KeyboardButton(card_number))
            bot.send_message(
                chat_id=chat_id, text=result_message, reply_markup=markup)

        result_message = result_message.replace("\n", " | ")
        logging.info(
            f'Send message: [{result_message}] to user [{username}] [{chat_id}]')


if __name__ == '__main__':
    main()
