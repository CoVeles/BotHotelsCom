# -*- coding: utf-8 -*-
from datetime import datetime

from loguru import logger
from decouple import config
from telebot import types, TeleBot
from telebot.types import CallbackQuery
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import constants
import log_setup
from botrequests import lowprice, highprice, bestdeal
from botrequests.locations import get_locations_from_api
from usershistory import User as User, UserHistory

logger.configure(**log_setup.logger_setup)
bot = TeleBot(config('TOKEN'))
user_history = UserHistory()
user_history.setup()


# button_cancel = types.ReplyKeyboardMarkup()
# button_cancel.add()
# hide_cancel = types.ReplyKeyboardRemove()


def create_keyboard(items: dict, prefix: str) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text=name,
                    callback_data=f'{prefix} {command}'
                )
            ]
            for command, name in items.items()
        ]
    )


@bot.message_handler(commands=['start'])
def on_start(message):
    user_id = message.chat.id
    logger.info(f'User {user_id} tapped /start')
    user = User.get_user(user_id)
    if not user:
        User(user_id)
        bot.send_message(user_id,
                         'Welcome to the bot for searching hotels!')
    else:
        user.init_req_params()

    bot.send_message(
        user_id,
        '\nSelect a command:',
        reply_markup=create_keyboard(constants.MAIN_MENU, 'cmd')
    )


# @bot.callback_query_handler(func=lambda c: c.data == 'back')
# def back_callback(call: types.CallbackQuery):
#     bot.edit_message_text(chat_id=call.message.chat.id,
#                           message_id=call.message.message_id,
#                           text='Select a command:',
#                           reply_markup=create_keyboard(constants.MAIN_MENU, 'cmd'))

@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def calendar_callback(call: CallbackQuery):
    user_id = call.message.chat.id
    user = User.get_user(user_id)

    if not user:
        logger.warning(f'User {user_id} tried to begin without /start')
        bot.send_message(user_id,
                         'For correct work begin with main menu!'
                         '\nTo call main menu tap: /start')
    else:
        result, key, step = DetailedTelegramCalendar().process(call.data)
        if not result and key:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.message_id,
                                  text=f'Select {LSTEP[step]}',
                                  reply_markup=key)
        elif result:
            user.req_params['check_in'] = result
            user.set_state(4)
            logger.info(f'{user_id} selected check-in date')
            text = 'For how many days do you plan to stay at the hotel?'
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.message_id,
                                  text=text)


@bot.callback_query_handler(func=None)
def command_callback(call: CallbackQuery):
    command: list = call.data.split()
    user_id = call.message.chat.id
    user = User.get_user(user_id)

    if not user:
        logger.warning(f'User {user_id} tried to begin without /start')
        bot.send_message(user_id,
                         'For correct work begin with main menu!'
                         '\nTo call main menu tap: /start')
    else:
        if command[0] == 'cmd' and user.state == 0:
            logger.info(f'{user_id} tapped command: {command[1]}')
            if command[1] == 'history':
                # user.state = 11
                display_history(user_id=user_id)
            elif command[1] == 'help':
                # user.state = 11
                display_help(user_id=user_id)
            else:
                text = 'Input town to search for hotels'
                user.command = command[1]
                user.state = 1
                bot.edit_message_text(chat_id=user_id,
                                      message_id=call.message.message_id,
                                      text=text)
        elif command[0] == 'loc' and user.state == 1:
            logger.info(f'{user_id} selected specific location')
            user.req_params['loc_id'] = command[1]
            user.state = 2
            """Ask amount of hotels"""
            bot.edit_message_text(
                chat_id=user_id,
                message_id=call.message.message_id,
                text='Select amount of hotels to view',
                reply_markup=create_keyboard(constants.HOTELS_AMOUNT, 'ham'))
        elif command[0] == 'ham' and user.state == 2:
            logger.info(f'{user_id} selected amount of hotels')
            user.state = 3
            user.req_params['hotels_amount'] = command[1]
            """Ask check-in date"""
            calendar, step = DetailedTelegramCalendar().build()
            bot.send_message(user_id, 'Select check-in date')
            bot.send_message(user_id,
                             f'Select {LSTEP[step]}',
                             reply_markup=calendar)
        elif command[0] == 'pic' and user.state == 5:
            logger.info(f'{user_id} selected the need of pictures')
            if command[1] == 'yes':
                user.state = 6
                """Ask photo amount"""
                bot.edit_message_text(
                    chat_id=user_id,
                    message_id=call.message.message_id,
                    text='Select the number of photos to show',
                    reply_markup=create_keyboard(constants.PHOTO_AMOUNT, 'pnum'))
            else:
                user.state = 7
                step_after_pics_query(user)
        elif command[0] == 'pnum' and user.state == 6:
            logger.info(f'{user_id} selected amount of pictures')
            user.state = 7
            user.req_params['pictures'] = command[1]
            step_after_pics_query(user)
        elif command[0] == 'dst' and user.state == 10:
            logger.info(f'{user_id} selected distance')
            user.req_params['distance'] = command[1]
            display_hotels(user, user_id)
        else:
            logger.warning(f'{user_id} selected wrong command')
            text = 'Unknown command. Please begin with main menu' \
                   '\nFor main menu tap /start'
            bot.send_message(user_id, text)


