#!/usr/bin/env python3
import sqlite3
from sqlite3 import Error
import telebot
import Scrapping
import time
import requests
import uuid
import os

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


@bot.message_handler(commands=['start'])
def send_welcome(message):
    usinfo = (message.from_user.id,
              message.from_user.username,
              message.from_user.first_name,
              message.from_user.last_name,
              time.ctime()
              )
    send_user_info(usinfo)
    bot.send_message(
        message.chat.id,
        'test start message'
    )


def send_user_info(usinfo):
    connection = sqlite3.connect(f'{os.getcwd()}\home1.db')
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO USERS_BOT (user_id, username, first_name, last_name, reg_date, find_parameters) VALUES(?,?,?,?,?,'pass')",
            usinfo)
    except Error as e:
        print(e)
        pass
    connection.commit()
    connection.close()


@bot.message_handler(commands=['startfind'])
def send_test(message):
    connection = sqlite3.connect(f'{os.getcwd()}\home1.db')
    cursor=connection.execute(f"SELECT find_parameters FROM USERS_BOT WHERE user_id={message.from_user.id}")
    urls=[]
    for item in cursor:
        urls.append(item[0])

    url=urls[0]
    bot.send_message(
        message.chat.id,
        Scrapping.start_find(url,message.from_user.id)
    )


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
def sow_variants(message):
    connection = sqlite3.connect(f'{os.getcwd()}\home1.db')
    cursor=connection.execute(f"SELECT url FROM apartment_sale_ads WHERE userid={message.from_user.id} and status='listed' and shown=0")
    urls=[]
    for item in cursor:
        urls.append(item[0])
    for item in urls:
        bot.send_message(
            message.chat.id,
            item)
        connection.execute(f"UPDATE apartment_sale_ads set shown=1 where url='{item}'")
        connection.commit()

@bot.message_handler()
def set_search(message):
    if message.text.find('/setsearch:') != -1:
        search=message.text[message.text.find(':') + 1:]
        connection = sqlite3.connect(f'{os.getcwd()}\home1.db')
        cursor = connection.cursor()
        cursor.execute(f"UPDATE USERS_BOT set find_parameters='{search}' WHERE user_id={message.from_user.id}")
        connection.commit()
        connection.close()
        bot.send_message(
            message.chat.id,
            'строка поиска изменена.'
        )


bot.infinity_polling()
