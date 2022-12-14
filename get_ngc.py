import re
import json
import cloudscraper
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_argument("--enable-javascript")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--window-size=1920x1080')
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--nogpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--enable-javascript")
chrome_options.add_experimental_option(
    "excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

category_file_name = "coin_category_links.json"
coin_page_file_name = "coin_page_links.json"

path = '/usr/local/bin/chromedriver'

driver = webdriver.Chrome(service=Service(path), options=chrome_options)


def get_element_links(element, array):
    for anchor in element.find_elements(By.TAG_NAME, 'a'):
        try:
            link = anchor.get_attribute('href')
            array.append(link)
        except:
            pass


def open_file(filename):
    file_object = open(filename, "r")
    json_content = file_object.read()
    return json.loads(json_content)


def write_new_file(array, filename):
    file_to_erase = open(filename, 'r+')
    file_to_erase.truncate(0)
    data_json = json.dumps(array)
    new_file = open(filename, "w")
    new_file.write(data_json)
    new_file.close()


def close_modal(driver):
    try:
        modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'email-signup')))

        close_icon = modal.find_element(By.CLASS_NAME, "modal-dialog-close")
        close_icon.click()
    except:
        print('unable to find close icon')
        pass


def scrape_coin_data():
    coin_data = []
    coin_page_links = open_file(coin_page_file_name)
    counter = 0
    LIMIT = 1000
    for coin_page_link in coin_page_links:
        driver.get(coin_page_link)
        close_modal(driver)
        coin_data_object = {
            "price": {},
            "pop": {}
        }
        barcode = coin_page_link.split('/')[7]
        coin_data_object['barcode'] = barcode

        def get_coin_info(soup):
            try:
                data_list = soup.find('ul', {'class': 'ce-coin__specs-list'})
                list_elements = data_list.find_all('li')
                for list_element in list_elements:
                    raw_list_string = list_element.text
                    data = re.sub(r'\n', "", raw_list_string).split(":")
                    key = data[0]
                    value = data[1]
                    coin_data_object[key] = value
            except:
                pass
        try:
            html = driver.page_source

            soup = BeautifulSoup(html, "html.parser")

            raw_coin_description = soup.select_one(
                'body > div.ccg-canvas > div.ccg-body > div.inner-main > div > div > div.ce-coin__topbar.ng-scope > div > div:nth-child(3) > div.ce-coin__title > h1').text
            description = re.sub(r'\s+', " ", raw_coin_description).strip()

            # GET PRODUCT DESCRIPTION
            coin_data_object['Description'] = description
            get_coin_info(soup)
            grade_scroller_table = soup.find(
                'div', {'id': 'gradeScroller'})
            data_rows = grade_scroller_table.find_all('tr')
            grades = []
            grade_row = data_rows[0]
            for grade in grade_row.find_all('th'):
                grades.append(grade.text)
            price_row = data_rows[1]
            price_index = 0
            for price in price_row.find_all('td'):
                price_grade = grades[price_index]
                raw_price = price.text
                formatted_price = re.sub(r'\s+', '', raw_price)
                coin_data_object['price'][price_grade] = formatted_price
                price_index += 1
            pop_index = 0
            pop_row = data_rows[2]
            for pop in pop_row.find_all('td'):
                pop_grade = grades[pop_index]
                coin_data_object['pop'][pop_grade] = pop.text
                pop_index += 1
            # loop through table row
            # set the index of the header as the key
            coin_data.append(coin_data_object)
            counter += 1
            if counter == LIMIT:
                write_new_file(coin_data, "coin_data.json")
                counter = 0
        except:
            pass
    driver.close()
    write_new_file(coin_data, "coin_data.json")


def get_coin_category_links():
    base_url = 'https://www.ngccoin.com/coin-explorer'

    driver.get(base_url)

    close_modal(driver)

    outer_category_class = 'ccg-card-grid__item'

    coin_grid_container = driver.find_element(
        By.CLASS_NAME, 'ccg-card-grid__inner')

    outer_categories = coin_grid_container.find_elements(
        By.CLASS_NAME, outer_category_class)

    category_page_links = []
    cat_index = 1
    for outer_category in outer_categories:
        outer_category.click()
        get_element_links(outer_category, category_page_links)
        close_xpath = f'/html/body/div[2]/div[2]/div/div[1]/div/div/div[3]/div[2]/div[{cat_index}]/div/div[2]/div/div/div[2]/div[1]'

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, close_xpath)))
            outer_category.find_element(
                By.XPATH, close_xpath).click()
            driver.implicitly_wait(5)
            cat_index += 1
        except:
            break

    driver.close()

    write_new_file(category_page_links, category_file_name)


def get_coin_page_links():
    driver = webdriver.Chrome(service=Service(path), options=chrome_options)
    # load category links
    coin_page_links = []
    coin_categories = open_file(category_file_name)
    for category_link in coin_categories:
        # go to page
        driver.get(category_link)
        # find div.ce-tab-contents
        try:
            close_modal(driver)
            tab = driver.find_element(By.CLASS_NAME, 'ce-tab-contents')
            # get all element links
            get_element_links(tab, coin_page_links)
            driver.implicitly_wait(5)
        except:
            pass
    driver.close()
    write_new_file(coin_page_links, coin_page_file_name)
    scrape_coin_data()


scrape_coin_data()
