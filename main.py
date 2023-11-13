import telebot
from telebot import types
import datetime
from DB.database import DB
from visualizer import Visualizer
import logging
import pandas as pd
import configparser
import os
import bot_answers

from User import telegram_user


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(f"Balance_Bot.log", mode="w")
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info(f"Logget for module BalanceBot_telegaram")


config = configparser.ConfigParser()
config.read("conf.ini")
TOKEN = config["Telegram"]["token"]


users = {}
db = DB()
bot = telebot.TeleBot(token=TOKEN)


def logged(func):
    def wrapper(message, **kwargs):
        print(type(message))
        try:
            func(message, **kwargs)
            logger.info(f"User {message.chat.id}. Message: {message}")
            return
        except Exception as e:
            bot.send_message(
                message.chat.id,
                bot_answers.error_message,
            )
            logger.exception(f"User {message.chat.id} error. Message: {message} \n {e}")

    return wrapper


def go_to_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    users[f"{message.chat.id}"].clear_data()
    markup.add("Запись данных", "Вывод данных", "Удаление данных")
    msg = bot.reply_to(message, "Выбирите нужное вам действие", reply_markup=markup)
    bot.register_next_step_handler(msg, action_choosing)


@bot.message_handler(commands=["help", "start"])
@logged
def send_welcome(message):
    user = telegram_user(chatID=message.chat.id, name=message.from_user.first_name)
    db.create_new_table()
    users[f"{message.chat.id}"] = user
    if not db.get_user(telegram_id=message.chat.id):
        db.add_user(telegram_id=message.chat.id, ban=False)
        msg = bot.reply_to(
            message,
            bot_answers.welcome,
        )
        msg = bot.reply_to(
            message,
            bot_answers.debit_categorues_request,
        )
        bot.register_next_step_handler(msg, select_types_debit)
    else:
        for i in db.get_types(message.chat.id, debit=True)[0]:
            user.append_types_debit(i)
            print(i)
        print(user.get_types_debit())
        for i in db.get_types(message.chat.id, debit=False)[0]:
            user.append_types_credit(i)
            print(i)
        print(user.get_types_credit())
        msg = bot.reply_to(
            message,
            f"Здравствуйте, {message.from_user.first_name}. Можете продолжить пользование сервисом.",
        )
        go_to_menu(message)


@logged
def select_types_debit(message):
    msg = [value.strip() for value in message.text.lower().split(",")]
    for i in msg:
        users[f"{message.chat.id}"].append_types_debit(i)
        print(i)
    db.record_types(
        telegram_id=message.chat.id,
        types=users[f"{message.chat.id}"].get_types_debit(),
        debit=True,
    )
    msg = bot.reply_to(
        message,
        bot_answers.credit_categorues_request,
    )
    bot.register_next_step_handler(msg, select_types_credit)


def select_types_credit(message):
    msg2 = []
    for i in message.text.lower().split(","):
        msg2.append(i.strip())
    for i in msg2:
        users[f"{message.chat.id}"].append_types_credit(i)
        print(i)
    db.record_types(
        telegram_id=message.chat.id,
        types=users[f"{message.chat.id}"].get_types_credit(),
        debit=False,
    )
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("menu")
    msg = bot.reply_to(
        message,
        bot_answers.end_welcome,
        reply_markup=markup,
    )
    bot.register_next_step_handler(msg, menu)


@logged
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Запись данных", "Вывод данных", "Удаление данных")
    msg = bot.reply_to(message, "Выбирите нужное вам действие", reply_markup=markup)
    bot.register_next_step_handler(msg, action_choosing)


def action_choosing(message):
    if message.text == "Запись данных":

        @logged
        def data_write(message):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("Доход", "Расход", "Вернуться в меню")
            msg = bot.reply_to(
                message,
                bot_answers.record_type_request,
                reply_markup=markup,
            )
            bot.register_next_step_handler(msg, debit_or_credit)
            users[f"{message.chat.id}"].set_data(index="delete", value=False)

        data_write(message)
    elif message.text == "Вывод данных":

        @logged
        def data_output(message):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(
                "За период в таблицы",
                "Excel документ",
                "Вывод диаграммы",
                "Вывод статистики",
                "Вернуться в меню",
            )
            msg = bot.reply_to(message, "Выбирите действие", reply_markup=markup)
            bot.register_next_step_handler(msg, period_data_select)

        data_output(message)
    elif message.text == "Удаление данных":

        @logged
        def delete_data(message):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(
                "Доход", "Расход", "Тип расхода", "Тип дохода", "Вернуться в меню"
            )
            users[f"{message.chat.id}"].set_data(index="delete", value=True)
            msg = bot.reply_to(
                message,
                "Укажите какую запись хотите удалить, доход/расход",
                reply_markup=markup,
            )
            bot.register_next_step_handler(msg, debit_or_credit)

        delete_data(message)


