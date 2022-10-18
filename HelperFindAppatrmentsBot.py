#!/usr/bin/env python3
import sqlite3
from sqlite3 import Error
import telebot
import Scrapping
import time
import requests
import uuid
import os
from telebot import types

AGREGATOR = 'AVITO'
TOKEN = "5764053396:AAEBFx3nES5oZ0hm1ejtqomTa3LfHKr4Zu4"
bot = telebot.TeleBot(TOKEN)

with sqlite3.connect(f'{os.getcwd()}\home1.db') as connection:
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS  USERS_BOT (
    user_id INTEGER NOT NULL PRIMARY KEY, 
    username TEXT, 
    first_name TEXT, 
    last_name TEXT,
    reg_date DATE,
    find_parameters TEXT)
    ''')

# @bot.message_handler(commands=['button'])
# def button_message(message):


@bot.message_handler(commands=['start'])
def send_welcome(message):
    start_markup = telebot.types.InlineKeyboardMarkup()

    # первый ряд (две кнопки)
    btn1 = telebot.types.InlineKeyboardButton('Провести поиск', callback_data='start_find')
    btn2 = telebot.types.InlineKeyboardButton('Проверить листинг', callback_data='check_ad')
    start_markup.row(btn1, btn2)

    # второй ряд (одна кнопка)
    btn3 = telebot.types.InlineKeyboardButton('Показать варианты', callback_data='show_variants')
    btn4 = telebot.types.InlineKeyboardButton('Изменить поиск', callback_data='update_search_parameters')
    start_markup.row(btn3,btn4)

    # markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    # item1=types.KeyboardButton("Кнопка1")
    # item2=types.KeyboardButton("Кнопка2")
    # markup.add(item1)
    # markup.add(item2)

    usinfo = (message.from_user.id,
              message.from_user.username,
              message.from_user.first_name,
              message.from_user.last_name,
              time.ctime()
              )
    send_user_info(usinfo)
    bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=start_markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'start_find':
        bot.send_message(call.message.chat.id, 'Ищем...')
        start_find(call.from_user.id)
        bot.send_message(call.message.chat.id, 'Закончили!')

    elif call.data == 'check_ad':
        bot.send_message(call.message.chat.id, 'Проверяем...')
        Scrapping.check_ad(call.from_user.id)
        bot.send_message(call.message.chat.id, 'Закончили!')

    elif call.data == 'show_variants':
        show_variants(call.message)

    elif call.data == 'update_search_parameters':
        set_search(call.message)

def send_user_info(usinfo):
    connection = sqlite3.connect(f'{os.getcwd()}\home1.db')
    cursor = connection.cursor()
    default_search='https://www.avito.ru/sankt-peterburg_peterhof/kvartiry/prodam/1-komnatnye/vtorichka-ASgBAQICAUSSA8YQAkDmBxSMUsoIFIBZ?f=ASgBAQECAkSSA8YQ6sEN_s45BEDmBxSMUsoIFIBZjt4OFAKQ3g4UAgFFxpoMF3siZnJvbSI6MCwidG8iOjUwMDAwMDB9'
    try:
        cursor.execute(
            f"INSERT INTO USERS_BOT (user_id, username, first_name, last_name, reg_date, find_parameters) VALUES({usinfo[0]},'{usinfo[1]}','{usinfo[2]}','{usinfo[3]}','{usinfo[4]}','{default_search}')")
    except Error as e:
        print(e)
        pass
    connection.commit()
    connection.close()

def start_find(userid):
    connection = sqlite3.connect(f'{os.getcwd()}\home1.db')
    cursor=connection.execute(f"SELECT find_parameters FROM USERS_BOT WHERE user_id={userid}")
    url=cursor.fetchone()[0]
    Scrapping.start_find(url,userid)


@bot.message_handler(commands=['startfind'])
def startfindcommand(message):
    try:
        start_find(message.from_user.id)
        bot.send_message(message.chat.id,'Поиск закончен')
    except:
        bot.send_message(message.chat.id,'Поиск завершился неудачей')


@bot.message_handler(commands=['domofond'])
def set_agregator(message):
    global AGREGATOR
    AGREGATOR = message.text
    bot.send_message(
        message.chat.id,
        AGREGATOR
    )


@bot.message_handler(commands=['checkad'])
def checkad(message):
    Scrapping.check_ad(message.from_user.id)


@bot.message_handler(commands=['showme'])
def show_variants(message):
    connection = sqlite3.connect(f'{os.getcwd()}\home1.db')
    cursor=connection.execute(f"SELECT url,price FROM apartment_sale_ads WHERE userid={message.chat.id} and status='listed' and shown=0")
    urls=[]
    for item in cursor:
        urls.append([item[0],item[1]])
    for item in urls:
        bot.send_message(
            message.chat.id,
            f"{item[0]} \nЦена:{item[1]}")
        connection.execute(f"UPDATE apartment_sale_ads set shown=1 where url='{item[0]}'")
        connection.commit()

@bot.message_handler(commands=['setsearch'])
def set_search(message):
    msg = bot.reply_to(message,f"Хочешь сменить строку поиска?\nхорошо. тогда подготовь её самостоятельно\n"
                               f"открой avito и заполни фильтры недвижимости и скопируй получившуюся итоговую строку и отправь следующим сообщением.")
    bot.register_next_step_handler(msg, update_search_parameters)

def update_search_parameters(message):
        try:
            connection = sqlite3.connect(f'{os.getcwd()}\home1.db')
            cursor = connection.cursor()
            cursor.execute(f"UPDATE USERS_BOT set find_parameters='{message.text}' WHERE user_id={message.chat.id}")
            connection.commit()
            connection.close()
            bot.send_message(message.chat.id,'Строка поиска изменена!')
        except Exception as e:
            bot.reply_to(message, 'oooops')


# @bot.message_handler()
# def set_search(message):
#     if message.text.find('/setsearch:') != -1:
#         search=message.text[message.text.find(':') + 1:]
#         connection = sqlite3.connect(f'{os.getcwd()}\home1.db')
#         cursor = connection.cursor()
#         cursor.execute(f"UPDATE USERS_BOT set find_parameters='{search}' WHERE user_id={message.from_user.id}")
#         connection.commit()
#         connection.close()
#         bot.send_message(
#             message.chat.id,
#             'строка поиска изменена.'
#         )




if __name__ == '__main__':

    bot.infinity_polling()



















