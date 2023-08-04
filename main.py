import telebot
from telebot import types
import datetime
from database import DB
from visualizer import Visualizer
import logging
import pandas as pd
import os
import time
from threading import Thread
from User import telegram_user


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler(f'BalanceBot_telegram.log', mode='w')
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info(f'Logget for module BalanceBot_telegaram')


TOKEN = '6307584334:AAFTbpuVN3A340IRpIbENqIwo3udCA8EPu8'
users = {}
db = DB()

bot = telebot.TeleBot(token=TOKEN) 

def go_to_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Запись данных")
    btn2 = types.KeyboardButton("Вывод данных")
    btn3 = types.KeyboardButton("Удаление данных")
    markup.add(btn1, btn2, btn3)
    msg = bot.reply_to(message, 'Выбирите нужное вам действие', reply_markup=markup)
    bot.register_next_step_handler(msg, action_choosing)       


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    try:
        user = telegram_user(chatID=message.chat.id, name=message.from_user.first_name)
        db.create_new_table(message.chat.id)
        users[f'{message.chat.id}'] = user
        msg = bot.reply_to(message, '''\
Приветствую. Я бот для ведения расходов и доходов.
С недавних пор у моего создателя завелась идея вести расходы и доходы. В Play market есть несколько неплохих приложений, но у них есть общие недостатки:
1. Большинство из них платные.
2. Они не имеют приложения на компьютер.
3. Я не хочу плодить приложения на телефоне.
4. Создателю хотелось написать какой-нибудь интересный ему проект, интегрировать в сервис базу данных.
Поэтому он решил создать меня. \n\n
Предупреждение: все данные, которые вы передаете мне, будут храниться на компьютере моего создателя. Он имею к ним полный доступ.
Но никакой информации кроме имени и ID пользователя у него о вас нет. 
''')
        msg = bot.reply_to(message, 'Перед тем как начать пользование, необходимо выбрать категории доходов и расходов.\
В дальнейшем эти категории можно будет дополнять либо сокращать. \n\nВведите категории вашего дохода в формате: зарплата, инвестиции, подработка')
        bot.register_next_step_handler(msg, select_types_debit)
        logger.info(f'User {message.chat.id} is registered. Message: {message}')
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка. Попробуйте еще раз. Создатель уже занимается ее исправлением')
        logger.exception(f'User {message.chat.id} registration error. Message: {message}')
        
        
        
        
def select_types_debit(message):
    try:
        msg = message.text
        msg2 = []
        msg = msg.lower()
        msg = msg.split(',')
        for i in msg:
           msg2.append(i.strip())
        for i in msg2:
            users[f'{message.chat.id}'].append_types_debit(i)
            print(i)

        msg = bot.reply_to(message, 'Теперь нужно указать категории расходов. Формат тот же: еда, аренда помещения, кредит')
        bot.register_next_step_handler(msg, select_types_credit)
        logger.info(f"User {message.chat.id} specified the categories of debits: {users[f'{message.chat.id}']}. Message: {message}")
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка. Попробуйте еще раз. Создатель уже занимается ее исправлением')
        logger.exception(f"User {message.chat.id} error specifying debits categories. Message: {message}")
        
    
    
    
def select_types_credit(message):
    try:
        msg = message.text
        msg2 = []
        msg = msg.lower()
        msg = msg.split(',')
        for i in msg:
           msg2.append(i.strip())
        for i in msg2:
            users[f'{message.chat.id}'].append_types_credit(i)
            print(i)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('menu')
        msg = bot.reply_to(message, 'На этом все. Теперь можете ознакомиться с меню.', reply_markup=markup)
        bot.register_next_step_handler(msg, menu)
        logger.info(f"User {message.chat.id} specified the categories of credits: {users[f'{message.chat.id}']}. Message: {message}")
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка. Попробуйте еще раз. Создатель уже занимается ее исправлением')
        logger.exception(f"User {message.chat.id} error specifying credits categories. Message: {message}")



        
def menu(message):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Запись данных")
        btn2 = types.KeyboardButton("Вывод данных")
        btn3 = types.KeyboardButton("Удаление данных")
        markup.add(btn1, btn2, btn3)
        msg = bot.reply_to(message, 'Выбирите нужное вам действие', reply_markup=markup)
        bot.register_next_step_handler(msg, action_choosing)
        logger.info(f"User {message.chat.id}: the menu is working properly. Message: {message}")
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка. Попробуйте еще раз. Создатель уже занимается ее исправлением')
        logger.exception(f"User {message.chat.id}: an error has occurred in the menu. Message: {message}")
        
        
        
