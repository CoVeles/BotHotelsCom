# -*- coding: utf-8 -*-
from decouple import config
from usershistory import UsersLog
from botrequests.locations import get_locations_from_api
from botrequests import lowprice
import constants
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.types import Message, CallbackQuery
from telebot import types, TeleBot
from telebot.custom_filters import AdvancedCustomFilter

bot = TeleBot(config('TOKEN'))


class User:
    users_dct = dict()

    def __init__(self, chat_id):
        self.chat_id: int = chat_id
        self.command: str = 'start'
        self.state: int = 0
        self.req_params = dict()
        User.add_user(chat_id, self)

    @classmethod
    def add_user(cls, user_id, user):
        user.init_req_params()
        cls.users_dct[user_id] = user

    @classmethod
    def get_user(cls, user_id):
        return cls.users_dct[user_id]

    def init_req_params(self):
        self.req_params: dict = {'loc_id': '', 'hotels_amount': 0,
                                 'distance': 0, 'pictures': 0}


def create_keyboard(items: dict, prefix: str):
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text=name,
                    callback_data=f'{prefix} {id}'
                )
            ]
            for id, name in items.items()
        ]
    )


def back_keyboard():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text='⬅',
                    callback_data='back'
                )
            ]
        ]
    )


@bot.message_handler(commands=['start'])
def on_start(message):
    user = User(message.chat.id)
    bot.send_message(
        message.chat.id,
        'Welcome to the bot for searching hotels!'
        '\nSelect a command:',
        reply_markup=create_keyboard(constants.MAIN_MENU, 'cmd')
    )


@bot.callback_query_handler(func=lambda c: c.data == 'back')
def back_callback(call: types.CallbackQuery):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Select a command:',
                          reply_markup=create_keyboard(constants.MAIN_MENU, 'cmd'))


# TODO: split into different callback_query_handlers with filters
@bot.callback_query_handler(func=None)
def command_callback(call: CallbackQuery):
    command: list = call.data.split()
    user = User.get_user(call.message.chat.id)
    if command[0] == 'cmd':
        text = 'Input town to search for hotels or back to main menu'
        user.command = command[1]
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text,
                              reply_markup=back_keyboard()
                              )
    elif command[0] == 'loc':
        """Location has been selected"""
        user.req_params['loc_id'] = command[1]
        user.state = 1
        if user.command == 'bestdeal':
            """Ask min price"""
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='Select minimal price for hotel room',
                reply_markup=create_keyboard(constants.MIN_PRICES, 'min'))
        else:
            """Ask amount of hotels"""
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='Select amount of hotels to view',
                reply_markup=create_keyboard(constants.HOTELS_AMOUNT, 'ham'))
    elif command[0] == 'ham':
        user.state = 2
        user.req_params['hotels_amount'] = command[1]
        """Ask about photo"""
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Do you want to see hotel pictures?',
            reply_markup=create_keyboard(constants.PHOTO_ASK, 'pic'))
    elif command[0] == 'pic':
        if command[1] == 'yes':
            user.state = 3
            """Ask photo amount"""
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='Select the number of photos to show',
                reply_markup=create_keyboard(constants.PHOTO_AMOUNT, 'pnum'))
        else:
            user.state = 4
            if user.command == 'bestdeal':
                """Ask min price"""
            else:
                display_hotels(user, call.message.chat.id)

    elif command[0] == 'pnum':
        user.req_params['pictures'] = command[1]
        if user.command == 'bestdeal':
            """Ask min price"""
        else:
            display_hotels(user, call.message.chat.id)


@bot.message_handler(content_types=['text'])
def get_text_messages(message) -> None:
    """
    text messages handler
    :param message: Message
    :return: None
    """
    user = User.get_user(message.chat.id)
    if not user:
        bot.send_message(message.chat.id,
                         'For restart tap: /start')
    else:
        if user.state == 0:
            # TODO: wrap in function
            locations = get_locations_from_api(message.text)
            if locations.get('err'):
                bot.send_message(message.chat.id, locations.get('err'))
                bot.send_message(message.chat.id, 'For restart tap: /start')
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text='Select a specific location',
                                 reply_markup=create_keyboard(locations, 'loc'))
        else:
            bot.send_message(message.chat.id, 'misunderstanding')


def display_hotels(user: User, chat_id):
    hotels = []
    if user.command == 'lowprice':
        hotels = lowprice.get_hotels(user.req_params)
    if len(hotels) == 0:
        text = 'Sorry, but there is no any hotel there'
        bot.send_message(chat_id, text)
    else:
        for hotel in hotels:
            text = ''
            for name, info in hotel.items():
                if name != 'pictures':
                    text += f'{name} {info}\n'
            bot.send_message(chat_id, text)
            if hotel.get('pictures'):
                display_pictures(hotel['pictures'], chat_id)
    bot.send_message(chat_id, 'For restart tap: /start')


def display_pictures(pictures: list, chat_id):
    for picture_url in pictures:
        if picture_url.startswith('http'):
            bot.send_photo(chat_id, picture_url)
        else:
            bot.send_message(chat_id, picture_url)


if __name__ == '__main__':
    bot.infinity_polling()
