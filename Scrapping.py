import requests
import time
from random import randint
from selenium.webdriver.common.by import By
import selenium.webdriver.edge
import selenium.webdriver.chrome
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
import sqlite3
import os


def get_connection():
    connection = sqlite3.connect(f'{os.getcwd()}\home1.db')
    return connection


def create_db():
    connection = sqlite3.connect(f'{os.getcwd()}\home1.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS apartment_sale_ads
                  (id integer, description TEXT, url TEXT, full_description TEXT, interfloor TEXT, notes TEXT)''')


def get_full_description(url):
    options = Options()
    options.headless = False
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-certificate-errors')
    service = Service("C:\\Users\\Leventsov.AV\\PycharmProjects\\homeproject\\msedgedriver.exe")
    driver = webdriver.Edge(options=options, service=service)
    driver.get(url)
    full_about = {}
    all_params = {}
    all_home_params = {}

    about_app = driver.find_elements(By.CLASS_NAME, 'params-paramsList__item-appQw')
    try:
        for i in about_app:
            item = i.text.split(':')
            all_params.update({item[0].replace('"', ""): item[1].replace('"', "")})
            full_about.update({'about_app': all_params})
    except Exception as error:
        full_about.update({'about_app': f"что то пошло не так. ошибка:{error}, url:{url}"})
    try:
        full_about.update(
            {'descript': driver.find_elements(By.CLASS_NAME, 'style-item-description-text-mc3G6')[0].text.replace('"',
                                                                                                                  "")})
    except:
        try:
            full_about.update({'descript': driver.find_elements(By.CLASS_NAME, 'style-item-description-html-qCwUL')[
                0].text.replace('"', "").replace('"', "")})
        except Exception as error:
            full_about.update({'descript': f"что то пошло не так. ошибка:{error}, url:{url}"})

    about_home = driver.find_elements(By.CLASS_NAME, 'style-item-params-list-item-aXXql')
    try:
        for i in about_home:
            item = i.text.split(':')
            all_home_params.update({item[0].replace('"', ""): item[1].replace('"', "")})
            full_about.update({'about_home': all_home_params})
    except Exception as error:
        full_about.update({'about_home': f"что то пошло не так. ошибка:{error}, url:{url}"})
    time.sleep(randint(2, 5))
    driver.quit()
    return full_about


def start_edje(url,ids):
    cursor = get_connection().cursor()
    options = Options()
    options.headless = False
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-certificate-errors')
    service = Service("C:\\Users\\Leventsov.AV\\PycharmProjects\\homeproject\\msedgedriver.exe")
    driver = webdriver.Edge(options=options, service=service)
    driver.get(url)
    time.sleep(2)
    blocks = driver.find_elements(By.CLASS_NAME, 'items-items-kAJAg')
    for block in blocks:
        suggestions = block.find_elements(By.CLASS_NAME, 'iva-item-root-_lk9K')
        for element in suggestions:
            try:
                url_home = element.find_element(By.TAG_NAME, 'a').get_property('href')
                id = url_home[url_home.rfind('_') + 1:]
                if int(id) not in ids:
                    small_desc = element.text
                    full_description = get_full_description(url_home)
                    print('stop')
                    cursor.execute(f'INSERT INTO apartment_sale_ads ('
                                   f'id,'
                                   f'description,'
                                   f'url,'
                                   f'full_description,'
                                   f'interfloor,'
                                   f'notes) '
                                   f'VALUES('
                                   f'"{id}",'
                                   f'"{small_desc}",'
                                   f'"{url_home}",'
                                   f'"{full_description}",'
                                   f'"перекрытие",'
                                   f'"заметки")')
                    time.sleep(randint(15, 60))
                    cursor.connection.commit()
            except Exception as er:
                print(er)
                pass
    cursor.connection.commit()
    time.sleep(1)
    driver.quit()


# test_url=['https://www.avito.ru/','https://spb.cian.ru/','https://www.domofond.ru/','https://domclick.ru/']

create_db()
conn = get_connection()
cursor = conn.execute('SELECT id from apartment_sale_ads')
ids = []
for i in cursor:
    ids.append(i[0])

avito = 'https://www.avito.ru/sankt-peterburg_peterhof/kvartiry/prodam/1-komnatnye/vtorichka-ASgBAQICAkSSA8YQ5geMUgFAyggUgFk?f=ASgBAQECA0SSA8YQ5geMUsDBDbr9NwFAyggUgFkCRYQJFXsiZnJvbSI6MzUsInRvIjpudWxsfcaaDBd7ImZyb20iOjAsInRvIjo1NTAwMDAwfQ'
start_edje(avito,ids)

print('finish')