def action_choosing(message):
    if message.text == 'Запись данных':
        try:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Доход")
            btn2 = types.KeyboardButton("Расход")
            back = types.KeyboardButton("Вернуться в меню")
            markup.add(btn1, btn2, back)
            msg = bot.reply_to(message, 'Укажите какую запись хотите сделать, доход/расход', reply_markup=markup)
            bot.register_next_step_handler(msg, debit_or_credit)
            logger.info(f"User {message.chat.id}: action_choosing is working properly. Message: {message}")
        except Exception as e:
            bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
            logger.exception(f"User {message.chat.id}: an error has occurred in action_choosing. Message: {message}")
            go_to_menu(message=message)
            return
    elif message.text == 'Вывод данных':
        try:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("За период в таблицы")
            btn2 = types.KeyboardButton("Excel документ")
            btn3 = types.KeyboardButton("Вывод диаграммы")
            btn4 = types.KeyboardButton("Вывод статистики")
            back = types.KeyboardButton("Вернуться в меню")
            markup.add(btn1, btn2, btn3, btn4, back)
            msg = bot.reply_to(message, 'Выбирите что хотите получить', reply_markup=markup)
            bot.register_next_step_handler(msg, period_data_select)
            logger.info(f"User {message.chat.id}: action_choosing is working properly. Message: {message}")
        except Exception as e:
            bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
            logger.exception(f"User {message.chat.id}: an error has occurred in action_choosing. Message: {message}")
            go_to_menu(message=message)
            return
    elif message.text == 'Удаление данных':
        try:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Доход")
            btn2 = types.KeyboardButton("Расход")
            back = types.KeyboardButton("Вернуться в меню")
            markup.add(btn1, btn2, back)
            msg = bot.reply_to(message, 'Укажите какую запись хотите удалить, доход/расход', reply_markup=markup)
            bot.register_next_step_handler(msg, debit_or_credit)
            logger.info(f"User {message.chat.id}: action_choosing is working properly. Message: {message}")
        except Exception as e:
            bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
            logger.exception(f"User {message.chat.id}: an error has occurred in action_choosing. Message: {message}")
            go_to_menu(message=message)
            return
        
        
        
def debit_or_credit(message):
    if message.text == 'Вернуться в меню':
        go_to_menu(message=message)
        return
    elif message.text == 'Доход':
        try:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Сегодня")
            back = types.KeyboardButton("Вернуться в меню")
            markup.add(btn1, back)
            msg = bot.reply_to(message, 'Укажите дату операции. Формат ГГГГ-ММ-ДД, пример: 2001-01-01', reply_markup=markup)
            bot.register_next_step_handler(msg, select_date_1)
            users[f'{message.chat.id}'].set_data(index = "debit", value = True)
            logger.info(f"User {message.chat.id}: debit_or_cradit is working properly. Message: {message}")
        except Exception as e:
            bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
            logger.exception(f"User {message.chat.id}: an error has occurred in debit_or_credit. Message: {message}")
            go_to_menu(message=message)
            return
    elif message.text == 'Расход':
        try:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Сегодня")
            back = types.KeyboardButton("Вернуться в меню")
            markup.add(btn1, back)
            msg = bot.reply_to(message, 'Укажите дату операции. Формат ГГГГ-ММ-ДД, пример: 2001-01-01', reply_markup=markup)
            bot.register_next_step_handler(msg, select_date_1)
            users[f'{message.chat.id}'].set_data(index = "debit", value = False)
            logger.info(f"User {message.chat.id}: debit_or_cradit is working properly. Message: {message}")
        except Exception as e:
            bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
            logger.exception(f"User {message.chat.id}: an error has occurred in debit_or_credit. Message: {message}")
            go_to_menu(message=message)
            return
            
    
