# -*- coding: utf-8 -*-
MAIN_MENU = {
    'help': ('Info about commands', 'Информация о командах'),
    'lang': ('Choose language', 'Выберите язык интерфейса и поиска'),
    'lowprice': ('Get the cheapest hotels', 'Топ дешевых отелей'),
    'highprice': ('Get the most expensive hotels', 'Топ дорогих отелей'),
    'bestdeal': ('Get the cheapest hotels closer to the center',
                 'Лучшее предложение по цене и удаленности от центра'),
    'history': ('Get the history of user commands',
                'История запросов пользователя')
}
LANGUAGE_MENU = {
    0: ('English', 'Английский'),
    1: ('Russian', 'Русский')
}
LANGUAGE_FOR_REQUEST = {
    0: 'en_US',
    1: 'ru_RU'
}
LANGUAGE_FOR_CALENDAR = {
    0: 'en',
    1: 'ru'
}
CURRENCY = {
    0: 'USD',
    1: 'RUB'
}
HOTELS_AMOUNT = {
    1: ('Only one hotel', 'Только один отель'),
    3: ('Three hotels', 'Три отеля'),
    5: ('Five hotels', 'Пять отелей'),
    10: ('Ten hotels', 'Десять отелей')
}
PHOTO_ASK = {
    'yes': ('Yes', 'Да'),
    'no': ('No', 'Нет')
}
PHOTO_AMOUNT = {
    1: ('Only one picture', 'Только одна фотография'),
    3: ('Three pictures', 'Три фотографии'),
    5: ('Five pictures', 'Пять фотографий'),
}
DISTANCE = {
    5: ('5 km', '5 км'),
    10: ('10 km', '10 км'),
    20: ('20 km', '20 км'),
}
HELP_INFO = (
    {'Help': ' - additional info about commands',
     'Choose language': 'choose language of interface and API search',
     'Get the cheapest hotels': ' - the bot trying to find the cheapest'
                                ' hotels in the selected town',
     'Get the most expensive hotels': ' - the bot trying to find the '
                                      'most expensive hotels '
                                      'in the selected town',
     'Best price and location': ' - the bot trying to find the cheapest'
                                'hotels closer to the center',
     'Get the history of user commands': ' - the bot shows the '
                                         'history about used commands'
                                         ' and which hotels have been found',
     'Recommendations': ' - a city name should consist only of the letters'
                        ' of selected language in main menu. English is default.'
                        ' The price is an integer or real number, the maximum'
                        ' price must be greater than the minimum and not equal'
                        ' to zero. '},
    {'Помощь': ' - дополнительна информация о командах',
     'Выберите язык': 'выберите язык сообщений и поиска',
     'Топ дешевых отелей':
         ' - бот выводит самые дешевые отели доступные в определенные даты',
     'Топ дорогих отелей':
         ' - бот выводит самые дорогие отели доступные в определенные даты',
     'Лучшее предложение по цене и удаленности от центра':
         ' - бот выводит самые дешевые отели, которые расположены не дальше '
         'определенного пользователем расстояния от центра и '
         'в диапазоне указанных цен',
     'История запросов пользователя':
         ' - бот выводит информацию о выбранных ранее пользователем командах '
         'и найденных при этом отелях',
     'Рекомендации':
         ' - название города должно состоять только  из букв языка, '
         'который выбран в пункте меню -Выберите язык-. '
         'По умолчанию: English. Цена- это целое или дробное число. '
         'Максимальная цена должна быть больше минимальной и больше нуля.'}
)
PHRASES = {
    '': ('', ''),
    'welcome': ('Welcome to the bot for searching hotels!',
                'Добро пожаловать в бот поиска отелей!'),
    'hist_mess': ('Look through your commands history:',
                  'Вот список введенных вами команд'),
    'sel_cmd': ('Select a command:', 'Выберите команду'),
    'sel_ah': ('Select amount of hotels to view',
               'Выберите  количество отелей для просмотра'),
    'sel_date': ('Select check-in date', 'Выберите дату въезда'),
    'sel_np': ('Select the number of pictures to show',
               'Выберите количество фотографий для вывода'),
    'sel_loc': ('Select a specific location',
                'Выберите конкретное место'),
    'sel_lang': ('Select language', 'Выберите язык'),
    'input_town': ('Input town to search for hotels',
                   'Введите название города для поиска'),
    'input_minp': ('Input minimum price for hotel',
                   'Введите минимальную цену'),
    'input_maxp': ('Input maximum price for hotel',
                   'Введите максимальную цену'),
    'input_dist': ('Select maximum distance from centre',
                   'Выберите максимальное расстояние от центра'),
    'need_pics': ('Do you want to see hotel pictures?',
                  'Вывести фотографии отеля?'),
    'days': ('For how many days do you plan to stay at the hotel?',
             'Сколько дней вы планируете находится в отеле?'),
    'restart': ('To call main menu and restart tap: /start',
                'Чтобы вызвать главное меню нажмите: /start'),
    'none_usr': ('For correct work begin with main menu!',
                 'Для корректной работы начните с главного меню'),
    'none_htls': ('Sorry, but there is no any hotel with such parameters',
                  'К сожалению не нашлось отелей по данным параметрам'),
    'none_hist': ('There is no any command in your history',
                  'В вашей истории нет сохраненных команд'),
    'err_cmd': ('Selected wrong command', 'Выбрана неверная команда'),
    'err_txt': ('Do not understand your text', 'Не понимаю ваш текст'),
    'err_days': ('You input wrong amount of days'
                 '\nTry again to input amount of staying days',
                 'Вы неверно ввели количество дней. '
                 '\nПопробуйте еще раз ввести количество дней'),
    'err_price': ('You input wrong price', 'Вы не правильно ввели цену'),
    'err_maxp': ('Maximum price must be more than minimum price',
                 'Максимальная цена должна быть больше минимальной'),
    'err_town_search': ('Unsuccessful attempt to search for town.'
                        '\nType another town or tap /start',
                        'Неудачная попытка поиска города.'
                        '\nВведите новое название или нажмите /start'),
    'Hotel': ('Hotel', 'Название'),
    'Address': ('Address', 'Адрес'),
    'Distance': ('Distance to city center',
                 'Расстояние до центра города'),
    'URL': ('Hotel URL', 'URL отеля'),
    'Price': ('Price a day', 'Цена за один день'),
    'Tot_price': ('Total_price:', 'Общая цена:'),
    'Command': ('Command', 'Команда'),
    'DateTime': ('Date&Time', 'Дата и время'),
    'select': ('Select', 'Выберите'),
    'Curr': ('$', 'руб'),
    'Language': ('You selected English', 'Вы выбрали Русский язык'),
}