@bot.message_handler(content_types=['text'])
def get_text_messages(message) -> None:
    user_id = message.chat.id
    user = User.get_user(user_id)
    if not user:
        logger.warning(f'User {user_id} tried to begin without /start')
        bot.send_message(user_id, 'For correct work begin with main menu!'
                                  '\nTo call main menu tap: /start')
    else:
        if user.state == 1:
            display_found_locations_menu(message.text, user_id)
        elif user.state == 4:
            check_and_save_days_delta(message.text,
                                      message.message_id, user)
        elif user.command == 'bestdeal' and user.state == 7:
            check_and_save_min_price(message.text, user)
        elif user.command == 'bestdeal' and user.state == 8:
            check_and_save_max_price(message.text, user)
        else:
            logger.warning(f'{user_id} typed wrong command')
            bot.send_message(user_id, 'misunderstanding')


def check_and_save_days_delta(text: str, mess_id: int, user: User) -> None:
    try:
        logger.info(f'{user.user_id} typed amount of days')
        days = abs(int(text))
        if days == 0:
            days += 1
        user.state = 5
        user.req_params['days'] = days
        """Ask about photo"""
        bot.send_message(
            chat_id=user.user_id,
            text= 'Do you want to see hotel pictures?',
            reply_markup=create_keyboard(constants.PHOTO_ASK, 'pic')
        )
        # bot.edit_message_text(
        #     chat_id=user.user_id,
        #     message_id=mess_id,
        #     text='Do you want to see hotel pictures?',
        #     reply_markup=create_keyboard(constants.PHOTO_ASK, 'pic'))
    except Exception as e:
        logger.error(f'User {user.user_id}: {e}')
        bot.send_message(
            user.user_id,
            'You input wrong amount of days'
            '\nTry again to input amount of staying days')


def check_and_save_min_price(text: str, user: User) -> None:
    try:
        logger.info(f'{user.user_id} typed min price')
        price = abs(int(float(text.replace(',', '.'))))
        user.state = 8
        user.req_params['price_min'] = price
        bot.send_message(user.user_id,
                         'Input maximum price for hotel')
    except Exception as e:
        logger.error(f'User {user.user_id}: {e}')
        bot.send_message(
            user.user_id,
            'You input wrong price'
            '\nTry again to input minimum price for hotel')


def check_and_save_max_price(text: str, user: User) -> None:
    try:
        logger.info(f'{user.user_id} typed max price')
        price = abs(int(float(text.replace(',', '.'))))
        if price <= user.req_params['price_min']:
            logger.error(f'User {user.user_id}: typed wrong max price')
            bot.send_message(
                user.user_id,
                'Maximum price must be more than minimum price'
                '\nTry again to input maximum price for hotel')
        else:
            user.state = 9
            user.req_params['price_max'] = price
            bot.send_message(chat_id=user.user_id,
                             text='Select maximum distance from centre',
                             reply_markup=create_keyboard(
                                 constants.DISTANCE, 'dst'))
    except Exception as e:
        logger.error(f'User {user.user_id}: {e}')
        bot.send_message(
            user.user_id,
            'You input wrong price.'
            '\nTry again to input maximum price for hotel')


