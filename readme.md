HotelsComBot- это бот для поиска отелей через Telegram
Бот HotelsComBot позволяет подбирать отели прямо в мессенджере Telegram используя различные критерии поиска. Адрес бота: http://t.me/super_hotels_bot.

Возможности бота
Данный бот позволяет:
•	подбирать отели по самой низкой или самой высокой цене;
•	подбирать отели по лучшему соотношению цена/расстояние от центра города;
•	выводить историю команд пользователя и найденных по этим командам отелей
Requirements
•	requests>=2.26.0 - библиотека requests
•	python-decouple>=3.5 работа с внутренним файлом в котором хранятся токены API
•	pyTelegramBotAPI>=4.2.2 - Python Telegram Bot API
•	
Вы можете установить все зависимости, выполнив следующую команду: pip install -r requirements.txt
Работа с историей пользователя
Работа с историей пользователя организована с помощью библиотеки sqlite3. При первом запуске скрипта создается файл базы данных: users_history.sqlite, в котором создается таблица usersLog и индекс usersIndex по полю user_id, для быстрого поиска при большом количестве записей.

Логирование
Для удобства отладки реализовано логирование с помощью библиотеки loguru. В лог попадает информация о каждом действии пользователя и ошибках, возникающих во время работы скрипта. Лог пишется в файл logs/bot.log
Статусы пользователя
Для корректной работы программы используется статус пользователя, который определяется, выполненным на данный момент, шагом пользователя и название активной команды. Эти данные хранятся в соответствующих переменных в классе User.
Cтатусы:
•	“1” – пользователь нажал команду в начальном меню 
•	“2” – пользователь выбрал конкретную локацию из меню локаций
•	“3” – пользователь выбрал количество отелей для просмотра
•	“4” – пользователь дату заселения
•	“5” – пользователь указал количество дней пребывания в отеле
Пользователь принимает решение о необходимости вывода фотографий, если он ответил положительно, то:
•	“6” – пользователь хочет видеть фотографии
•	“7” – пользователь выбрал количество фотографий
если он ответил отрицательно, то: 
•	“7” –количество фотографий = 0
Если активная команда bestdeal:
•	“8” – пользователь ввел минимальную цену за номер
•	“9” – пользователь ввел максиимальную цену за номер
•	“10” – пользователь ввел максимальную удаленность от центра
Статус “11” означает что пользователь прошел все шаги до вывода информации на экран

Начало работы с ботом HotelsComBot
Работа с ботом начинается с ввода команды /start. Если новый пользователь попытается начать работу не со стартовой команды, то бот выведет сообщение об ошибке и предложит пользователю напечатать /start. 

 С помощью команды /start вызывается главное меню:
![](imgs/main_menu.png)
•	Info about commands- краткое описание команд
•	Get the cheapest hotels- топ дешевых отелей
•	Get the most expensive hotels - топ дорогих отелей
•	Get the cheapest hotels closer to the center - лучшие предложения
•	Get the history of user commands- вывод на экран истории команд пользователя
Чтобы заново начать поиск, необходимо ввести команду /start. При этом вне зависимости от состояния(шага) пользователя, будет вызвано главное меню и сброшен статус пользователя в классе UsersLog.
Get the cheapest hotels & Get the most expensive hotels
1.	После нажатия кнопки Get the cheapest hotels или Get the most expensive hotels, бот попросит ввести город, в котором вы хотите искать отели.
2.	Введите название населенного пункта. Бот выполнит запрос к hotels API и выведет список локаций, названия которых похожи на введенный город. Если бот не найдет ни одну локацию, то бот сообщит об этом и предложит ввести название заново или начать с главного меню.
Пример ответа на запрос "tokyo":
 ![](imgs/loc_menu.png) 
3.	Выберите один из предложенных вариантов, наиболее подходящих вашему запросу или, снова напечатайте название города для нового поиска, если список совпадений вас не удовлетворил.
4.	На следующем шаге, бот выведет меню для выбора количества отелей, которое вы хотите видеть в качестве результата. Нажмите кнопку с подходящим количеством отелей.
5.	После выбора количества отелей, бот спросит о необходимости вывода фотографий и при положительном ответе- количества фотографий для каждого отеля.
6.	В итоге бот выполнит запрос к hotels API и выведет список отелей с указанием названия, адреса, расстояния от центра и цены.
Пример результата: 
 ![](imgs/result.png)
Get the cheapest hotels closer to the center
Первые действия схожи с действиями для команд Get the cheapest hotels и Get the most expensive hotels(пункты № 1-5)
Первые действия схожи с действиями для команд Get the cheapest hotels и Get the most expensive hotels(пункты № 1-5)
6.	Бот запросит минимальную цену за комнату. Введите число.
7.	Бот запросит максимальную цену за комнату. Введите число. Максимальная цена должна быть больше минимальной.
8.	Бот запросит максимальное расстояние от центра города до отеля. Введите число.
9.	В итоге бот выполнит запрос к hotels API и выведет список отелей с указанием названия, адреса, расстояния от центра и цены.

Get the history of user commands
После нажатия кнопки Get thr history of user commands бот выведет историю команд и найденных при этом отелей.
Пример результата:
 
Рекомендации
Название города должно состоять только из букв английского алфавита и символа дефис. Цена представляет собой целое или вещественное число, максимальная цена должна быть больше минимальной и не равна нулю. Максимальное расстояние от центра города должно быть написано в виде положительного целого или вещественного числа. 
