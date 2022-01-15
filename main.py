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


class NoneUsrError(Exception):
    pass


logger.configure(**log_setup.logger_setup)
bot = TeleBot(config('TOKEN'))
user_history = UserHistory()
user_history.setup()


# button_cancel = types.ReplyKeyboardMarkup()
# button_cancel.add()
# hide_cancel = types.ReplyKeyboardRemove()


def create_keyboard(items: dict, prefix: str,
                    lang_id: int) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        keyboard=[
            [
                types.InlineKeyboardButton(
                    text=name[lang_id],
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
        text = constants.PHRASES['welcome'][user.lang_id]
        bot.send_message(user_id, text)
        user = User.get_user(user_id)
    else:
        user.init_req_params()

    text = constants.PHRASES['sel_cmd'][user.lang_id]
    bot.send_message(
        user_id,
        text,
        reply_markup=create_keyboard(constants.MAIN_MENU, 'cmd',
                                     user.lang_id)
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
    try:
        user = get_user(user_id)
    except NoneUsrError:
        pass
    else:
        result, key, step = DetailedTelegramCalendar().process(call.data)
        if not result and key:
            text = f"{constants.PHRASES['select'][user.lang_id]} " \
                   f"{LSTEP[step]}"
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.message_id,
                                  text=text,
                                  reply_markup=key)
        elif result:
            user.req_params['check_in'] = result
            user.set_state(4)
            logger.info(f'{user_id} selected check-in date')
            text = constants.PHRASES['days'][user.lang_id]
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.message_id,
                                  text=text)


@bot.callback_query_handler(func=None)
def command_callback(call: CallbackQuery):
    command: list = call.data.split()
    user_id = call.message.chat.id

    try:
        user = get_user(user_id)
    except NoneUsrError:
        pass
    else:
        if command[0] == 'cmd' and user.state == 0:
            logger.info(f'{user_id} tapped command: {command[1]}')
            if command[1] == 'history':
                user.state = 11
                display_history(user_id=user_id, lang_id=user.lang_id)
            elif command[1] == 'help':
                user.state = 11
                display_help(user_id=user_id, lang_id=user.lang_id)
            else:
                text = constants.PHRASES['input_town'][user.lang_id]
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
            text = constants.PHRASES['sel_ah'][user.lang_id]
            bot.edit_message_text(
                chat_id=user_id,
                message_id=call.message.message_id,
                text=text,
                reply_markup=create_keyboard(constants.HOTELS_AMOUNT,
                                             'ham', user.lang_id))
        elif command[0] == 'ham' and user.state == 2:
            logger.info(f'{user_id} selected amount of hotels')
            user.state = 3
            user.req_params['hotels_amount'] = command[1]
            """Ask check-in date"""
            calendar, step = DetailedTelegramCalendar(
                locale=constants.LANGUAGE_FOR_CALENDAR[user.lang_id]
            ).build()
            text = constants.PHRASES['sel_date'][user.lang_id]
            bot.send_message(user_id, text)
            text = f"{constants.PHRASES['select'][user.lang_id]} " \
                   f"{LSTEP[step]}"
            bot.send_message(user_id,
                             text,
                             reply_markup=calendar)
        elif command[0] == 'pic' and user.state == 5:
            logger.info(f'{user_id} selected the need of pictures')
            if command[1] == 'yes':
                user.state = 6
                """Ask photo amount"""
                text = constants.PHRASES['sel_np'][user.lang_id]
                bot.edit_message_text(
                    chat_id=user_id,
                    message_id=call.message.message_id,
                    text=text,
                    reply_markup=create_keyboard(constants.PHOTO_AMOUNT,
                                                 'pnum', user.lang_id))
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
            text = f"{constants.PHRASES['err_cmd'][user.lang_id]}" \
                   f"\n{constants.PHRASES['restart'][user.lang_id]}"
            bot.send_message(user_id, text)


@bot.message_handler(content_types=['text'])
def get_text_messages(message) -> None:
    user_id = message.chat.id
    try:
        user = get_user(user_id)
    except NoneUsrError:
        pass
    else:
        if user.state == 1:
            display_found_locations_menu(message.text, user_id,
                                         user.lang_id)
        elif user.state == 4:
            check_and_save_days_delta(message.text,
                                      message.message_id, user)
        elif user.command == 'bestdeal' and user.state == 7:
            check_and_save_min_price(message.text, user)
        elif user.command == 'bestdeal' and user.state == 8:
            check_and_save_max_price(message.text, user)
        else:
            logger.warning(f'{user_id} typed wrong text')
            text = constants.PHRASES['err_txt'][user.lang_id]
            bot.send_message(user_id, text)


def check_and_save_days_delta(text: str, mess_id: int, user: User) -> None:
    try:
        logger.info(f'{user.user_id} typed amount of days')
        days = abs(int(text))
        if days == 0:
            days += 1
        user.state = 5
        user.req_params['days'] = days
        """Ask about photo"""
        text = constants.PHRASES['need_pics'][user.lang_id]
        bot.send_message(
            chat_id=user.user_id,
            text=text,
            reply_markup=create_keyboard(constants.PHOTO_ASK,
                                         'pic', user.lang_id)
        )
        # bot.edit_message_text(
        #     chat_id=user.user_id,
        #     message_id=mess_id,
        #     text='Do you want to see hotel pictures?',
        #     reply_markup=create_keyboard(constants.PHOTO_ASK, 'pic'))
    except Exception as e:
        logger.error(f'User {user.user_id}: {e}')
        text = constants.PHRASES['err_days'][user.lang_id]
        bot.send_message(user.user_id,text)


def check_and_save_min_price(text: str, user: User) -> None:
    try:
        logger.info(f'{user.user_id} typed min price')
        price = abs(int(float(text.replace(',', '.'))))
        user.state = 8
        user.req_params['price_min'] = price
        text = constants.PHRASES['input_maxp'][user.lang_id]
        bot.send_message(user.user_id, text)
    except Exception as e:
        logger.error(f'User {user.user_id}: {e}')
        text = f"{constants.PHRASES['err_price'][user.lang_id]}" \
               f"\n{constants.PHRASES['input_minp'][user.lang_id]}"
        bot.send_message(user.user_id, text)


def check_and_save_max_price(text: str, user: User) -> None:
    try:
        logger.info(f'{user.user_id} typed max price')
        price = abs(int(float(text.replace(',', '.'))))
        if price <= user.req_params['price_min']:
            logger.error(f'User {user.user_id}: typed wrong max price'
                         f'Less than the min price')
            text = f"{constants.PHRASES['err_price'][user.lang_id]}" \
                   f"\n{constants.PHRASES['err_maxp'][user.lang_id]}" \
                   f"\n{constants.PHRASES['input_maxp'][user.lang_id]}"
            bot.send_message(user.user_id, text)
        else:
            user.state = 9
            user.req_params['price_max'] = price
            text = constants.PHRASES['input_dist'][user.lang_id]
            bot.send_message(chat_id=user.user_id,
                             text=text,
                             reply_markup=create_keyboard(
                                 constants.DISTANCE, 'dst', user.lang_id))
    except Exception as e:
        logger.error(f'User {user.user_id}: {e}')
        text = f"{constants.PHRASES['err_price'][user.lang_id]}" \
               f"\n{constants.PHRASES['input_maxp'][user.lang_id]}"
        bot.send_message(user.user_id, text)


def display_found_locations_menu(mess_text: str, user_id: int,
                                 lang_id: int) -> None:
    """Display menu of found locations"""
    locations = get_locations_from_api(mess_text)
    if locations.get('err'):
        logger.error(f"User {user_id} {locations['err']}")
        # bot.send_message(user_id, locations['err'])
        text = constants.PHRASES['err_town_search'][lang_id]
        bot.send_message(user_id, text)
    else:
        text = constants.PHRASES['sel_loc'][lang_id]
        bot.send_message(chat_id=user_id,
                         text=text,
                         reply_markup=create_keyboard(
                             locations, 'loc', lang_id))


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
        text = f"{constants.PHRASES['none_htls'][user.lang_id]}" \
               f"\n{constants.PHRASES['restart'][user.lang_id]}"
        bot.send_message(chat_id, text)
    else:
        hotel_texts = []
        for hotel in hotels:
            if hotel.get('text'):
                hotel_texts.append(hotel['text'])
                bot.send_message(chat_id, hotel['text'],
                                 disable_web_page_preview=True)
            if hotel.get('pictures'):
                display_pictures(hotel['pictures'], chat_id)

        if len(hotel_texts) > 0:
            hotel_texts = '|'.join(hotel_texts)
            command = constants.MAIN_MENU[user.command][user.lang_id]
            save_result_to_history(user.user_id, command, hotel_texts)

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
            bot.send_photo(chat_id, pictures[0])
    except Exception as e:
        logger.error(f'User {chat_id}: {e}')


def save_result_to_history(user_id: int, command: str,
                           text: str) -> None:
    date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user_hist = UserHistory()
    user_hist.add_user_command(user_id, command, date, text)


def display_history(user_id: int, lang_id: int) -> None:
    history_thread = UserHistory()
    history: list = history_thread.get_commands_for_user(user_id)
    if len(history) == 0:
        text = constants.PHRASES['none_hist'][lang_id]
        bot.send_message(user_id, text)
    else:
        text = constants.PHRASES['hist_mess'][lang_id]
        bot.send_message(user_id, text)
        for item in history:
            text = f'Command: {item[1]}'
            text += f'\nDate & Time: {item[2]}'
            bot.send_message(user_id, text)
            for hotel_text in item[3].split('|'):
                bot.send_message(user_id, hotel_text)
    bot.send_message(user_id, 'For restart tap: /start')


def display_help(user_id: int, lang_id: int) -> None:
    for name, info in constants.HELP_INFO[lang_id].items():
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


def get_user(user_id: int) -> User:
    user = User.get_user(user_id)
    if not user:
        logger.warning(f'User {user_id} tried to begin without /start')
        text = f"{constants.PHRASES['none_usr'][user.lang_id]}" \
               f"\n{constants.PHRASES['restart'][user.lang_id]}"
        bot.send_message(user_id, text)
        raise NoneUsrError
    else:
        return user


if __name__ == '__main__':
    bot.infinity_polling()
