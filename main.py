# -*- coding: utf-8 -*-
import telebot
TOKEN = '5004954394:AAGvH_L3o23Sj3QV9TES8NYBMSyokDi_XPs'

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=["text"])
def get_text_message(message):
    if (message.text == '/hello-world'
            or message.text.lower() == 'привет'):
        bot.send_message(message.chat.id, message.text)
    else:
        bot.send_message(message.chat.id, 'Неизвестная команда')


if __name__ == '__main__':
    bot.infinity_polling()
