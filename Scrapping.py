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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import os


def get_connection():
    connection = sqlite3.connect(f'{os.getcwd()}\home1.db')
    return connection


def create_db():
    connection = sqlite3.connect(f'{os.getcwd()}\home1.db')
    cursor = connection.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS apartment_sale_ads "
                   f"(id integer, "
                   f"description TEXT, "
                   f"url TEXT, "
                   f"full_description TEXT, "
                   f"interfloor TEXT, "
                   f"notes TEXT,"
                   f"userid INTEGER,"
                   f"status TEXT,"
                   f"shown INTEGER,"
                   f"price INTEGER)")


def get_full_description(url):
    capa = DesiredCapabilities.EDGE
    capa["pageLoadStrategy"] = "none"
    options = Options()
    options.headless = False
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-certificate-errors')
    service = Service("C:\\Users\\Мура\\PycharmProjects\\homeproject\\msedgedriver.exe")
    driver = webdriver.Edge(options=options, service=service, capabilities=capa)
    wait = WebDriverWait(driver, 30)
    # driver.implicitly_wait(10)
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'style-item-params-list-item-aXXql')))
    driver.execute_script("window.stop();")
    full_about = {}
    all_params = {}
    all_home_params = {}

    about_app = driver.find_elements(By.CLASS_NAME, 'params-paramsList__item-appQw')
    try:
        for i in about_app:
            item = i.text.split(':')
            all_params.update({item[0].replace('"', "").replace("'", ""): item[1].replace('"', "").replace("'", "").replace('"', "").replace("'", "")})
            full_about.update({'about_app': all_params})
    except Exception as error:
        full_about.update({'about_app': f"что то пошло не так. ошибка:{error}, url:{url}"})
    try:
        full_about.update({'descript': driver.find_elements(By.CLASS_NAME, 'style-item-description-text-mc3G6')[0].text.replace('"', "").replace("'", "")})
    except:
        try:
            full_about.update({'descript': driver.find_elements(By.CLASS_NAME, 'style-item-description-html-qCwUL')[0].text.replace('"', "").replace("'", "")})
        except Exception as error:
            full_about.update({'descript': f"что то пошло не так. ошибка:{error}, url:{url}"})

    about_home = driver.find_elements(By.CLASS_NAME, 'style-item-params-list-item-aXXql')
    try:
        for i in about_home:
            item = i.text.split(':')
            all_home_params.update({item[0].replace('"', "").replace("'", ""): item[1].replace('"', "").replace("'", "")})
            full_about.update({'about_home': all_home_params})
    except Exception as error:
        full_about.update({'about_home': f"что то пошло не так. ошибка:{error}, url:{url}"})
    try:
        price=int(driver.find_elements(By.CLASS_NAME,'style-price-value-main-TIg6u')[1].text.replace(' ', "").split("\n")[0])
    except Exception as error:
        price=0
    time.sleep(randint(2, 5))
    driver.quit()
    return full_about, price

def check_ad(userid):
    conn = get_connection()
    cursor = conn.execute(f"SELECT url from apartment_sale_ads where userid={userid} and status='listed'")
    listed_ad=[]
    for item in cursor:
        listed_ad.append(item[0])
    options = Options()
    options.headless = False
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-certificate-errors')
    service = Service("C:\\Users\\Мура\\PycharmProjects\\homeproject\\msedgedriver.exe")
    capa = DesiredCapabilities.EDGE
    capa["pageLoadStrategy"] = "none"
    driver = webdriver.Edge(options=options, service=service, capabilities=capa)
    # driver.implicitly_wait(10)
    for url in listed_ad:
        wait = WebDriverWait(driver, 30)
        try:
            driver.get(url)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'style-item-view-PCYlM')))
            driver.execute_script("window.stop();")
            time.sleep(randint(10, 20))
            if driver.find_elements(By.CLASS_NAME,'closed-warning-content-_f4_B'):
                conn.execute(f"UPDATE apartment_sale_ads set status='delisted' where url='{url}'")
                conn.commit()
                print(f"url delisted: {url}")
            else:
                print(f"url listed: {url}")

        except Exception as e:
            conn.execute(f"UPDATE apartment_sale_ads set status='fail' where url='{url}'")
            print(f"url fail: {url}")
    driver.close()

def start_edje(url,ids,userid):
    cursor = get_connection().cursor()
    # check_ad(userid)
    options = Options()
    options.headless = False
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-certificate-errors')
    service = Service("C:\\Users\\Мура\\PycharmProjects\\homeproject\\msedgedriver.exe")
    capa = DesiredCapabilities.EDGE
    capa["pageLoadStrategy"] = "none"
    driver = webdriver.Edge(options=options, service=service, capabilities=capa)
    wait = WebDriverWait(driver, 30)
    # driver.implicitly_wait(10)
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'items-items-kAJAg')))
    driver.execute_script("window.stop();")
    time.sleep(2)
    blocks = driver.find_elements(By.CLASS_NAME, 'items-items-kAJAg')
    block=blocks[0]
    suggestions = block.find_elements(By.CLASS_NAME, 'iva-item-root-_lk9K')
    for element in suggestions:
        try:
            url_home = element.find_element(By.TAG_NAME, 'a').get_property('href')
            id = url_home[url_home.rfind('_') + 1:]
            if int(id) not in ids:
                small_desc = element.text.replace('"', "").replace("'", "")
                full_description, price = get_full_description(url_home)
                cursor.execute(f'INSERT INTO apartment_sale_ads ('
                               f'id,'
                               f'description,'
                               f'url,'
                               f'full_description,'
                               f'interfloor,'
                               f'notes,'
                               f'userid, '
                               f'status,'
                               f'shown,'
                               f'price) '
                               f'VALUES('
                               f'"{id}",'
                               f'"{small_desc}",'
                               f'"{url_home}",'
                               f'"{full_description}",'
                               f'"перекрытие",'
                               f'"заметки",'
                               f'"{userid}",'
                               f'"listed",'
                               f'0,'
                               f'"{price}")')
                time.sleep(randint(15, 60))
                cursor.connection.commit()
                print('commit')
        except Exception as er:
            print(er)
            pass
    cursor.connection.commit()
    time.sleep(1)
    driver.quit()


# test_url=['https://www.avito.ru/','https://spb.cian.ru/','https://www.domofond.ru/','https://domclick.ru/']

def start_find(url,userid):
    create_db()
    conn = get_connection()
    cursor = conn.execute('SELECT id from apartment_sale_ads')
    ids = []
    for i in cursor:
        ids.append(i[0])
    # avito = 'https://www.avito.ru/sankt-peterburg_peterhof/kvartiry/prodam/1-komnatnye/vtorichka-ASgBAQICAkSSA8YQ5geMUgFAyggUgFk?f=ASgBAQECA0SSA8YQ5geMUsDBDbr9NwFAyggUgFkCRYQJFXsiZnJvbSI6MzUsInRvIjpudWxsfcaaDBd7ImZyb20iOjAsInRvIjo1NTAwMDAwfQ'
    start_edje(url,ids,userid)

def test_message():
    return 'testmessage'