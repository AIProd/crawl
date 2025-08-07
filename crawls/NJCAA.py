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



def get_url_content(url,CLASS_NAME):
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
class GenderSport:
    member: str
    member_val: str
    conf: str
    gender: str
    sport: str
    div: str

@dataclass
class Member:
    member_val: str
    member: str
    member_url: str
    team_avatar: str
    address: str
    city: str
    state: str
    member_since: str
    institut_url: str
    athletics_url: str
    conf: str
    national_championships: str
    mascot: str
    women_mascot: str
    member_colors: str
    division1_sport: str
    division2_sport: str
    division3_sport: str
    non_divisional: str
    institut_facebook: str
    institut_x: str
    institut_instagram: str

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

def crawl_NJCAA():
    root="https://njcaamemberdirectory.prestosports.com"
    members_links=[]
    for page in range(1,30):
        try:
            list_html=get_url_content("%s/njcaa-member-directory/?frm-page-15=%s"%(root,page),"directory-container")
            a=list_html.select(".directory-container h5 a")
            members_links=members_links+[item['href'] for item in a]
        except:
            continue
    members=[]
    gender_sport=[]
    for ind, link in enumerate(members_links):
        html = get_url_content(link,"site-main")
        h1 = html.select('h1')[0]
        name=h1.text.strip()
        first_info_divs=html.select(".row .col-12 .row .col-8")
        second_info_divs = html.select(".row .col-12 .row .col-md-8")

        division_divs = html.select(".row .col-12 > span")
        avatar_img = html.select(".row .col-md-2 img")[0]
        team_avatar=check_url(avatar_img['src'])
        institut_url=check_url(first_info_divs[0].select("a")[0]["href"])
        member_since=first_info_divs[1].select("span")[0].text
        athletics_url = check_url(second_info_divs[0].select("a")[0]["href"])
        conf = second_info_divs[1].select("span")[0].text
        national_championships = second_info_divs[2].select("span")[0].text
        mascot = second_info_divs[3].select("span")[0].text
        mascot = mascot.split("&")[0] if "&" in mascot else mascot
        women_mascot = mascot.split("&")[1] if "&" in mascot else ''
        member_colors=second_info_divs[4].select("span")[0].text
        division1_sport=division_divs[0].text
        division2_sport = division_divs[1].text
        division3_sport = division_divs[2].text
        non_divisional = division_divs[3].text

        member_val=link.split("listing/")[1].replace("/","")
        address_blocks=[item.text for item in html.select(".social-container .mb-4 div") if len(item.text) > 0]
        last_block=address_blocks[len(address_blocks)-1]
        city=last_block.split(",")[0] if len(last_block) > 0 else ''
        state = last_block.split(",")[1] if len(last_block) > 0 else ''
        address=" ".join([item for index, item in enumerate(address_blocks) if index >= len(address_blocks)-2 ])
        social_blocks = html.select(".social-container .social-ul li")
        institut_facebook=""
        institut_instagram=""
        institut_x=""
        # institut_facebook = check_url(social_blocks[0].select("a")[0]["href"]) if len(social_blocks[0].select("a")) >0 else ""
        # institut_instagram = check_url(social_blocks[1].select("a")[0]["href"]) if len(social_blocks[1].select("a")) > 0 else ""
        # institut_x = check_url(social_blocks[2].select("a")[0]["href"]) if len(social_blocks[2].select("a")) > 0 else ""
        members.append(Member(member_val,name,link,team_avatar,address,city,state,member_since,institut_url,athletics_url,conf,national_championships,mascot,women_mascot,member_colors,division1_sport,division2_sport,division3_sport,non_divisional,institut_facebook,institut_x,institut_instagram))
        sports =[{"name":"division1","data": division1_sport.split(",")},
                 {"name":"division2","data": division2_sport.split(",")},
                 {"name":"division3","data": division3_sport.split(",")},
                 {"name": "non_divisional", "data": non_divisional.split(",")}]
        gender_sport_division_obj={}
        for div in sports:
            for sport in div["data"]:
                sport_cleaned=sport.strip()
                if len(sport_cleaned) >0:
                    no_gender=False
                    gender=""
                    if 'women' in sport_cleaned.lower():
                        gender = 'women'
                    elif 'men' in sport_cleaned.lower():
                        gender = 'men'
                    else:
                        no_gender = True

                    sport=" ".join([item.strip() for index, item in enumerate(sport_cleaned.split(" ")) if index >= 1 ]) if not no_gender else sport_cleaned
                    gender_sport_division_obj["%s_%s_%s"%(gender,sport,div["name"])]=GenderSport(name,member_val,conf,gender,sport,div["name"])
        gender_sport=gender_sport+list(gender_sport_division_obj.values())


    export_to_excel(members,"c_njcaa_members")
    export_to_excel(gender_sport, "c_njcaa_school_sports")

if __name__=="__main__":
    crawl_NJCAA()