def select_date_1(message):
    if message.text == 'Вернуться в меню':
        go_to_menu(message=message)
        return
    elif message.text == 'Сегодня':
        try:
            msg = bot.reply_to(message, 'Укажите сумму. Формат 334234.34 либо 23343,85')
            bot.register_next_step_handler(msg, select_amount)
            users[f'{message.chat.id}'].set_data(index = "date", value = str(datetime.datetime.now().date()))
            logger.info(f"User {message.chat.id}: select_date is working properly. Message: {message}")
        except Exception as e:
            bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
            logger.exception(f"User {message.chat.id}: an error has occurred in select_date. Message: {message}")
            go_to_menu(message=message)
            return
    elif len(message.text) == 10 and message.text[4] == '-' and message.text[7] == '-':
        try:
            msg = bot.reply_to(message, 'Укажите сумму. Формат 334234.34 либо 23343,85')
            bot.register_next_step_handler(msg, select_amount)
            users[f'{message.chat.id}'].set_data(index = "date", value = message.text)
            logger.info(f"User {message.chat.id}: select_date is working properly. Message: {message}")
        except Exception as e:
            bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
            logger.exception(f"User {message.chat.id}: an error has occurred in select_date. Message: {message}")
            go_to_menu(message=message)
            return
    else: 
        msg = bot.reply_to(message, 'Неверный формат. Введите дату заново. ')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Сегодня")
        back = types.KeyboardButton("Вернуться в меню")
        markup.add(btn1, back)
        bot.register_next_step_handler(msg, select_date_1)
            
def select_amount(message):
    if message.text == 'Вернуться в меню':
        go_to_menu(message=message)
        return
    elif len(message.text) > 9:
        msg = bot.reply_to(message, 'Неверно указана сумма. Не должно быть больше двух знаков после запятой(точки) и 6 знаков перед запятой(точки)')
        bot.register_next_step_handler(msg, select_amount)
    amount = message.text
    amount = amount.replace(',', '.')
    try:
        amount = float(amount)
    except Exception as e:
        msg = bot.reply_to(message, 'Неверно указана сумма. Не должно быть больше двух знаков после запятой(точки) и 6 знаков перед запятой(точки). Попробуйте еще раз')
        bot.register_next_step_handler(msg, select_amount)
    try:
        if users[f'{message.chat.id}'].get_data('debit'): 
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True) 
            for i in users[f'{message.chat.id}'].get_types_debit():
                markup.add(i)
            back = types.KeyboardButton("Вернуться в меню")
            markup.add(back)
            msg = bot.reply_to(message, f"Укажите категорию: {users[f'{message.chat.id}'].get_types_debit()}", reply_markup=markup)
            bot.register_next_step_handler(msg, select_type)
            users[f'{message.chat.id}'].set_data(index = "amount", value = amount)
            logger.info(f"User {message.chat.id}: select_amount is working properly. Message: {message}")
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)    
            for i in users[f'{message.chat.id}'].get_types_credit():
                markup.add(i)                
            msg = bot.reply_to(message, f"Укажите категорию: {users[f'{message.chat.id}'].get_types_credit()}", reply_markup=markup)
            bot.register_next_step_handler(msg, select_type)
            users[f'{message.chat.id}'].set_data(index = "amount", value = amount)
            logger.info(f"User {message.chat.id}: select_amount is working properly. Message: {message}")
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
        logger.exception(f"User {message.chat.id}: an error has occurred in select_type. Message: {message}")
        go_to_menu(message=message)
        return
    
    
def select_type(message):
    if message.text == 'Вернуться в меню':
        go_to_menu(message=message)
        return
    if not users[f'{message.chat.id}'].get_data('debit'):
        try:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)   
            back = types.KeyboardButton("Вернуться в меню")
            markup.add('1', '2', '3', '4', '5', '6', back)
            users[f'{message.chat.id}'].set_data(index = "type", value = message.text)
            msg = bot.reply_to(message, f"Укажите приоритет (необходимость совершения траты)", reply_markup=markup)
            bot.register_next_step_handler(msg, select_priority)
            logger.info(f"User {message.chat.id}: select_type is working properly")
        except Exception as e:
            bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
            logger.exception(f"User {message.chat.id}: an error has occurred in select_type. Message: {message}")
            go_to_menu(message=message)
            return
    else:
        try:
            users[f'{message.chat.id}'].set_data(index = "type", value = message.text)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton("Вернуться в меню")
            markup.add(back)
            msg = bot.reply_to(message, f"Запись создана : {users[f'{message.chat.id}'].get_data_list()}",  reply_markup=markup)
            bot.register_next_step_handler(msg, menu)
            db.data_record(userID=message.chat.id, 
                           amount=users[f'{message.chat.id}'].get_data('amount'),
                           date=users[f'{message.chat.id}'].get_data('date'),
                           type=users[f'{message.chat.id}'].get_data('type'),
                           debit=users[f'{message.chat.id}'].get_data('debit'),
                           priority=0)
            users[f'{message.chat.id}'].clear_data()
            logger.info(f"User {message.chat.id}: select_type is working properly")
        except Exception as e:
            bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
            logger.exception(f"User {message.chat.id}: an error has occurred in select_type. Message: {message}")
            go_to_menu(message=message)
            return
            
    
