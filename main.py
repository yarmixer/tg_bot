from telebot import *
import sqlite3

bot = TeleBot('6012349907:AAEJI30cmP1mhiv6W1dcs6UKfmWVz9U3yPU')
db_file = "for school.db"
con = sqlite3.connect(db_file, check_same_thread=False)
cur = con.cursor()


@bot.message_handler(commands=['start'])
def start_main(message):
    # Старт - классическая команда у всех ботов, создается для начала работы и проверки работоспобности проекта
    bot.send_message(message.chat.id, f'привет, {message.from_user.first_name}, это школьный цифоровой дневник в '
                                      f'телеграмм')


@bot.message_handler(commands=["help"])
def get_help(message):
    bot.send_message(message.chat.id, "/start - начать программу\n/register - регистрация в базе данных\n"
                                      "/reset - сбросить данные \n/help - помощь по командам")


@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой")
    # бот будет сбрасывать данные !!!!!!!!!!!!!!!!!!!!!!


@bot.message_handler(commands=['register'])  # декоратор обработки комады
def register(message):  # Обработка сообщения
    bot.send_message(message.chat.id, "Введите логин: ")  # Отправка запроса пользователю
    bot.register_next_step_handler(message, user_name)  # Получаение ответа от пользователя


def user_name(message):  # Обработка ответа
    res = cur.execute("""SELECT FIO from ученики UNION 
    SELECT FIO from учителя UNION SELECT FIO from родители""").fetchall()
    # Запрос в базу данных, ФИО учителей, родителей и учеников.
    res_str = ''
    for i in range(len(res)):
        for j in range(len(res[i])):
            res_str += ''.join(res[i][j])
        res_str += ', '
    print(res_str)
    name = message.text.strip()
    if name in res_str:  # Поиск в базе данных и если да, то отправка запроса пароля
        bot.send_message(message.chat.id, "Введите пароль: ")  # Запрос пароля
        bot.register_next_step_handler(message, user_get_password, name)  # Переход к обработке полученного пароля
    else:
        bot.send_message(message.chat.id, "Вас нет в базе данных(либо опечатались), обратитесь за помощью к @yarmixer")
        # Если не нашлось ФИО в базе данных


def user_get_password(message, name):  # Обработка пароля
    password = message.text.strip()  # переменная с паролем
    res = cur.execute(f"""SELECT password from ученики WHERE FIO='{name}'
    UNION SELECT password from учителя WHERE FIO='{name}' 
    UNION SELECT password from родители WHERE FIO='{name}'""").fetchall()  # Запрос в базу данных, поиск пароля по ФИО

    print(password)
    print(str(res[0][0]))
    if password == str(res[0][0]):  # Проверка пароля
        bot.send_message(message.chat.id, "Вы успешно вошли в аккаунт, теперь может воспользоваться /menu (ученик),"
                                          " /pmenu (родитель), /tmenu (учитель)")
        print(message.chat.id)
        cur.execute(f"""UPDATE ученики SET chat_id = '{message.chat.id}' WHERE FIO = '{name}'""").fetchall()
        cur.execute(f"""UPDATE родители SET chat_id = '{message.chat.id}' WHERE FIO = '{name}'""").fetchall()
        cur.execute(f"""UPDATE учителя SET chat_id = '{message.chat.id}' WHERE FIO = '{name}'""").fetchall()
        # Регистрация аккаунта в базе данных
        con.commit()  # Подтверждение изменений
    else:
        bot.send_message(message.chat.id, "Неверный пароль, за у точнениями обратитесь к @yarmixer"
                                          " или попробуйте снова /register")  # Если проверка пароля не удалась, или
        # пароль не совпал


@bot.message_handler(commands=['pmenu'])
def pmenu(message):
    res = cur.execute("""SELECT chat_id FROM родители""").fetchall()  # запрос из базы данных chat_id из учеников
    res_sr = ''
    for i in res:
        res_sr += str(i[0]) + ', '
    if str(message.chat.id) in res_sr:  # проверка на присутствия регистрации аккаунта
        print('ок')
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton('Оценки', callback_data='question_1')
        btn2 = types.InlineKeyboardButton('Расписание', callback_data='question_2')
        btn3 = types.InlineKeyboardButton('Домашнее задание', callback_data='question_3')
        markup.add(btn1, btn2, btn3)
        bot.send_photo(message.chat.id, open('img/род меню.jpg', 'rb'), reply_markup=markup, caption='меню родителя')
    print('...')


