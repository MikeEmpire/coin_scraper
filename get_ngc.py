
from bs4 import BeautifulSoup
import json
import undetected_chromedriver as uc


f = open('coin_category_links.json')
coin_category_links = json.load(f)

file = open('coin_type_links.json')
coin_type_links = json.load(file)

uc_opts = uc.ChromeOptions()
driver = uc.Chrome(use_subprocess=True, options=uc_opts)
base_url = 'https://www.ngccoin.com/coin-explorer'
# CHOOSE_A_COIN = "Choose a Coin Type:"
# initial_url = 'https://www.ngccoin.com/coin-explorer/coinfacts'
# driver.get(initial_url)
driver.get(base_url)
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
box_class = 'ccg-card-grid__item ng-scope'
selected_class = 'ccg-card-grid__item ng-scope ccg-resource-card--selected'
card_boxes = soup.find_all('div', {"class": box_class})
for box in card_boxes:
    box.click

# coin_page_links = []
# coin_category_page_links = []


def get_element_links(element, array):
    for link in element.find_all('a', href=True):
        coin_page_link = link.get('href')
        link_to_add = f'{base_url}{coin_page_link}'
        array.append(link_to_add)


# for box in category_boxes:
#     for list_element in box.find_all('li'):
#         get_element_links(list_element, category_page_links)


# go through each page link,
# for page_link in coin_category_links:
#     driver.get(page_link)
#     cat_html = driver.page_source
#     cat_page_soup = BeautifulSoup(cat_html, 'html.parser')
#     tall_text_class = 'container-fluid padding-bottom text-tall-lh'
#     is_pre_page = cat_page_soup.find('div', {"class": tall_text_class})
#     new_links = new_links.remove(page_link)
#     if is_pre_page is None:
#         row_class = 'row cf-cat-list padding-top text-center vertical-top'
#         coin_type_div = cat_page_soup.find('div', {"class": row_class})
#         get_element_links(coin_type_div, coin_type_links)


# check if page has text: "Select a coin" OR "choose a type"
# 	loop through tabs, get all coin links


driver.close()

# file_to_erase = open('coin_page_links.json', 'r+')
# file_to_erase.truncate(0)
# page_json = json.dumps(new_links)
# new_file = open("coin_page_links.json", "w")
# new_file.write(page_json)
# new_file.close()