def select_priority(message):
    if message.text == 'Вернуться в меню':
            go_to_menu(message=message)
            return
    try: 
        users[f'{message.chat.id}'].set_data(index = "priority", value = message.text)
        db.data_record(userID=message.chat.id, 
                       amount=users[f'{message.chat.id}'].get_data('amount'), 
                       date=users[f'{message.chat.id}'].get_data('date'),
                       type=users[f'{message.chat.id}'].get_data('type'),
                       debit=users[f'{message.chat.id}'].get_data('debit'),
                       priority= message.text)
        msg = bot.reply_to(message, f"Запись создана : {users[f'{message.chat.id}'].get_data_list()}")
        users[f'{message.chat.id}'].clear_data()        
        go_to_menu(message=message)
        logger.info(f"User {message.chat.id}: select_priority is working properly")
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
        logger.exception(f"User {message.chat.id}: an error has occurred in select_priority. Message: {message}")
        go_to_menu(message=message)
        return
    
    

def period_data_select(message):
    if message.text == 'Вернуться в меню':
            go_to_menu(message=message)
            return
    try:
        users[f'{message.chat.id}'].set_data(index = 'function', value = f'{message.text}')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("За последние 7 дней")
        btn2 = types.KeyboardButton("За последний месяц")
        btn3 = types.KeyboardButton("За последние 3 месяца")
        btn4 = types.KeyboardButton("За полгода")
        btn5 = types.KeyboardButton("За год")
        back = types.KeyboardButton("Вернуться в меню")
        markup.add(btn1, btn2, btn3, btn4, btn5, back)
        msg = bot.reply_to(message, 'Укажите период', reply_markup=markup)
        bot.register_next_step_handler(msg, select_date_2)
        logger.info(f"User {message.chat.id}: period_data_select is working properly")
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
        logger.exception(f"User {message.chat.id}: an error has occurred in period_data_select. Message: {message}")
        go_to_menu(message=message)
        return
    
    
def get_excel(message):
    try:
        strList = database_query(message=message, debit= True, send_mess= False)
        firstStr = True
        for i in strList:
            if firstStr:
                firstStr = False            
                data1 = pd.DataFrame([[i[0], i[1], float(i[2]), i[4]]], columns=['date', 'time', 'amount', 'type'])
                print(data1)
            data1.loc[int(data1.shape[0])] = [i[0], i[1], float(i[2]), i[4]]
        data1.to_excel("Debit.xlsx", sheet_name='Debit', columns=['date', 'time', 'amount', 'type'])
        path = '/Users/aleksandr/Documents/Programming/Python/telegram_bot_balance/Debit.xlsx'
        bot.send_document(message.chat.id, open(rf'{path}', 'rb'))
        os.remove(path)
        strList = database_query(message=message, debit= False, send_mess= False)
        print(strList)
        firstStr = True
        for i in strList:
            if firstStr:
                firstStr = False
                data2 = pd.DataFrame([[i[0], i[1], float(i[2]), i[3], i[4]]], columns=['date', 'time', 'amount', 'type', 'priority'])
            data2.loc[int(data2.shape[0])] = [i[0], i[1], float(i[2]), i[3], i[4]]
        data2.to_excel("Credit.xlsx", sheet_name='Credit', columns=['date', 'time', 'amount', 'type', 'priority'])
        path = '/Users/aleksandr/Documents/Programming/Python/telegram_bot_balance/Credit.xlsx'
        bot.send_document(message.chat.id, open(rf'{path}', 'rb'))
        os.remove(path)
        logger.info(f"User {message.chat.id}: get_excel is working properly")
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
        logger.exception(f"User {message.chat.id}: an error has occurred in get_excel. Message: {message}")
        go_to_menu(message=message)
        return
    
    
