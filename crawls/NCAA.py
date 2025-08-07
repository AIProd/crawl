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
from datetime import datetime

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

conference="NCAA"

def get_init_data_from_api(url=''):
    api_url = url
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "application/json, text/plain, */*",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
    }
    json_data=[]
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200 or response.status_code == 202:
        json_data = response.json()
    else:
        print("Error: ", response.status_code)
        return []

    member_list = [{"orgId":token["orgId"]} for token in json_data]
    return member_list


def get_url_content(url):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)
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
class Athlete:
    member: str
    member_val: str
    name: str
    gender_sport: str
    division: str
    conf: str
    conf_url: str
    academic_year: str


@dataclass
class Admin:
    member: str
    member_val: str
    name: str
    title: str


@dataclass
class School:
    member_val: str
    member: str
    member_url: str
    name: str
    logo: str
    address: str
    city: str
    state: str
    zip: str
    division: str
    active: str
    conf_name: str
    conf_url: str
    conf_val: str
    pronoun: str
    since: str
    private: str
    hbcu: str
    inst_link: str
    inst_facebook: str
    inst_x: str
    inst_inst: str
    athlete_link: str
    athlete_facebook: str
    athlete_x: str
    athlete_inst: str


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

def crawl_NCAA():
    root="https://web3.ncaa.org"  # will be different for different conferences
    listing=get_init_data_from_api("%s/directory/api/directory/memberList?type=1&_=1743490359036"%root)
    listing=sorted(listing, key=lambda d: d['orgId'])
    schools=[]
    admins=[]
    athletes=[]
    count=0
    for ind, x in enumerate(listing):
        print(ind)
        member_url="%s/directory/orgDetail?id=%s"%(root,x["orgId"])
        html=get_url_content(member_url)
        h1 = html.select('h1')[0]
        name=' '.join([item.text.strip() for item in h1.select('span')])
        logo= h1.select('img')[0]['src']
        logo=logo if "http" in logo else root+logo
        team=html.select('h4')[0].text
        address_tag = html.select('address')[0]
        add_len=len(address_tag.select('span'))
        address=''
        for i in range(add_len-3):
            address="%s %s"%(address,address_tag.select('span')[i].text)
        city = address_tag.select('span')[add_len-3].text
        state = address_tag.select('span')[add_len-2].text
        zip = address_tag.select('span')[add_len-1].text
        info_block=address_tag.find_previous()
        division=info_block.select('address + span')[0].text
        active = info_block.select('address + span + span')[0].text
        conf_block=info_block.select('a')[0]
        conf_name=conf_block.text
        conf_url=root+conf_block['href'] if len(conf_name) > 0 else ''
        conf_val=conf_url.split("id=")[1] if len(conf_name) > 0 else ''
        pronoun = ''
        since = ''
        private = ''
        hbcu = ''
        for dv in info_block.select('div'):
            if 'Since' in dv.text:
                since=dv.select("span")[0].text
            elif 'Public' in dv.text:
                private = dv.select("span")[0].text
            elif 'HBCU' in dv.text:
                hbcu = dv.select("span")[0].text
            elif 'Pronunciation' in dv.text:
                pronoun = dv.select("span")[0].text
        link_list = html.select(".institutionDetail .col-md-4 .list-group")

        inst_link = ''
        inst_facebook = ''
        inst_x = ''
        inst_inst = ''
        athlete_link = ''
        athlete_facebook = ''
        athlete_x = ''
        athlete_inst = ''
        if len(link_list) > 0:
            lnk=link_list[0].select("a.list-group-item")
            inst_link=check_url(lnk[1]["href"]) if len(lnk) > 1 else ''
            fb=link_list[0].select("li.list-group-item a[title='Facebook']")
            inst_facebook = check_url(fb[0]["href"]) if len(fb) > 0 else ''
            tw=link_list[0].select("li.list-group-item a[title='Twitter']")
            inst_x = check_url(tw[0]["href"]) if len(tw) > 0 else ''
            ins=link_list[0].select("li.list-group-item a[title='Instagram']")
            inst_inst = check_url(ins[0]["href"]) if len(ins) > 0 else ''
        if len(link_list) > 1:
            lnk = link_list[1].select("a.list-group-item")
            athlete_link = check_url(lnk[1]["href"]) if len(lnk) > 1 else ''
            fb = link_list[1].select("li.list-group-item a[title='Facebook']")
            athlete_facebook = check_url(fb[0]["href"]) if len(fb) > 0 else ''
            tw = link_list[1].select("li.list-group-item a[title='Twitter']")
            athlete_x = check_url(tw[0]["href"]) if len(tw) > 0 else ''
            ins = link_list[1].select("li.list-group-item a[title='Instagram']")
            athlete_inst = check_url(ins[0]["href"]) if len(ins) > 0 else ''
        school=School(x["orgId"],name,member_url,team,logo,address,city,state,zip,division,active,conf_name,conf_url,conf_val,pronoun,since,private,hbcu,inst_link,inst_facebook,inst_x,inst_inst,athlete_link,athlete_facebook,athlete_x,athlete_inst)

        schools.append(school)
        tables=html.select(".institutionDetail section table:not(.coo-table) tbody")

        for index1, tr in enumerate(tables[0].select('tr')):
            if index1 >0:
                title= ''.join([item.text.strip() for item in tr.select('td')[0].select('span')])
                full_name = ''.join([item.text.strip() for item in tr.select('td')[1].select('span')])
                full_name = " ".join(full_name.split())
                if len(full_name) >0:
                    admin=Admin(name,x["orgId"],full_name,title)
                    admins.append(admin)
        for index1, tr in enumerate(tables[1].select('tr')):
            if index1 >0:
                gender_sport = tr.select('td')[0].text.strip()
                full_name = ''.join([item.text.strip() for item in tr.select('td')[1].select('span')])
                full_name=" ".join(full_name.split())
                division = tr.select('td')[2].text.strip()
                conf = tr.select('td')[3].select('a')[0].text.strip()
                conf_url_athlete = check_url(root+tr.select('td')[3].select('a')[0]['href'])
                athlete_section=html.select(".institutionDetail section")[1]
                academic_year=athlete_section.select(".panel-heading span")[0].text
                if len(full_name) >0:
                    athlete = Athlete(name, x["orgId"], full_name, gender_sport, division, conf, conf_url_athlete,academic_year)
                    athletes.append(athlete)

    export_to_excel(schools,"c_ncaa_members")
    export_to_excel(admins, "c_ncaa_member_admin")
    export_to_excel(athletes, "c_ncaa_member_sports")

if __name__=="__main__":
    crawl_NCAA()

