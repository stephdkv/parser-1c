import pickle
import time 
import xml.etree.ElementTree as ET
import re
import filecmp
import shutil

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


option = webdriver.FirefoxOptions()
option.set_preference('dom.webdriver.enable', False)
option.set_preference('webnotifications.enable', False)
option.set_preference('general.useragent.override', 'firefox142134')
driver = webdriver.Firefox(options=option)
driver.minimize_window()

while True:
    start_time = time.time()
    # Создаем корневой элемент
    root = ET.Element("items")
    driver.get('https://magsbt.com/')
    for cookie in pickle.load(open('session', 'rb')):
        driver.add_cookie(cookie)
    driver.refresh()
    categories = driver.find_elements(By.CLASS_NAME, 'main-link')
    categories_list = []
    for category in categories:
        driver.implicitly_wait(10) 
        data_href = category.get_attribute('data-href')
        driver.execute_script("window.open();")
        tabs = driver.window_handles
        driver.switch_to.window(tabs[1])
        driver.get(f'https://magsbt.com/{data_href}filter/imyie_stores4filter-is-75fd9124-d772-11e2-ae74-d48564610fb7/apply/')
        
        # Проверяем наличие элемента '(//*[@class="dark_link"])[last()]'
        try:
            last_element = driver.find_element(By.XPATH, '(//*[@class="dark_link"])[last()]').text
        except NoSuchElementException:
            # Если элемент не найден, начинаем обработку элементов items
            items = driver.find_elements(By.CLASS_NAME, 'table-view__item')
            for item in items :
                item_title = WebDriverWait(item, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.item-title > a.dark_link.js-notice-block__title > span')
                    )).text
                item_available = WebDriverWait(item, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.item-stock .value span span')
                    )).text
                
                item_code = WebDriverWait(item, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, 'article_block')
                    )).text
                # Разделить строку по символу "|"
                if item_available and re.search(r'\b\d+\b', item_available):
                    item_quantity = re.search(r'\b\d+\b', item_available).group()
                split_by_pipe = item_code.split(" | ")
                code = None
                art = None
                for part in split_by_pipe:
                    if "Код" in part:
                        code = part.split(": ")[1]
                    elif "Арт" in part:
                        art = part.split(": ")[1]
                if code is not None:
                    item_element = ET.SubElement(root, "item")
                    tovar_element = ET.SubElement(item_element, 'Товар')
                    title_element = ET.SubElement(tovar_element, "Имя")
                    title_element.text = item_title
                    available_element = ET.SubElement(item_element, "Колличество") 
                    available_element.text = item_quantity
                    code_element = ET.SubElement(tovar_element, "Код")
                    code_element.text = code
                    if art is not None:
                        art_element = ET.SubElement(tovar_element, "Арт.")
                        art_element.text = art
                    
                
            # Закрываем вкладку и переключаемся на основную страницу
            driver.close()
            driver.switch_to.window(tabs[0])
            continue  # Продолжаем цикл, чтобы перейти к следующей категории
        
        # Если элемент найден, продолжаем выполнение кода
        items_list = []
        for i in range(1, int(last_element)+1):
            driver.get(f'https://magsbt.com/{data_href}filter/imyie_stores4filter-is-75fd9124-d772-11e2-ae74-d48564610fb7/apply/?PAGEN_1={i}')
            items = driver.find_elements(By.CLASS_NAME, 'table-view__item')
            for item in items :
                item_title = WebDriverWait(item, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.item-title > a.dark_link.js-notice-block__title > span')
                    )).text
                item_available = WebDriverWait(item, 10).until(
                    EC.visibility_of_element_located((By.XPATH,  ".//span[contains(@style, '#5fa800') and contains(text(), 'Екатеринбурге')]")
                    )).text
                
                item_code = WebDriverWait(item, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, 'article_block')
                    )).text
                if item_available and re.search(r'\b\d+\b', item_available):
                    item_quantity = re.search(r'\b\d+\b', item_available).group()
                # Разделить строку по символу "|"
                split_by_pipe = item_code.split(" | ")
                code = None
                art = None
                for part in split_by_pipe:
                    if "Код" in part:
                        code = part.split(": ")[1]
                    elif "Арт" in part:
                        art = part.split(": ")[1]
                if code is not None:
                    item_element = ET.SubElement(root, "item")
                    tovar_element = ET.SubElement(item_element, 'Товар')
                    title_element = ET.SubElement(tovar_element, "Имя")
                    title_element.text = item_title
                    available_element = ET.SubElement(item_element, "Колличество") 
                    available_element.text = item_quantity
                    code_element = ET.SubElement(tovar_element, "Код")
                    code_element.text = code
                    if art is not None:
                        art_element = ET.SubElement(tovar_element, "Арт.")
                        art_element.text = art
        
        tree = ET.ElementTree(root)
        tree.write(f"items_current.xml", encoding="utf-8", xml_declaration=True)

        
        
        
        driver.close()
        driver.switch_to.window(tabs[0])
    # Проверяем идентичность файлов
    if not filecmp.cmp('items_current.xml', 'items_old.xml'):
            # Если файлы не идентичны, дублируем текущий файл в items_old.xml
        shutil.copy('items_current.xml', 'items_old.xml')
        shutil.copy('items_current.xml', 'items_new.xml') 

    end_time = time.time()  # Засекаем время окончания выполнения скрипта
    execution_time = end_time - start_time  # Вычисляем время выполнения
    print("Время выполнения скрипта:", execution_time, "секунд")