def debit_or_credit(message):
    def credit_debit(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Сегодня", "Вернуться в меню")
        msg = bot.reply_to(
            message,
            bot_answers.date_request,
            reply_markup=markup,
        )
        bot.register_next_step_handler(msg, select_date_1)
        value = False if message.text == "Расход" else True
        users[f"{message.chat.id}"].set_data(index="debit", value=value)

    def choice_type(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if message.text == "Тип расхода":
            value = False
            types_list = users[f"{message.chat.id}"].get_types_credit()
        else:
            value = True
            types_list = users[f"{message.chat.id}"].get_types_debit()
        users[f"{message.chat.id}"].set_data(index="debit", value=value)
        for i in types_list:
            markup.add(i)
        markup.add("Вернуться в меню")
        msg = bot.reply_to(
            message,
            f"Укажите категорию: {types_list}",
            reply_markup=markup,
        )
        bot.register_next_step_handler(msg, delete_type)

    action_types = {
        "Вернуться в меню": go_to_menu,
        "Доход": credit_debit,
        "Расход": credit_debit,
        "Тип расхода": choice_type,
        "Тип дохода": choice_type,
    }

    @logged
    def action(action_types, msg):
        action_types[message.text](message=msg)

    action(action_types, msg=message)


def select_date_1(message):
    if message.text == "Вернуться в меню":
        go_to_menu(message=message)
        return
    elif message.text == "Сегодня":

        @logged
        def today(message):
            print("Not Aboba")
            msg = bot.reply_to(message, bot_answers.amount_request)
            bot.register_next_step_handler(msg, select_amount)
            users[f"{message.chat.id}"].set_data(
                index="date", value=str(datetime.datetime.now().date())
            )

        today(message)
    elif len(message.text) == 10 and message.text[4] == "-" and message.text[7] == "-":

        @logged
        def amount(message):
            msg = bot.reply_to(message, bot_answers.amount_request)
            bot.register_next_step_handler(msg, select_amount)
            users[f"{message.chat.id}"].set_data(index="date", value=message.text)

        amount(message)
    else:
        msg = bot.reply_to(message, bot_answers.date_error)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Сегодня", "Вернуться в меню")
        bot.register_next_step_handler(msg, select_date_1)


def select_amount(message):
    if message.text == "Вернуться в меню":
        go_to_menu(message=message)
        return
    elif len(message.text) > 9:
        msg = bot.reply_to(
            message,
            bot_answers.amount_error,
        )
        bot.register_next_step_handler(msg, select_amount)
    amount = message.text.replace(",", ".")
    try:
        amount = float(amount)
    except Exception as e:
        msg = bot.reply_to(
            message,
            bot_answers.amount_error + ". Попробуйте еще раз",
        )
        bot.register_next_step_handler(msg, select_amount)

    @logged
    def category_request(message, debit=True):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        types_ = (
            users[f"{message.chat.id}"].get_types_debit()
            if debit
            else users[f"{message.chat.id}"].get_types_credit()
        )
        print(types_)
        for i in types_:
            markup.add(i)
        back = types.KeyboardButton("Вернуться в меню")
        markup.add(back)
        msg = bot.reply_to(
            message,
            f"Укажите категорию: {types_}",
            reply_markup=markup,
        )
        bot.register_next_step_handler(msg, select_type)
        users[f"{message.chat.id}"].set_data(index="amount", value=amount)

    if users[f"{message.chat.id}"].get_data("debit"):
        category_request(message=message, debit=True)
    else:
        category_request(message=message, debit=False)


def select_type(message):
    if message.text == "Вернуться в меню":
        go_to_menu(message=message)
        return
    if users[f"{message.chat.id}"].get_data("delete"):
        users[f"{message.chat.id}"].set_data(index="type", value=message.text)
        msg = bot.reply_to(message, "Введите любой символ")
        bot.register_next_step_handler(msg, delete_data)
        return
    if not users[f"{message.chat.id}"].get_data("debit"):

        @logged
        def set_priority(message):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("1", "2", "3", "4", "5", "6", "Вернуться в меню")
            users[f"{message.chat.id}"].set_data(index="type", value=message.text)
            msg = bot.reply_to(
                message,
                bot_answers.priority_request,
                reply_markup=markup,
            )
            bot.register_next_step_handler(msg, select_priority)

        set_priority(message)
    else:

        @logged
        def record_and_back(message):
            users[f"{message.chat.id}"].set_data(index="type", value=message.text)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("Вернуться в меню")
            msg = bot.reply_to(
                message,
                f"Запись создана : {users[f'{message.chat.id}'].get_data_list()}",
                reply_markup=markup,
            )
            user = users[f"{message.chat.id}"]
            db.data_record(
                telegram_id=message.chat.id,
                amount=user.get_data("amount"),
                date=user.get_data("date"),
                type=user.get_data("type"),
                debit=user.get_data("debit"),
                priority=0,
            )
            users[f"{message.chat.id}"].clear_data()
            go_to_menu(message)

        record_and_back(message)


def select_priority(message):
    if message.text == "Вернуться в меню":
        go_to_menu(message=message)
        return

    @logged
    def record(message):
        users[f"{message.chat.id}"].set_data(index="priority", value=message.text)
        user = users[f"{message.chat.id}"]
        db.data_record(
            telegram_id=message.chat.id,
            amount=user.get_data("amount"),
            date=user.get_data("date"),
            type=user.get_data("type"),
            debit=user.get_data("debit"),
            priority=message.text,
        )
        bot.reply_to(
            message, f"Запись создана : {users[f'{message.chat.id}'].get_data_list()}"
        )
        user.clear_data()
        go_to_menu(message=message)

    record(message)


def period_data_select(message):
    if message.text == "Вернуться в меню":
        go_to_menu(message=message)
        return

    @logged
    def set_period(message):
        users[f"{message.chat.id}"].set_data(index="function", value=f"{message.text}")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            "За последние 7 дней",
            "За последний месяц",
            "За последние 3 месяца",
            "За полгода",
            "За год",
            "Вернуться в меню",
        )
        msg = bot.reply_to(message, "Укажите период", reply_markup=markup)
        bot.register_next_step_handler(msg, select_date_2)

    set_period(message)


def get_excel(message):
    @logged
    def make_xlsx(message):
        strList1 = database_query(message=message, debit=True, send_mess=False)
        firstStr = True
        for i in strList1:
            if firstStr:
                firstStr = False
                data1 = pd.DataFrame(
                    [[i[2], i[3], float(i[4]), i[6]]],
                    columns=["date", "time", "amount", "type"],
                )
                print(data1)
            data1.loc[int(data1.shape[0])] = [i[2], i[3], float(i[4]), i[6]]
        data1.to_excel(
            "Debit.xlsx",
            sheet_name="Debit",
            columns=["date", "time", "amount", "type"],
            index=False,
        )
        path = config["excel"]["debit"]
        bot.send_document(message.chat.id, open(path, "rb"))
        os.remove(path)
        strList = database_query(message=message, debit=False, send_mess=False)
        firstStr = True
        for i in strList:
            if firstStr:
                firstStr = False
                data2 = pd.DataFrame(
                    [[i[2], i[3], float(i[4]), i[5], i[6]]],
                    columns=["date", "time", "amount", "type", "priority"],
                )
            data2.loc[int(data2.shape[0])] = [i[2], i[3], float(i[4]), i[5], i[6]]
        data2.to_excel(
            "Credit.xlsx",
            sheet_name="Credit",
            columns=["date", "time", "amount", "type", "priority"],
            index=False,
        )
        path = config["excel"]["credit"]
        bot.send_document(message.chat.id, open(path, "rb"))
        os.remove(path)

    make_xlsx(message)


def database_query(message, debit, send_mess=True):
    period = {
        "За последние 7 дней": 7,
        "За последний месяц": 31,
        "За последние 3 месяца": 31 * 3,
        "За полгода": 31 * 6 - 3,
    }
    if message.text != "За год":
        dayS = period[message.text]
    else:
        dayS = 31 * 12 - 6

    data1 = db.data_getting(
        telegram_id=message.chat.id,
        debit=debit,
        date_from=str(datetime.datetime.now() - datetime.timedelta(dayS))[0:10:],
        date_to=str(datetime.datetime.now().date()),
    )
    strList = []
    strLen = 10
    indent = "\x20"
    if send_mess:
        str1 = ""
        for i in data1:
            for j in i:
                if not f"{j}" == "False" or not "{j}" == "True":
                    str1 += f"{j}"
                    if send_mess:
                        str1 += (
                            indent * 2 + (strLen - len(f"{j}")) * indent * 2
                        )  # е****й пропорциональный шрифт
            strList.append(str1)
            str1 = ""
    else:
        str1 = []
        strList = []
        for i in data1:
            for j in i:
                if not f"{j}" == ("False" or "True"):
                    if j == None:
                        str1.append("0")
                    else:
                        str1.append(f"{j}")
            strList.append(str1.copy())
            str1.clear()
    return strList


def select_date_2(message):
    action = {}

    def print_records(message, debit):
        strList = database_query(message=message, debit=True)
        bot.send_message(message.chat.id, "Дебит" if debit else "Кредит")
        for i in strList:
            bot.send_message(message.chat.id, i)

    @logged
    def choice_stat(message):
        if users[f"{message.chat.id}"].get_data("function") == "За период в таблицы":
            print_records(message, True)
            print_records(message, False)
        elif users[f"{message.chat.id}"].get_data("function") == "Excel документ":
            get_excel(message)
        elif users[f"{message.chat.id}"].get_data("function") == "Вывод диаграммы":
            make_diorama(message=message, debit=True)
            make_diorama(message=message, debit=False)
        elif users[f"{message.chat.id}"].get_data("function") == "Вывод статистики":
            statistics(message, debit=True)
        go_to_menu(message=message)
        logger.info(f"User {message.chat.id}: select_date_2 is working properly")

    choice_stat(message)


def make_diorama(message, debit=True):
    dioramaData = {}
    period = {
        "За последние 7 дней": 7,
        "За последний месяц": 31,
        "За последние 3 месяца": 31 * 3,
        "За полгода": 31 * 6 - 3,
    }
    if message.text != "За год":
        dayS = period[message.text]
    else:
        dayS = 31 * 12 - 6

    if debit:
        usersTypes = users[f"{message.chat.id}"].get_types_debit()
    else:
        usersTypes = users[f"{message.chat.id}"].get_types_credit()
    for i in usersTypes:
        sum = 0
        if i == None:
            continue
        data1 = db.data_getting(
            telegram_id=message.chat.id,
            debit=debit,
            type=i,
            date_from=str(datetime.datetime.now() - datetime.timedelta(dayS))[0:10:],
            date_to=str(datetime.datetime.now().date()),
        )
        for j in data1:
            step = 0
            for k in j:
                step += 1
                if step == 5:
                    sum += float(str(k))
        dioramaData[i] = round(sum, 2)
    types = []
    amount = []
    for i in dioramaData.keys():
        if not dioramaData[i] == 0:
            types.append(i)
            amount.append(dioramaData[i])
    path = (
        "/Users/aleksandr/Documents/Programming/Python/telegram_bot_balance/"
        + Visualizer.pie_chart_building(types=types, amounts=amount, debit=debit)
    )
    bot.send_photo(message.chat.id, open(path, "rb"))
    os.remove(path)


def statistics(message, debit=True):
    if message.text == "За последние 7 дней":
        dayS = 7
    else:
        if message.text == "За последний месяц":
            dayS = 31
        if message.text == "За последние 3 месяца":
            dayS = 31 * 3
        if message.text == "За полгода":
            dayS = 31 * 6 - 3
        else:
            dayS = 31 * 12 - 6  # вычетаем 6 т.к. есть месяца с 31 и 30 днями

    periodDebit = 0
    periodCredit = 0
    previousMonthDebit = 0
    previousMonthCredit = 0

    data1 = db.data_getting(
        telegram_id=message.chat.id,
        debit=True,
        date_from=str(datetime.datetime.now() - datetime.timedelta(dayS))[0:10:],
        date_to=str(datetime.datetime.now().date()),
    )

    data2 = db.data_getting(
        telegram_id=message.chat.id,
        debit=True,
        date_from=str(datetime.datetime.now() - datetime.timedelta(dayS + dayS * 2))[
            0:10:
        ],
        date_to=str(datetime.datetime.now() - datetime.timedelta(dayS * 2))[0:10:],
    )
    for j in data1:
        step = 0
        for k in j:
            step += 1
            if step == 5:
                periodDebit += float(str(k))
                previousMonthDebit += float(str(k))
    for j in data2:
        step = 0
        for k in j:
            step += 1
            if step == 5:
                periodCredit += float(str(k))
                previousMonthCredit += float(str(k))
    amount = []
    date = []
    for i in range(12):
        data3 = db.data_getting(
            telegram_id=message.chat.id,
            debit=True,
            date_from=str(datetime.datetime.now() - datetime.timedelta(dayS + i * 30))[
                0:10:
            ],
            date_to=str(datetime.datetime.now() - datetime.timedelta(i * 30))[0:10:],
        )
        for j in data3:
            step = 0
            for k in j:
                step += 1
                if step == 5:
                    amount.append(float(str(k)))
                if step == 3:
                    date.append(f"{k}")
    if periodDebit > previousMonthDebit:
        bot.send_message(
            message.chat.id,
            f"В прошлом расчетном периоде вы заработали меньше, нежели в текущем. \
Разница составила: {round(periodDebit - previousMonthDebit, 2)}",
        )
    else:
        bot.send_message(
            message.chat.id,
            f"В прошлом расчетном периоде вы заработали больше, нежели в текущем. \
Разница составила: {round(previousMonthDebit - periodDebit,2)}",
        )
    if periodCredit < previousMonthCredit:
        bot.send_message(
            message.chat.id,
            f"В прошлом расчетном периоде вы потратили больше, нежели в текущем. \
Разница составила: {round(periodCredit - previousMonthCredit, 2)}",
        )
    else:
        bot.send_message(
            message.chat.id,
            f"В прошлом расчетном периоде вы потратили меньше, нежели в текущем. \
Разница составила: {round(previousMonthCredit - periodCredit, 2)}",
        )

    bot.send_message(
        message.chat.id, f"За выбранный период было заработано: {round(periodDebit, 2)}"
    )
    bot.send_message(
        message.chat.id, f"За выбранный период было потрачено: {round(periodCredit, 2)}"
    )
    if not int(periodCredit) == int(periodDebit):
        bot.send_message(
            message.chat.id,
            f"Баланс не сошелся на {round(abs(periodDebit - periodCredit), 2)}",
        )

    path = (
        "/Users/aleksandr/Documents/Programming/Python/telegram_bot_balance/"
        + Visualizer.plotting(dates=date, amounts=amount)
    )
    bot.send_photo(message.chat.id, open(rf"{path}", "rb"))
    os.remove(path)


def delete_data(message):
    if message.text == "Вернуться в меню":
        go_to_menu(message=message)
        return

    @logged
    def delete(message):
        user = users[f"{message.chat.id}"]
        data = db.data_getting(
            telegram_id=message.chat.id,
            date_from=user.get_data("date"),
            date_to=user.get_data("date"),
            debit=user.get_data("debit"),
        )
        msg = ""
        if data:
            for j in data[0]:
                msg += f"{j}" + "\x20"
            msg += "\n"
            bot.send_message(message.chat.id, msg)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("Да", "Нет", "Вернуться в меню")
            msg = bot.reply_to(
                message, "Эту запись вы хотите удалить?", reply_markup=markup
            )
            bot.register_next_step_handler(msg, delete_data_step2)
        else:
            bot.send_message(message.chat.id, "Запись не найдена")
            go_to_menu(message=message)

    delete(message)


def delete_data_step2(message):
    if message.text == "Да":

        @logged
        def confirmation(message):
            req = db.data_delete(
                telegram_id=message.chat.id,
                date=users[f"{message.chat.id}"].get_data("date"),
                amount=users[f"{message.chat.id}"].get_data("amount"),
                debit=users[f"{message.chat.id}"].get_data("debit"),
                type=users[f"{message.chat.id}"].get_data("type"),
            )

            if req:
                bot.send_message(message.chat.id, "Запись удалена")
            else:
                bot.send_message(
                    message,
                    bot_answers.error_message,
                )

        confirmation(message)
    go_to_menu(message=message)
    return


def delete_type(message):
    if message.text == "Вернуться в меню":
        go_to_menu(message=message)
        return
    user = users[f"{message.chat.id}"]
    @logged
    def type_del(message):
        db.type_record_delete(
            telegram_id=message.chat.id,
            debit=user.get_data(index="debit"),
            type=message.text,
        )
    if user.get_data(index="debit"):
        user.remove_types_debit(message.text)
    else:
        user.remove_types_credit(message.text)
        
    type_del(message)
    go_to_menu(message)
    return


bot.infinity_polling()