@bot.message_handler(commands=['menu'])  # декоратор в библеотеке Telebot
def menu(message):  # обработка команды /menu
    res = cur.execute("""SELECT chat_id FROM ученики""").fetchall()  # запрос из базы данных chat_id из учеников
    res_sr = ''
    for i in res:
        res_sr += str(i[0]) + ', '
    if str(message.chat.id) in res_sr:  # проверка на присутствия регистрации аккаунта
        print('ок')
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton('Оценки', callback_data='question_4')  # кнопка оценок
        btn2 = types.InlineKeyboardButton('Расписание', callback_data='question_5')  # кнопка расписания
        btn3 = types.InlineKeyboardButton('Домашка', callback_data='question_6')  # кнопка домашнего задания
        markup.add(btn1, btn2, btn3)  # кнопки
        bot.send_photo(message.chat.id, open('img/меню2.jpg', 'rb'), reply_markup=markup, caption='меню')  # вывод меню


@bot.message_handler(commands=['tmenu'])
def tmenu(message):
    res = cur.execute("""SELECT chat_id FROM учителя""").fetchall()  # запрос из базы данных chat_id из учеников
    res_sr = ''
    for i in res:
        res_sr += str(i[0]) + ', '
    if str(message.chat.id) in res_sr:  # проверка на присутствия регистрации аккаунта
        print('ок')
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton('Выставить оценку', callback_data='question_7')  # кнопка оценок
        btn2 = types.InlineKeyboardButton('Школьное расписание', callback_data='question_8')  # кнопка расписания
        btn3 = types.InlineKeyboardButton('Задать домашнее задание', callback_data='question_9')
        # кнопка домашнего задания
        markup.add(btn1, btn2, btn3)  # кнопки
        bot.send_photo(message.chat.id, open('img/уч меню.jpg', 'rb'), reply_markup=markup, caption='меню')
        # вывод меню


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == 'question_1':
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton("Назад в меню", callback_data='back1')
            markup.add(btn)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_photo(call.message.chat.id, open('img/оценки.png', 'rb'), reply_markup=markup,
                           caption='оценки вашего ребенка')

        elif call.data == 'question_2':
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton("Назад в меню", callback_data='back1')
            markup.add(btn)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_photo(call.message.chat.id, open('img/расписание2.png', 'rb'), reply_markup=markup,
                           caption='расписание')
        elif call.data == 'question_3':
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton("Назад в меню", callback_data='back1')
            markup.add(btn)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(chat_id=call.message.chat.id, text=f'домашнее задание на завтра:\n'
                                                                f'русский: упр243\n'
                                                                f'математика: номер 63, 57 выучить теорему\n'
                                                                f'биологоия: нет дз\n'
                                                                f'литература: подготовить доклад\n'
                                                                f'физ-ра: нет дз', reply_markup=markup)
        elif call.data == 'question_4':
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton("Назад в меню", callback_data='back2')
            markup.add(btn)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_photo(call.message.chat.id, open('img/оценки.png', 'rb'), reply_markup=markup)

        elif call.data == 'question_5':
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton("Назад в меню", callback_data='back2')
            markup.add(btn)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_photo(call.message.chat.id, open('img/расписание2.png', 'rb'), reply_markup=markup)

        elif call.data == 'question_6':
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton("Назад в меню", callback_data='back2')
            markup.add(btn)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(chat_id=call.message.chat.id, text=f'домашнее задание на завтра:\n'
                                                                f'русский: упр243\n'
                                                                f'математика: номер 63, 57 выучить теорему\n'
                                                                f'биологоия: нет дз\n'
                                                                f'литература: подготовить доклад\n'
                                                                f'физ-ра: нет дз', reply_markup=markup)

        elif call.data == 'question_7':
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton("назад", callback_data='back3')
            markup.add(btn)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(chat_id=call.message.chat.id, text='функция в разработке', reply_markup=markup)

        elif call.data == 'question_8':
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton("Назад в меню", callback_data='back3')
            markup.add(btn)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_photo(call.message.chat.id, open('img/расписание2.png', 'rb'), reply_markup=markup)

        elif call.data == 'question_9':
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton("Назад в меню", callback_data='back3')
            markup.add(btn)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(chat_id=call.message.chat.id, text="функция в разработке", reply_markup=markup)

        elif call.data == 'back1':
            markup = types.InlineKeyboardMarkup(row_width=3)
            btn1 = types.InlineKeyboardButton('Оценки', callback_data='question_1')
            btn2 = types.InlineKeyboardButton('Расписание', callback_data='question_2')
            btn3 = types.InlineKeyboardButton('Домашнее задание', callback_data='question_3')
            markup.add(btn1, btn2, btn3)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_photo(call.message.chat.id, open('img/род меню.jpg', 'rb'), reply_markup=markup,
                           caption='меню родителя')

        elif call.data == 'back2':
            markup = types.InlineKeyboardMarkup(row_width=3)
            btn1 = types.InlineKeyboardButton('Оценки', callback_data='question_4')
            btn2 = types.InlineKeyboardButton('Расписание', callback_data='question_5')
            btn3 = types.InlineKeyboardButton('Домашка', callback_data='question_6')
            markup.add(btn1, btn2, btn3)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_photo(call.message.chat.id, open('img/меню2.jpg', 'rb'), reply_markup=markup,
                           caption='меню ученика')

        elif call.data == 'back3':
            markup = types.InlineKeyboardMarkup(row_width=3)
            btn1 = types.InlineKeyboardButton('Выставить оценку', callback_data='question_7')
            btn2 = types.InlineKeyboardButton('Школьное расписание', callback_data='question_8')
            btn3 = types.InlineKeyboardButton('Задать домашнее задание', callback_data='question_9')
            markup.add(btn1, btn2, btn3)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_photo(call.message.chat.id, open('img/уч меню.jpg', 'rb'), reply_markup=markup,
                           caption='меню учителя')