def database_query(message, send_mess = True, debit = True): 
    if message.text == 'За последние 7 дней':
        data1 = db.data_getting(userID=message.chat.id, debit=debit)
    else:
        if message.text == 'За последний месяц':
            dayS = 31
        if message.text == 'За последние 3 месяца':
            dayS = 31 * 3
        if message.text == 'За полгода':
            dayS = 31 * 6 - 3
        else: dayS = 31 * 12 - 6 # вычетаем 6 т.к. есть месяца с 31 и 30 днями
        
        data1 = db.data_getting(userID=message.chat.id, debit=debit, 
                                date_from = str(datetime.datetime.now() - datetime.timedelta(dayS))[0:10:],
                                date_to = str(datetime.datetime.now().date()))
        print(data1)
    strList = []
    strLen = 10
    indent = '\x20'
    if send_mess:
        str1 = ''
        for i in data1:
            for j in i:
                if not f'{j}' == 'False' or not '{j}' == 'True':
                    str1 += f'{j}'
                    if send_mess:
                        str1 += indent * 2 + (strLen - len(f'{j}')) * indent * 2 #ебаный пропорциональный шрифт 
            strList.append(str1)                
            str1 = ''
    else:
        str1 = []
        strList = []
        for i in data1:
            for j in i:
                if not f'{j}' == ('False' or  'True'):
                    if j == None:
                        str1.append('0')
                    else: 
                        str1.append(f'{j}')
            strList.append(str1.copy())
            str1.clear()
    return strList
        
        
        # За период в таблицы")
        #     btn2 = types.KeyboardButton("Excel документ")
        #     btn3 = types.KeyboardButton("Вывод диаграммы")
        #     btn4 = types.KeyboardButton("Вывод статистики")
        #     back = types.KeyboardButton("Вернуться в меню")
        
        
def select_date_2(message):
    if message.text == 'Вернуться в меню':
            go_to_menu(message=message)
            return
    try:          
        if users[f'{message.chat.id}'].get_data('function') == 'За период в таблицы':
            strList = database_query(message=message, debit= True)
            bot.send_message(message.chat.id, 'Дебит')
            for i in strList:
                bot.send_message(message.chat.id, i)
            strList = database_query(message=message, debit= False)
            bot.send_message(message.chat.id, 'Кредит')
            for i in strList:
                bot.send_message(message.chat.id, i)
        elif users[f'{message.chat.id}'].get_data('function') == 'Excel документ':
            get_excel(message)
        elif users[f'{message.chat.id}'].get_data('function') == 'Вывод диаграммы':
            th1 = Thread(target=make_diorama, args=[message, True])
            th2 = Thread(target=make_diorama, args=[message, False])
            th1.start()
            th2.start()
        go_to_menu(message=message)
        logger.info(f"User {message.chat.id}: select_date_2 is working properly")
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка. Вы будите возращены в меню. Создатель уже занимается ее исправлением')
        logger.exception(f"User {message.chat.id}: an error has occurred in period_data_select. Message: {message}")
        go_to_menu(message=message)
        return

def make_diorama(message, debit = True):
    dioramaData = {}
    if debit:
        usersTypes = users[f'{message.chat.id}'].get_types_debit()
    else:
        usersTypes = users[f'{message.chat.id}'].get_types_credit()
    for i in usersTypes:
        sum = 0    
        if i == None:
            continue 
        data1 = db.data_getting(userID=message.chat.id, debit=debit, type=i)
        for j in data1:
            step = 0
            for k in j:
                step += 1
                if step == 3:
                    sum += float(str(k))
        dioramaData[i] = round(sum, 2)
    print(dioramaData)
    types = []
    amount = []
    for i in dioramaData.keys():
        if not dioramaData[i] == 0:
            types.append(i)
            amount.append(dioramaData[i])
    path = '/Users/aleksandr/Documents/Programming/Python/telegram_bot_balance/' + \
            Visualizer.pie_chart_building(types=types, amounts=amount)
    if debit:
        bot.send_message(message.chat.id, 'Дебит:')
    else:
        bot.send_message(message.chat.id, 'Кредит:')
    bot.send_document(message.chat.id, open(rf'{path}', 'rb'))
    os.remove(path)
    

        
bot.infinity_polling()

            