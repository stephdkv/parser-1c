import pickle

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By



from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


option = webdriver.FirefoxOptions()
option.set_preference('dom.webdriver.enable', False)
option.set_preference('webnotifications.enable', False)
option.set_preference('general.useragent.override', 'firefox142134')

driver = webdriver.Firefox(options=option)

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
    driver.get(f'https://magsbt.com/{data_href}')
    items = driver.find_elements(By.CLASS_NAME, 'table-view__item')
    button_enabled = False

# Пока кнопка не будет доступна для нажатия, продолжаем ожидание
    while not button_enabled:
        try:
        # Ждем, пока кнопка не станет видимой
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'more_text_ajax'))
            ).click()
        # Если кнопка кликабельна (т.е. не выбросится исключение), устанавливаем флаг в True
            button_enabled = True
        except:
        # Если кнопка не кликабельна, продолжаем ожидание
            pass
    items_list = []
    for item in items :
        item_title = WebDriverWait(item, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.item-title > a.dark_link.js-notice-block__title > span')
            )).text
        print(item_title)
        
    print('Конец категории')
    driver.close()
    driver.switch_to.window(tabs[0]) 
# Спарсить количесвто страниц для категории
# Пройтись по страницам https://magsbt.com/catalog/zapchasti-dlya-stiralnykh-mashin/?PAGEN_1=54