@bot.message_handler(commands=['menu'])  # декоратор в библеотеке Telebot
def menu(message):  # обработка команды /menu
    res = cur.execute("""SELECT chat_id FROM ученики""").fetchall()  # запрос из базы данных chat_id из учеников
    res_sr = ''
    for i in res:
        res_sr += str(i[0]) + ', '
    if str(message.chat.id) in res_sr:  # проверка на присутствия регистрации аккаунта
        print('ок')
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton('Оценки', callback_data='question_4')  # кнопка оценок
        btn2 = types.InlineKeyboardButton('Расписание', callback_data='question_5')  # кнопка расписания
        btn3 = types.InlineKeyboardButton('Домашка', callback_data='question_6')  # кнопка домашнего задания
        markup.add(btn1, btn2, btn3)  # кнопки
        bot.send_photo(message.chat.id, open('img/меню2.jpg', 'rb'), reply_markup=markup, caption='меню')  # вывод меню


@bot.message_handler(commands=['tmenu'])
def tmenu(message):
    res = cur.execute("""SELECT chat_id FROM учителя""").fetchall()  # запрос из базы данных chat_id из учеников
    res_sr = ''
    for i in res:
        res_sr += str(i[0]) + ', '
    if str(message.chat.id) in res_sr:  # проверка на присутствия регистрации аккаунта
        print('ок')
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton('Выставить оценку', callback_data='question_7')  # кнопка оценок
        btn2 = types.InlineKeyboardButton('Школьное расписание', callback_data='question_8')  # кнопка расписания
        btn3 = types.InlineKeyboardButton('Задать домашнее задание', callback_data='question_9')
        # кнопка домашнего задания
        markup.add(btn1, btn2, btn3)  # кнопки
        bot.send_photo(message.chat.id, open('img/уч меню.jpg', 'rb'), reply_markup=markup, caption='меню')
        # вывод меню


@bot.message_handler(content_types=['text'])
def name_get(message):
    text = message.text.strip()  # заглушка для отладки
    print(text)


bot.infinity_polling()