def display_found_locations_menu(mess_text: str, user_id: int) -> None:
    """Display menu of found locations"""
    locations = get_locations_from_api(mess_text)
    if locations.get('err'):
        logger.error(f"User {user_id} {locations['err']}")
        bot.send_message(user_id, locations['err'])
        bot.send_message(user_id,
                         'Type another town or tap /start')
    else:
        bot.send_message(chat_id=user_id,
                         text='Select a specific location',
                         reply_markup=create_keyboard(locations, 'loc'))


def display_hotels(user: User, chat_id: int) -> None:
    hotels = []
    logger.info(f'Attempt to request hotels info from API')
    if user.command == 'lowprice':
        hotels = lowprice.get_hotels(user.req_params)
    elif user.command == 'highprice':
        hotels = highprice.get_hotels(user.req_params)
    elif user.command == 'bestdeal':
        hotels = bestdeal.get_hotels(user.req_params)

    if len(hotels) == 0:
        logger.info(f'{chat_id} there is no any hotel in request')
        text = 'Sorry, but there is no any hotel ' \
               'with such parameters' \
               '\nFor restart tap /start'
        bot.send_message(chat_id, text)
    else:
        hotels_lst = []
        for hotel in hotels:
            if hotel.get('err'):
                logger.error(f"User {chat_id}: {hotel.get['err']}")
            else:
                hotels_lst.append(hotel.get('Hotel:'))
                text = ''
                for name, info in hotel.items():
                    if name == 'id':
                        text += f'Hotel URL: https://ru.hotels.com/ho' \
                                f'{info}\n'
                    elif name == 'pictures':
                        display_pictures(hotel['pictures'], chat_id)
                    else:
                        text += f'{name} {info}\n'
                try:
                    total_price = int(hotel.get('Price:')[1:].replace(',', ''))
                    total_price *= user.req_params['days']
                    text += f"Price for {user.req_params['days']} days:" \
                            f" ${total_price}"
                except Exception as e:
                    logger.error(f'User {chat_id}: {e}')

                bot.send_message(chat_id, text, disable_web_page_preview=True)

        save_user_history(user.user_id, user.command, hotels_lst)
    bot.send_message(chat_id, 'For restart tap: /start')


def display_pictures(pictures: list, chat_id: int) -> None:
    try:
        if len(pictures) > 1:
            medias = [types.InputMediaPhoto(img_url, 'View')
                      for img_url in pictures]
            bot.send_media_group(chat_id=chat_id,
                                 media=medias,
                                 allow_sending_without_reply=True)
        else:
            if pictures[0].startswith('http'):
                bot.send_photo(chat_id, pictures[0])
            else:
                logger.error(f'User {chat_id}: {pictures[0]}')
                bot.send_message(chat_id, pictures[0])
    except Exception as e:
        logger.error(f'User {chat_id}: {e}')


def save_user_history(user_id: int, command: str, hotels: list) -> None:
    date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    hotels_str = ', '.join(hotels)
    user_hist = UserHistory()
    user_hist.add_user_command(user_id, command, date, hotels_str)


def display_history(user_id: int) -> None:
    user_hist = UserHistory()
    history: list = user_hist.get_commands_for_user(user_id)
    if len(history) == 0:
        text = 'There is no any command in your history'
        bot.send_message(user_id, text)
    else:
        text = 'Look through your commands history:'
        bot.send_message(user_id, text)
        for item in history:
            text = f'Command: {item[1]}'
            text += f'\nDate & Time: {item[2]}'
            text += f'\nFounded hotels: {item[3]}'
            bot.send_message(user_id, text)
    bot.send_message(user_id, 'For restart tap: /start')


def display_help(user_id: int) -> None:
    for name, info in constants.HELP_INFO.items():
        bot.send_message(user_id,
                         name + info)
    bot.send_message(user_id,
                     'To begin searching tap: /start')


def step_after_pics_query(user: User) -> None:
    if user.command == 'bestdeal':
        """Ask min price"""
        text = 'Input minimum price for hotel'
        bot.send_message(user.user_id, text)
    else:
        user.set_state(11)
        display_hotels(user, user.user_id)


if __name__ == '__main__':
    bot.infinity_polling()
