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
class GenderSport:
    member_val: str
    member: str
    div: str
    conf: str
    gender: str
    sport: str


@dataclass
class Member:
    member_val: str
    member: str
    member_url: str
    team_logo_url: str
    address: str
    city: str
    state: str
    zip: str
    member_phone: str
    institut_url:str
    athletics_url:str
    athletics_facebook:str
    athletics_x:str
    div: str
    conf: str
    mascot: str
    affiliation: str
    mens_sports: str
    womens_sports: str
    coed_sports: str
    asterix_val: str

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

def get_parent_text(html,index,part=None):
    try:
        child=html[index]
        if part:
            return child.parent.text.split(":")[1] if part in child.parent.text else ""
        else:
            return child.parent.text.split(":")[1]
    except:
        return ""
def crawl_NCCAA():
    root="https://thenccaa.org"  # will be different for different conferences
    listing_html=get_url_content("%s/sports/2017/6/14/Member_Schools_17-18.aspx"%root)
    listing=[item for item in listing_html.select('table td a')]
    members=[]
    gender_sports=[]
    athletes=[]
    count=0
    for ind, link in enumerate(listing):
        try:
            link_url=link["href"]
        except:
            continue
        if "#" not in link_url:
            member_url=link_url if "http" in link_url else "%s%s"%(root,link_url)
            member_val=link_url.split("?id=")[1].replace("&","") if "?id=" in link_url else ""
            html=get_url_content(member_url)
            h1 = html.select('h1')[1]
            name=h1.text
            logo= html.select('table td img')[0]['src']
            logo=logo if "http" in logo else root+logo
            address_block = html.select('.article-content span span strong')[0]
            address_parsed=address_block.text.split("<br>")[0].splitlines()
            address=address_parsed[0]
            area_part=address_parsed[1].strip()
            city=area_part.split(",")[0] if "," in area_part else area_part.split(" ")[0]
            state=area_part.split(",")[1].strip().split(" ")[0] if "," in area_part else area_part.split(" ")[1]
            zip = (area_part.split(",")[1].strip().split(" ")[1] if len(area_part.split(",")[1].strip().split(" "))>1 else "") if "," in area_part else " ".join([item for index, item in enumerate(area_part.split(" "))  if index > 1])
            member_phone=address_parsed[2]
            blue_links=html.select('.article-content span span b a')
            institut_url=blue_links[4]["href"] if len(blue_links) > 4 else html.select('.article-content td > a')[0]["href"]
            athletics_url = blue_links[5]["href"] if len(blue_links) > 5 else html.select('.article-content td > a')[1]["href"]
            institut_url=institut_url if "http" in institut_url else "%s%s" % (root, institut_url)
            athletics_url = athletics_url if "http" in athletics_url else "%s%s" % (root, athletics_url)
            athletics_facebook=""
            athletics_x=""
            for img in html.select('.article-content td a img'):
                if "facebook" in img["src"]:
                    facebook_a=img.parent
                    athletics_facebook=facebook_a["href"]
                if "twitter" in img["src"]:
                    twitter_a=img.parent
                    athletics_x=twitter_a["href"]
            div = get_parent_text(html.select('.article-content span span strong'),2).strip()
            conf = get_parent_text(html.select('.article-content span span strong'), 3).strip()
            mascot = get_parent_text(html.select('.article-content span span strong'), 4).strip()
            affiliation = get_parent_text(html.select('.article-content span span strong'), 5).strip()
            mens_sports = get_parent_text(html.select('.article-content span span strong'), 7,"Men").strip()
            womens_sports = get_parent_text(html.select('.article-content span span strong'), 8,"Women").strip()
            coed_sports = get_parent_text(html.select('.article-content span span strong'), 9,"Coed").strip()
            coed_sports=coed_sports.splitlines()[0] if len(coed_sports) >0 else ""
            trs=html.select('.article-content table tr')
            last_tr=trs[len(trs)-1]
            asterix_val=last_tr.select("td span span")[0].text if len(last_tr.select("td span span")) >=1 else (last_tr.select("td")[0].text if len(last_tr.select("td")) >=1 else "")
            asterix_val=asterix_val.replace("*","").strip()
            asterix_val=asterix_val if "Division" in asterix_val else ""
            members.append(Member(member_val,name,member_url,logo,address,city,state,zip,member_phone,institut_url,athletics_url,athletics_facebook,athletics_x,div,conf,mascot,affiliation,mens_sports,womens_sports,coed_sports,asterix_val))

            gender_list=[{"gender":"men","data":mens_sports.split(",")},{"gender":"women","data":womens_sports.split(",")},{"gender":"coed","data":coed_sports.split(",")}]
            for gender in gender_list:
                if gender["gender"] == "coed":
                    if len(coed_sports) <=0:
                        continue
                for item in gender["data"]:
                    div_later=div
                    if "^" in item:
                        div_later="Not sponsored by NCCAA"
                    if "*" in item:
                        div_later = asterix_val.split(" ")[1]
                    gender_sports.append(GenderSport(member_val,name,div_later,conf,gender["gender"],item.strip()))

    export_to_excel(members,"c_nccaa_members")
    export_to_excel(gender_sports, "c_nccaa_school_sports")

if __name__=="__main__":
    crawl_NCCAA()