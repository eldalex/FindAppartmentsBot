#!/usr/bin/env python3
import sqlite3
from sqlite3 import Error
import telebot
import Scrapping
import datetime
import time
import json
import os
from telebot import types

bot = telebot.TeleBot(TOKEN)
log = open('/homeproject/log.txt', 'a')
log.write(f'------------------------------------------------------------\n')
log.write(f'{datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}: Старт!\n')
log.write(f'------------------------------------------------------------\n')
log.close()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    create_table()
    usinfo = (message.from_user.id,
              message.from_user.username,
              message.from_user.first_name,
              message.from_user.last_name,
              time.ctime()
              )
    send_user_info(usinfo)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Меню")
    markup.add(btn1)
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Я бот помощник поиска квартир на авито!".format(
                         message.from_user), reply_markup=markup)


@bot.message_handler(commands=['startfind'])
def startfindcommand(message):
    start_find(message.from_user.id)
    bot.send_message(message.chat.id, 'Поиск закончен')


@bot.message_handler(commands=['checkad'])
def checkad(message):
    Scrapping.check_ad(message.from_user.id)


@bot.message_handler(commands=['showme'])
def show_variants(message):
    show(message, [0])


@bot.message_handler(commands=['setsearch'])
def set_search(message):
    msg = bot.reply_to(message,
                       f"Хочешь сменить строку поиска?\nхорошо. но придётся готовить её самостоятельно☹\n"
                       f"открой avito и заполни фильтры недвижимости и скопируй получившуюся итоговую строку "
                       f"и отправь следующим сообщением.")
    bot.register_next_step_handler(msg, update_search_parameters)


@bot.message_handler(commands=['showadinfo'])
def show_ad_info(message):
    msg = bot.reply_to(message, f"Введи id объявления")
    bot.register_next_step_handler(msg, show_info_app)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'start_find':
        bot.send_message(call.message.chat.id,
                         f'Я начал искать объявления.\nпожалуйста наберитесь терпения и подождте.\n'
                         f'Я ищу медленно, чтобы авито не распознал во мне бота.\n'
                         f'Могу и быстро, но тогда меня заставляют вводить капчу:(')
        bot.send_message(call.message.chat.id,'🧐')
        start_find(call.from_user.id, call)
        bot.send_message(call.message.chat.id, 'Закончили!')

    elif call.data == 'check_ad':
        bot.send_message(call.message.chat.id, 'Проверяю я тоже медленно, по тем же причинам что и ищу:(')
        bot.send_message(call.message.chat.id, '🧐')
        Scrapping.check_ad(call.from_user.id,call)
        bot.send_message(call.message.chat.id, 'Закончили!')

    elif call.data == 'show_variants':
        show_variants(call.message)

    elif call.data == 'update_search_parameters':
        set_search(call.message)

    elif call.data == 'show_all_variants':
        show_all_variants(call.message)

    elif call.data == 'delete_all_variants':
        delete_all_variants(call.message)

    elif call.data == 'show_ad_info':
        show_ad_info(call.message)


@bot.message_handler(content_types=['text'])
def func(message):
    if (message.text == "Меню"):
        start_markup = telebot.types.InlineKeyboardMarkup()
        # Первый ряд (две кнопки)
        btn1 = telebot.types.InlineKeyboardButton('Провести поиск', callback_data='start_find')
        btn2 = telebot.types.InlineKeyboardButton('Проверить листинг', callback_data='check_ad')
        start_markup.row(btn1, btn2)
        # Второй ряд (две кнопки)
        btn3 = telebot.types.InlineKeyboardButton('Показать новое', callback_data='show_variants')
        btn4 = telebot.types.InlineKeyboardButton(f'Показать все', callback_data='show_all_variants')
        btn5 = telebot.types.InlineKeyboardButton(f'Показать описание', callback_data='show_ad_info')
        start_markup.row(btn3, btn4, btn5)
        btn6 = telebot.types.InlineKeyboardButton('Изменить поиск', callback_data='update_search_parameters')
        btn7 = telebot.types.InlineKeyboardButton('Удалить все', callback_data='delete_all_variants')
        start_markup.row(btn6, btn7)

        bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=start_markup)
    else:
        reply_parrot(message)


def reply_parrot(message):
    bot.send_message(message.chat.id, f'ты сказал:{message.text}')


