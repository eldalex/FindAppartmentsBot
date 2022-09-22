import requests
import time
from selenium.webdriver.common.by import By
import selenium.webdriver.edge
import selenium.webdriver.chrome
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service


def start_edje(url):
    options = Options()
    options.headless = False
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-certificate-errors')
    service = Service("C:\\Users\\Leventsov.AV\\PycharmProjects\\homeproject\\msedgedriver.exe")
    driver = webdriver.Edge(options=options, service=service)
    driver.get(url)
    time.sleep(2)
    blocks = driver.find_elements(By.CLASS_NAME, 'items-items-kAJAg')
    block0 = blocks[0]
    div = block0.find_elements(By.TAG_NAME, 'div')
    for i in range(0, len(div)):
        element = div[i]
        attrs = driver.execute_script(
            'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;',
            element)
        try:
            if attrs['class']:
                if attrs[
                    'class'] == 'iva-item-root-_lk9K photo-slider-slider-S15A_ iva-item-list-rfgcH iva-item-redesign-rop6P iva-item-responsive-_lbhG items-item-My3ih items-listItem-Gd1jN js-catalog-item-enum':
                    print('---------------------------------')
                    print(element.text)
                    hrefs = element.find_elements(By.CLASS_NAME, 'iva-item-titleStep-pdebR')
                    for item in hrefs:
                        print(item.find_element(By.TAG_NAME, 'a').get_property('href'))
                    # print(attrs)
                    print('---------------------------------')
        except:
            pass
    time.sleep(1)
    driver.quit()


# test_url=['https://www.avito.ru/','https://spb.cian.ru/','https://www.domofond.ru/','https://domclick.ru/']
avito = 'https://www.avito.ru/sankt-peterburg_peterhof/kvartiry/prodam/1-komnatnye/vtorichka-ASgBAQICAkSSA8YQ5geMUgFAyggUgFk?f=ASgBAQECA0SSA8YQ5geMUsDBDbr9NwFAyggUgFkCRYQJFXsiZnJvbSI6MzUsInRvIjpudWxsfcaaDBd7ImZyb20iOjAsInRvIjo1NTAwMDAwfQ'
start_edje(avito)

print('finish')
