# -*- coding: utf-8 -*-
from decouple import config
from botrequests.locations import get_locations_from_api
from botrequests import lowprice, highprice, bestdeal
import constants
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.types import Message, CallbackQuery
from telebot import types, TeleBot
from usershistory import UsersLog
from datetime import datetime

bot = TeleBot(config('TOKEN'))
user_log = UsersLog()
user_log.setup()


class User:
    """
    This class contains a dictionary of users of session
    Every user has a state of step and requirement parameters for
    requests to Hotels API
    """
    users_dct = dict()

    def __init__(self, user_id):
        self.user_id: int = user_id
        self.command: str = 'start'
        self.state: int = 0
        self.req_params = dict()
        User.add_user(user_id, self)

    @classmethod
    def add_user(cls, user_id, user):
        user.init_req_params()
        cls.users_dct[user_id] = user

    @classmethod
    def get_user(cls, user_id):
        return cls.users_dct.get(user_id)

    def init_req_params(self):
        self.req_params: dict = {'loc_id': '', 'hotels_amount': 0,
                                 'price_min': 0, 'price_max': 0,
                                 'distance': 0, 'pictures': 0}


button_cancel = types.ReplyKeyboardMarkup()
button_cancel.add()
hide_cancel = types.ReplyKeyboardRemove()


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


@bot.message_handler(commands=['start'])
def on_start(message):
    if not User.get_user(message.chat.id):
        User(message.chat.id)
        text = 'Welcome to the bot for searching hotels!' \
               '\nSelect a command:'
    else:
        text = '\nSelect a command:'
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=create_keyboard(constants.MAIN_MENU, 'cmd')
    )


# @bot.callback_query_handler(func=lambda c: c.data == 'back')
# def back_callback(call: types.CallbackQuery):
#     bot.edit_message_text(chat_id=call.message.chat.id,
#                           message_id=call.message.message_id,
#                           text='Select a command:',
#                           reply_markup=create_keyboard(constants.MAIN_MENU, 'cmd'))


@bot.callback_query_handler(func=None)
def command_callback(call: CallbackQuery):
    command: list = call.data.split()
    user = User.get_user(call.message.chat.id)
    if not user:
        bot.send_message(call.message.chat.id,
                         'For correct work begin with main menu!'
                         '\nTo call main menu tap: /start')
    else:
        if command[0] == 'cmd':
            """User tapped a command in main menu"""
            if command[1] == 'history':
                display_history(user_id=call.message.chat.id)
            elif command[1] == 'help':
                for name, info in constants.HELP_INFO.items():
                    bot.send_message(call.message.chat.id,
                                     name + info)
                bot.send_message(call.message.chat.id,
                                 'To begin tap: /start')
            else:
                text = 'Input town to search for hotels'
                user.command = command[1]
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=text)
        elif command[0] == 'loc':
            """Location is accepted"""
            user.req_params['loc_id'] = command[1]
            user.state = 1
            """Ask amount of hotels"""
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='Select amount of hotels to view',
                reply_markup=create_keyboard(constants.HOTELS_AMOUNT, 'ham'))
        elif command[0] == 'ham':
            """Amount of hotels is accepted"""
            user.state = 2
            user.req_params['hotels_amount'] = command[1]
            """Ask about photo"""
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='Do you want to see hotel pictures?',
                reply_markup=create_keyboard(constants.PHOTO_ASK, 'pic'))
        elif command[0] == 'pic':
            """The decision about photo is accepted"""
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
                    text = 'Input minimum price for hotel'
                    bot.send_message(call.message.chat.id, text)
                else:
                    display_hotels(user, call.message.chat.id)
        elif command[0] == 'pnum':
            """Amount of photo is accepted"""
            user.req_params['pictures'] = command[1]
            if user.command == 'bestdeal':
                """Ask min price"""
                text = 'Input minimum price for hotel'
                bot.send_message(call.message.chat.id, text)
            else:
                display_hotels(user, call.message.chat.id)
        elif command[0] == 'dst':
            display_hotels(user, call.message.chat.id)


