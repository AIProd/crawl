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
class Member:
    member_val: str
    member: str
    member_url: str
    team_logo_url: str
    president: str
    city: str
    state: str
    vice_president: str
    treasurer: str
    secretary: str
    team_email: str
    institut_url: str
    athletics_url: str
    athletics_facebook: str
    athletics_x: str
    athletics_instagram: str
    athletics_facebook_group: str
    athletics_youtube: str
    gender: str
    sport: str

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
    root="https://thencwsa.org"
    listing_html = get_url_content(root+"/teams/", "wp-block-list")
    members_list=listing_html.select(".wp-block-list li")
    members=[]
    for ind, member_li in enumerate(members_list):
        link=member_li.select("a")
        member_obj = {"member_val": "",
                      "member": member_li.text.strip(),
                      "member_url": "",
                      "team_logo_url": "",
                      "president": "",
                      "city": "",
                      "state": "",
                      "vice_president": "",
                      "treasurer": "",
                      "secretary": "",
                      "team_email": "",
                      "institut_url": "",
                      "athletics_url": "",
                      "athletics_facebook": "",
                      "athletics_x": "",
                      "athletics_instagram": "",
                      "athletics_facebook_group": "",
                      "athletics_youtube": "",
                      "gender": "coed",
                      "sport": "waterski"
                      }
        if len(link) >=1:
            member_obj["member_url"]=link[0]["href"]
            if "teams/" in member_obj["member_url"]:
                member_obj["member_val"] = member_obj["member_url"].split("teams/")[1].replace("/","")
            else:
                members_splits=member_obj["member_url"].split("/")
                member_obj["member_val"]=members_splits[len(members_splits)-2]
            html = get_url_content(member_obj["member_url"],"post-inner-content")
            if len(html.select('#main article h1')) >0:
                h1 = html.select('#main article h1')[0]
                member_obj["member"]=h1.text.strip()
                if len(html.select("#main > img"))>0:
                    avatar_img = html.select("#main > img")[0]
                    member_obj["team_logo_url"] = check_url(avatar_img['src'])

            delimiter=":"
            if len(html.select("#main .entry-content ul")) >0:
                info_ul = html.select("#main .entry-content ul")[0]
                first_li = info_ul("li")[0]
                if ":" not in first_li.text:
                    info_ul = html.select("#main .entry-content ul")[1]
                for info_text in info_ul.select("li"):
                    if "Vice President" in info_text.text:
                        member_obj["vice_president"] = info_text.text.split(delimiter)[1].strip()
                    elif "President" in info_text.text:
                        member_obj["president"] = info_text.text.split(delimiter)[1].strip()
                    elif "Treasurer" in info_text.text:
                        member_obj["treasurer"] = info_text.text.split(delimiter)[1].strip()
                    elif "Secretary" in info_text.text:
                        member_obj["secretary"] = info_text.text.split(delimiter)[1].strip()
                    elif "Team Email" in info_text.text:
                        member_obj["team_email"] = info_text.text.split(delimiter)[1].strip()
                last_li=info_ul.select("li")
                location_li=last_li[len(last_li)-1]
                if location_li:
                    location =location_li.text.split("located in")[1].strip() if "located in" in location_li.text else (location_li.text.split("is in")[1].strip() if "is in" in location_li.text else "")
                    if "," in location:
                        member_obj["city"]=location.split(",")[0].strip()
                        member_obj["state"] = location.split(",")[1].strip()
            for h3 in html.select("#main .entry-content h3"):
                if "Social Media" in h3.text:
                    social_ul=h3.find_next_sibling()
                    if social_ul.name.lower() == "ul":
                        for li in social_ul.select("li"):
                            if "Website" in li.text:
                                member_obj["institut_url"]=check_url(li.select("a")[0]["href"])
                            elif "Facebook" in li.text:
                                member_obj["athletics_facebook"]=check_url(li.select("a")[0]["href"])
                            elif "Instagram" in li.text:
                                member_obj["athletics_instagram"]=check_url(li.select("a")[0]["href"]) if len(li.select("a")) > 0 else ""
                            elif "Twitter" in li.text:
                                member_obj["athletics_x"]=check_url(li.select("a")[0]["href"])
                    elif social_ul.name.lower() == "p":
                        social_as = social_ul.select("a")
                        for a in social_as:
                            if "facebook" in a["href"] and "group" in a["href"]:
                                member_obj["athletics_facebook_group"] = check_url(a["href"])

                            elif "facebook" in a["href"]:
                                member_obj["athletics_facebook"]=check_url(a["href"])
                            elif "instagram" in a["href"]:
                                member_obj["athletics_instagram"] = check_url(a["href"])
                            elif "twitter" in a["href"]:
                                member_obj["athletics_x"] = check_url(a["href"])
                            elif "youtube" in a["href"]:
                                member_obj["athletics_youtube"] = check_url(a["href"])

                    elif social_ul.name.lower() == "figure":
                        tables=social_ul.select("table")
                        if len(tables) <=0:
                            social_ul_next=social_ul.find_next_sibling()
                            social_tds=social_ul_next.select("table td")
                            for td in social_tds:
                                social_a=td.select("a")[0]
                                if "insta" in social_a["href"]:
                                    member_obj["athletics_instagram"]=check_url(social_a["href"])
                                elif "facebook" in social_a["href"]:
                                    member_obj["athletics_facebook"] = check_url(social_a["href"])
                                else:
                                    member_obj["institut_url"] = check_url(social_a["href"])

        else:
            pass
        members.append(Member(**member_obj))


    export_to_excel(members,"c_ncwsa_members")

if __name__=="__main__":
    crawl_NJCAA()