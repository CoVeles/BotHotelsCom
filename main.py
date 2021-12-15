# -*- coding: utf-8 -*-
from decouple import config
import sqlite3
import telebot
from bd.users_base import UsersBase

cl = UsersBase('./bd/users.db')
bot = telebot.TeleBot(config('TOKEN'))

conn = sqlite3.connect('./bd/users.db', check_same_thread=False)
cursor = conn.cursor()


def db_table_val(user_id: int, user_name: str, user_surname: str, username: str, town_search: str):
    cursor.execute('INSERT INTO user_hist (user_id, user_name, user_surname, town_search) VALUES (?, ?, ?, ?)',
                   (user_id, user_name, user_surname, username))
    conn.commit()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добро пожаловать')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == 'привет':

        us_id = message.from_user.id
        us_name = message.from_user.first_name
        us_sname = message.from_user.last_name
        username = message.from_user.username
        try:
            db_table_val(user_id=us_id, user_name=us_name, user_surname=us_sname, username=username, town_search='')
        except Exception as e:
            bot.send_message(message.chat.id, e.__repr__(), e.args)
        else:
            bot.send_message(message.chat.id, 'Привет! Ваше имя добавлено в базу данных!')
    else:
        bot.send_message(message.chat.id, 'Неизвестная команда')


if __name__ == '__main__':
    bot.infinity_polling()
