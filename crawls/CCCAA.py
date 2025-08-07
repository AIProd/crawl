import pandas as pd
from openpyxl import load_workbook
from bs4 import BeautifulSoup
import openpyxl
from urllib.parse import urljoin
import spacy
import sys
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dataclasses import dataclass,astuple,asdict

import os
from dotenv import load_dotenv

load_dotenv()

CHROME_DRIVER = os.getenv('CHROME_DRIVER')
CHROME_BINARY = os.getenv('CHROME_BINARY')

chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.binary_location=CHROME_BINARY

service = Service(CHROME_DRIVER)
driver = webdriver.Chrome(service=service,options=chrome_options)



def get_url_content(url,CLASS_NAME=None):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        if CLASS_NAME:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, CLASS_NAME)))
        else:
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "table")))

        html_content = driver.page_source
    except:
        # if the driver doesn't work
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        page = requests.get(url, headers=headers)
        html_content = page.text
    soup = BeautifulSoup(html_content, "html.parser")
    return soup


@dataclass
class Member:
    member: str
    city: str
    nickname: str
    conference: str

def export_to_excel(data,name):
    try:
        wb_staff = openpyxl.load_workbook("%s.xlsx"%name)
        ws_staff_sh = wb_staff.active
        for member in data:
            ws_staff_sh.append(astuple(member))
        wb_staff.save("%s.xlsx"%name)
    except Exception as e:
        print(str(e))

def check_url(url):
    if url.find('https://') > 1:
        url=url.replace("http://", '')
    import re
    url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
    if re.match(url_pattern, url):
        if 'null' not in url:
            return url
    return ''

def crawl_CCCAA():

    list_html=get_url_content("https://www.cccaasports.org/about/List_of_3C2A_Schools")

    members=[]
    gender_sport=[]
    for ind, member_tr in enumerate(list_html.select("table tr")):
        if ind >0:
            tds=member_tr.select("td")
            if len(tds)>1:
                member=tds[0].text
                city=tds[1].text
                nickname = tds[2].text
                conference = tds[3].text
                members.append(Member(member,city,nickname,conference))


    export_to_excel(members,"c_cccaa_members")

if __name__=="__main__":
    crawl_CCCAA()