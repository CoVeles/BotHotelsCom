# -*- coding: utf-8 -*-
from decouple import config
import sqlite3
import telebot
from bd.users_base import UsersBase

cl = UsersBase('./bd/users.db')



# bot = telebot.TeleBot(config('TOKEN'))
#
#
# @bot.message_handler(content_types=["text"])
# def get_text_message(message):
#     if (message.text == '/hello-world'
#             or message.text.lower() == 'привет'):
#         bot.send_message(message.chat.id, message.text)
#     else:
#         bot.send_message(message.chat.id, 'Неизвестная команда')
#
# def start():
#
# if __name__ == '__main__':
#     bot.infinity_polling()
