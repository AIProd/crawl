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
class Member:
    member_val: str
    member: str
    team: str
    div: str
    skater_url: str
    team_logo_url: str
    roster_url: str

@dataclass
class Roster:
    member_val: str
    team: str
    position: str
    jersey_number: str
    player: str
    player_image_url: str
    player_profile_url: str
    title: str
    pos: str
    height: str
    weight_lb: str
    shoots: str
    catches: str
    home_town_city: str
    home_town_state: str

@dataclass
class Player_common:
    member_val: str
    team: str
    roster_id: str
    player: str
    gp: str
    g: str
    a: str
    pts: str
    gwg: str
    pim: str
    sh: str
    ppg: str
    shg: str
    sog: str
    soa: str
    sogw: str
    so_percent: str

@dataclass
class Player_reg(Player_common):
    regular_season: str

@dataclass
class Player_playoff(Player_common):
    playoffs: str

@dataclass
class Division:
    div_val: str
    acha_div_name: str

@dataclass
class Conference:
    div_val: str
    conf_val: str
    div: str
    conf: str


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

def get_acha_data(element,position):
    section = element[position]
    position = section.select("span")[0].text if len(section.select("span")) > 0 else ''
    return position

def crawl_ACHA():
    root="https://www.achahockey.org"
    html=get_url_content(root+"/stats/standings?season=45&conference=11&division=-1&standingstype=division&context=overall&specialteams=false&sortkey=points&league=1")
    menu_titles=["Men's Divisions","Women's Divisions"]
    important_menu=["Team Records","Rosters"]
    sub_menu_titles=html.select(".build-mega-menu .menu-item > a")
    menus=[]
    today=datetime.now()
    current_year=today.year
    for sub_menu in sub_menu_titles:
        if sub_menu.text in menu_titles:
            menu_item=sub_menu.parent
            for a in menu_item.select(".mega-menu-widget a"):
                if a.text == "Team Records":
                    menus.append(a)
    members =[]
    divisions=[]
    conferences=[]
    for menu in menus:
        team_records=get_url_content(menu["href"])
        selects=team_records.select(".ht-content-area .ht-col-left-select:not(.ng-hide) > select")
        selected_season=selects[1].select("option[selected='selected']")[0]
        if str(current_year) in selected_season.text:
            season_id=selected_season["value"]
            divisions_options=selects[2].select("option")
            divisions =  divisions+[{"label":item.text,"value":item["value"],"acronym":"".join([ s[0] for s in item.text.split() ])} for item in divisions_options if "All" not in item.text]
            conferences_options = selects[3].select("option")
            conferences = conferences+[{"label":item.text,"value":item["value"]} for item in conferences_options]
            conference_sections=team_records.select(".ht-table tbody")
            for conference_section in conference_sections:
                conference_section_trs=conference_section.select("tr")
                for index, tr in enumerate(conference_section_trs):
                    if index <= 0:
                        continue
                    member_block=tr.select("td a")[0]
                    member_name=member_block.text
                    division=member_name.split(" ")[0]
                    member=" ".join([item for item in member_name.split(" ") if item != division])
                    skater_url = check_url(root+member_block["href"])
                    member_season_list=skater_url.split("player-stats/")[1].split("?")[0]
                    member_id=member_season_list.split("/")[0]
                    season_id = member_season_list.split("/")[1]
                    roster_url=check_url(root+"/stats/roster/"+member_id+"/"+season_id)
                    members.append(Member(member_id,member,member_name,division,skater_url,"",roster_url))
    divisions_c = []
    conferences_c = []
    divisions = [dict(t) for t in set(tuple(item.items()) for item in divisions)]
    conferences = [dict(t) for t in set(tuple(item.items()) for item in conferences)]
    for division in divisions:
        divisions_c.append(Division(division["value"],division["label"]))

    for conference in conferences:
        division=conference["label"].split(" ")[0]
        division_match=[item for item in divisions if division == item["acronym"]]
        division_obj=division_match[0] if len(division_match) > 0 else None
        if division_obj:
            conferences_c.append(Conference(division_obj["value"],conference["value"],division,conference["label"].split(" ")[1]))

    rosters = []
    member_check=[]
    for member in members:
        if member.member_val in member_check:
            continue
        member_check.append(member.member_val)
        roster = get_url_content(member.roster_url)
        if len(member.team_logo_url) <= 0:
            member_logo = check_url(roster.select(".ht-roster-team-logo img")[0]["src"])
            member.team_logo_url=member_logo
        roster_sections = roster.select(".ht-table tbody")
        for roster_section in roster_sections:
            roster_section_tr = roster_section.select("tr")
            for index, tr in enumerate(roster_section_tr):
                if index <= 1:
                    continue
                name_section = tr.select("td")[1]
                home_town_city = ""
                home_town_state = ""
                if len(name_section.select("a")) > 0:
                    jersey_number = get_acha_data(tr.select("td"), 0)
                    name_anchor = name_section.select("a")[0]
                    player=name_anchor.text
                    player_profile_url=check_url(root+name_anchor["href"])
                    player_image_url=check_url(name_anchor.select("img")[0]["src"])
                    pos = get_acha_data(tr.select("td"), 2)
                    height = get_acha_data(tr.select("td"), 4)
                    weight = get_acha_data(tr.select("td"), 5)
                    shoots = get_acha_data(tr.select("td"), 6)
                    catches = get_acha_data(tr.select("td"), 7)
                    hometown = get_acha_data(tr.select("td"), 8)
                    if len(hometown) > 0:
                        if "," in hometown:
                            home_town_city = hometown.split(",")[0]
                            home_town_state = hometown.split(",")[1]
                        else:
                            home_town_city = hometown
                    title=""
                    position="Forwards" if pos=="F" else ("Defencemen" if pos=="D" else "Goalies")
                else:
                    player = get_acha_data(tr.select("td"), 1)
                    jersey_number=""
                    player_profile_url=""
                    player_image_url=""
                    title=get_acha_data(tr.select("td"), 3)
                    pos=""
                    height=""
                    weight=""
                    shoots=""
                    catches=""
                    position ="Coaches"
                member_val = member.member_val
                team = member.team
                rosters.append(Roster(member_val,team,position,jersey_number,player,player_image_url,player_profile_url,title,pos,height,weight,shoots,catches,home_town_city,home_town_state))

    reg_sessions=[]
    playoffs=[]
    stats_columns=["","","gp","g","a","pts","gwg","pim","sh","ppg","shg","sog","soa","sogw",f"so%"]
    for index_roster, roster in enumerate(rosters):
        if len(roster.player_profile_url) >0:
            member_val = roster.member_val
            team = roster.team
            roster_id=roster.player_profile_url.split("/player/")[1].split("/")[0]
            player=roster.player
            player_details = get_url_content(roster.player_profile_url)
            try:
                player_stats = player_details.select("#ht-statview .ht-player-data table.ht-table")[0]
            except:
                continue
            player_reg = player_stats.select("tbody")[0]
            for index, tr in enumerate(player_reg.select("tr")):
                if index <= 1 or index >= len(player_reg.select("tr")) -1:
                    continue
                stats_obj={}
                season = get_acha_data(tr.select("td"), 0)
                for stats_ind,td  in enumerate(tr.select("td")):
                    if stats_ind >= 2:
                        stats_obj[stats_columns[stats_ind]]=get_acha_data(tr.select("td"), stats_ind)
                reg_sessions.append(Player_reg(member_val,team,roster_id,player,stats_obj["gp"],stats_obj["g"],stats_obj["a"],stats_obj["pts"],stats_obj["gwg"],stats_obj["pim"],stats_obj["sh"],stats_obj["ppg"],stats_obj["shg"],stats_obj["sog"],stats_obj["soa"],stats_obj["sogw"],stats_obj[f"so%"],season))
            if len(player_stats.select("tbody")) > 1:
                player_playoffs = player_stats.select("tbody")[1]
                for index, tr in enumerate(player_playoffs.select("tr")):
                    if index <= 1 or index >= len(player_playoffs.select("tr")) -1:
                        continue
                    stats_obj={}
                    season = get_acha_data(tr.select("td"), 0)
                    for stats_ind,td  in enumerate(tr.select("td")):
                        if stats_ind >= 2:
                            stats_obj[stats_columns[stats_ind]]=get_acha_data(tr.select("td"), stats_ind)
                    playoffs.append(Player_reg(member_val,team,roster_id,player,stats_obj["gp"],stats_obj["g"],stats_obj["a"],stats_obj["pts"],stats_obj["gwg"],stats_obj["pim"],stats_obj["sh"],stats_obj["ppg"],stats_obj["shg"],stats_obj["sog"],stats_obj["soa"],stats_obj["sogw"],stats_obj[f"so%"],season))


    export_to_excel(divisions_c, "c_acha_div")
    export_to_excel(conferences_c, "c_acha_conf")
    export_to_excel(members, "c_acha_members")
    export_to_excel(rosters, "c_acha_member_roster")
    export_to_excel(reg_sessions, "c_acha_players_reg_season")
    export_to_excel(playoffs, "c_acha_players_playoff")



if __name__=="__main__":
    crawl_ACHA()