def show_info_app(message):
    connection = sqlite3.connect('/homeproject/database/home1.db')
    try:
        id = int(message.text)
    except:
        id = 0
    cursor = connection.cursor()
    cursor.execute(
        f"SELECT description,full_description,url FROM apartment_sale_ads WHERE userid={message.chat.id} and id={id}")
    info = cursor.fetchone()
    if info != None:
        short_description = info[0]
        url = info[2]
        full_description = json.loads(info[1].replace("'", '"'))
        about = full_description["about_app"]
        about_app = 'О квартире:\n'
        for item in about:
            about_app = about_app + f"{item}:{about[item]}\n"
        descript = "Описание:\n" + full_description["descript"]
        about = full_description["about_home"]
        about_home = 'О доме:\n'
        for item in about:
            about_home = about_home + f"{item}:{about[item]}\n"
        bot.send_message(message.chat.id, f"{short_description}\n\n{descript}\n\n{about_app}\n{about_home}\n{url}")
    else:
        bot.send_message(message.chat.id, "объявления с таким id не найдено.")


def update_search_parameters(message):
    try:
        connection = sqlite3.connect('/homeproject/database/home1.db')
        cursor = connection.cursor()
        cursor.execute(f"UPDATE USERS_BOT set find_parameters='{message.text}' WHERE user_id={message.chat.id}")
        connection.commit()
        connection.close()
        bot.send_message(message.chat.id, 'Строка поиска изменена!')
    except Exception as e:
        bot.reply_to(message, 'oooops')


def show(message, shown):
    connection = sqlite3.connect('/homeproject/database/home1.db')
    cursor = connection.execute(
        f"SELECT url,price,id FROM apartment_sale_ads WHERE userid={message.chat.id} and "
        f"status='listed' and shown in ({','.join(str(i) for i in shown)})")
    urls = []
    for item in cursor:
        urls.append([item[0], item[1], item[2]])
    for item in urls:
        bot.send_message(
            message.chat.id,
            f"id:{item[2]}\n{item[0]} \nЦена:{item[1]}")
        connection.execute(f"UPDATE apartment_sale_ads set shown=1 where id='{item[2]}'")
        connection.commit()


def show_all_variants(message):
    show(message, [0, 1])


def delete_all_variants(message):
    connection = sqlite3.connect('/homeproject/database/home1.db')
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"DELETE FROM apartment_sale_ads where userid={message.chat.id}")
    except Error as e:
        print(e)
        pass
    connection.commit()
    connection.close()


def send_user_info(usinfo):
    connection = sqlite3.connect('/homeproject/database/home1.db')
    cursor = connection.cursor()
    default_search = f'https://www.avito.ru/sankt-peterburg_peterhof/kvartiry/prodam/1-komnatnye/' \
                     f'vtorichka-ASgBAQICAUSSA8YQAkDmBxSMUsoIFIBZ?f=ASgBAQECAkSSA8YQ6sEN_' \
                     f's45BEDmBxSMUsoIFIBZjt4OFAKQ3g4UAgFFxpoMF3siZnJvbSI6MCwidG8iOjUwMDAwMDB9'
    try:
        cursor.execute(
            f"INSERT INTO USERS_BOT (user_id, username, first_name, last_name, reg_date, find_parameters) "
            f"VALUES({usinfo[0]},'{usinfo[1]}','{usinfo[2]}','{usinfo[3]}','{usinfo[4]}','{default_search}')")
    except Error as e:
        print(e)
        pass
    connection.commit()
    connection.close()


def start_find(userid, call):
    connection = sqlite3.connect('/homeproject/database/home1.db')
    cursor = connection.execute(f"SELECT find_parameters FROM USERS_BOT WHERE user_id={userid}")
    url = cursor.fetchone()[0]
    Scrapping.start_find(url, userid, call)


def send_message(call, mess, mess_id=None):
    if mess_id is None:
        mess_id = bot.send_message(call.message.chat.id, mess).id

    else:
        bot.edit_message_text(mess, call.message.chat.id, mess_id)
    return mess_id


def create_table():
    with sqlite3.connect('/homeproject/database/home1.db') as connection:
        try:
            log = open('/homeproject/log.txt', 'a')
            log.write(f'{datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}: Создаем таблицу USERS_BOT\n')
            cursor = connection.cursor()
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS  USERS_BOT (user_id INTEGER NOT NULL PRIMARY KEY,username TEXT,"
                f"first_name TEXT,last_name TEXT,reg_date DATE,find_parameters TEXT)")
            log.write(f'{datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}:Создали таблицу USERS_BOT\n')
            log.write(f'------------------------------------------------------------\n')
            log.close()
        except Exception as err:
            log = open('/homeproject/log.txt', 'a')
            log.write(f'{datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}:{err}\n')
            log.write(f'------------------------------------------------------------\n')
            log.close()


if __name__ == '__main__':
    bot.infinity_polling()