@bot.message_handler(content_types=['text'])
def get_text_messages(message) -> None:
    user = User.get_user(message.chat.id)
    if not user:
        bot.send_message(message.chat.id, 'For correct work begin with main menu!'
                                          '\nTo call main menu tap: /start')
    else:
        if user.state == 0:
            display_found_locations_menu(message.text, message.chat.id)
        elif user.state == 4:
            check_and_save_min_price(message.text, user)
        elif user.state == 5:
            check_and_save_max_price(message.text, user)
        else:
            bot.send_message(message.chat.id, 'misunderstanding')


def check_and_save_min_price(text, user):
    try:
        price = abs(float(text.replace(',', '.')))
        user.state = 5
        user.req_params['price_min'] = price
        bot.send_message(user.user_id,
                         'Input maximum price for hotel')
    except Exception:
        bot.send_message(
            user.user_id,
            'You input wrong price'
            '\nTry again to input minimum price for hotel')


def check_and_save_max_price(text, user):
    try:
        price = abs(float(text.replace(',', '.')))
        if price <= user.req_params['price_min']:
            bot.send_message(
                user.user_id,
                'Maximum price must be more than minimum price'
                '\nTry again to input maximum price for hotel')
        else:
            user.state = 6
            user.req_params['price_max'] = price
            bot.send_message(chat_id=user.user_id,
                             text='Select maximum distance from centre',
                             reply_markup=create_keyboard(
                                 constants.DISTANCE, 'dst'))
    except Exception:
        bot.send_message(
            user.user_id,
            'You input wrong price.'
            '\nTry again to input maximum price for hotel')


def display_found_locations_menu(mess_text, user_id):
    """Display menu of found locations"""
    locations = get_locations_from_api(mess_text)
    if locations.get('err'):
        bot.send_message(user_id, locations.get('err'))
        bot.send_message(user_id, 'For restart tap: /start')
    else:
        bot.send_message(chat_id=user_id,
                         text='Select a specific location',
                         reply_markup=create_keyboard(locations, 'loc'))


def display_hotels(user: User, chat_id):
    hotels = []
    if user.command == 'lowprice':
        hotels = lowprice.get_hotels(user.req_params)
    elif user.command == 'highprice':
        hotels = highprice.get_hotels(user.req_params)
    elif user.command == 'bestdeal':
        hotels = bestdeal.get_hotels(user.req_params)

    if len(hotels) == 0:
        text = 'Sorry, but there is no any hotel there'
        bot.send_message(chat_id, text)
    else:
        hotels_lst = []
        for hotel in hotels:
            hotels_lst.append(hotel.get('Hotel:'))
            text = ''
            for name, info in hotel.items():
                if name != 'pictures':
                    text += f'{name} {info}\n'
            bot.send_message(chat_id, text)
            if hotel.get('pictures'):
                display_pictures(hotel['pictures'], chat_id)
        save_user_log(user.user_id, user.command, hotels_lst)
    bot.send_message(chat_id, 'For restart tap: /start')


def display_pictures(pictures: list, chat_id):
    for picture_url in pictures:
        if picture_url.startswith('http'):
            bot.send_photo(chat_id, picture_url)
        else:
            bot.send_message(chat_id, picture_url)


def save_user_log(user_id, command, hotels: list):
    date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    hotels_str = ', '.join(hotels)
    user_log = UsersLog()
    user_log.add_user_command(user_id, command, date, hotels_str)


def display_history(user_id: int):
    user_log = UsersLog()
    log: list = user_log.get_commands_for_user(user_id)
    if len(log) == 0:
        text = 'There is no any command in your history'
        bot.send_message(user_id, text)
    else:
        text = 'Look through your commands history:'
        bot.send_message(user_id, text)
        for item in log:
            text = f'Command: {item[1]}'
            text += f'\nDate & Time: {item[2]}'
            text += f'\nFounded hotels: {item[3]}'
            bot.send_message(user_id, text)
    bot.send_message(user_id, 'For restart tap: /start')


if __name__ == '__main__':
    bot.infinity_polling()
