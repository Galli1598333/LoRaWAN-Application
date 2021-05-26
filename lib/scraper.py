from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import json
import csv


def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent + 1)
        else:
            print('\t' * (indent + 1) + str(value))


def make_dict(csvFilePath):
    # create a dictionary
    data = {}
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf, delimiter=';')
        for rows in csvReader:
            key = rows['GatewayMAC'].replace(':', '')
            data[key] = rows
    return data


class UniOrchestraScraper:
    def __init__(self, webdriver_fpath, user, pwd):
        self.driver = webdriver.Chrome(webdriver_fpath)
        self.user = user
        self.pwd = pwd
        self.message_list = []

    def scrape(self, device_id, start_date, end_date):
        driver = self.driver
        driver.get('https://uniorchestra.uniot.eu/login')

        players = driver.find_elements_by_xpath('//*[@id="wrapper"]/div/div[2]/p[1]')
        for p in range(len(players)):
            print(players[p].text)

        username = driver.find_element_by_name("username")
        password = driver.find_element_by_name("password")

        username.send_keys(self.user)
        password.send_keys(self.pwd)

        driver.find_elements_by_xpath('//*[@id="wrapper"]/div/div[2]/form/div[4]/div[2]/button')[0].click()
        time.sleep(5)
        driver.get('https://uniorchestra.uniot.eu/lora/device/'+device_id+'/pacchetti')
        print('loading')
        time.sleep(5)
        home = driver.find_elements_by_class_name('logo-lg')[0]
        start_dates = driver.find_elements_by_xpath(
            '//*[@id="content"]/ui-view/div/div[2]/tabs/div/ui-view/div/div/div/div[1]/div/div[1]/input')
        start_dates[0].send_keys(start_date)  # "20/12/2020"
        end_dates = driver.find_elements_by_xpath(
            '//*[@id="content"]/ui-view/div/div[2]/tabs/div/ui-view/div/div/div/div[1]/div/div[2]/input')
        end_dates[0].send_keys(end_date)  # "20/12/2020"
        driver.find_elements_by_xpath('//*[@id="my-chat-box"]/div[1]/div/button[4]')[0].click()
        time.sleep(15)
        pages = int(driver.find_elements_by_xpath('//*[@id="loggrid"]/div[2]/div[1]/div[1]/span')[0].text[2:])
        print("pages")
        print(pages)

        message_list = self.message_list
        for page in range(pages):
            print("visualizza")
            visualizza = driver.find_elements_by_class_name('ui-grid-coluiGrid-000F')
            gateways_deduplication = {}
            last_id = -1
            print(len(visualizza))
            """
            print(len(steps))
        
            print("last step: " + steps[len(steps)-1].text)
            for p in range(len(gateways)):
                if p > 0:
                    if gateways[p].text[0] == '(':
                        last_key = gateways[p].text[4:]
                        last_id += 1
                        gateways_deduplication[last_id] = {'ded': last_key, 'pre': []}
        
                    elif steps[p].text == 'pre_deduplication':
                        gateways_deduplication[last_id]['pre'].append(gateways[p].text)
            print(gateways_deduplication)
            """

            for p in range(len(visualizza)):
                if p > 0:
                    # print(p)
                    visualizza[p].click()
                    time.sleep(1)
                    json_pre = driver.find_elements_by_class_name('json')
                    time.sleep(1)
                    result = json.loads(json_pre[0].text)
                    # pretty(result)
                    message_list.append(result)
                    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(5)
                print("////////////////////////////")
            driver.find_elements_by_xpath('//*[@id="loggrid"]/div[2]/div[1]/div[1]/button[3]')[0].click()
            time.sleep(10)
        driver.close()
        return message_list

    def export_to_json(self, output_fpath):
        with open(output_fpath, 'w', encoding='utf-8') as f:
            json.dump(self.message_list, f, ensure_ascii=False, indent=4)

    def clear(self):
        self.message_list = []
