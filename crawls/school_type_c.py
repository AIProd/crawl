from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import re

chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
service = Service('C:/chromedriver-win32/chromedriver.exe')
driver = webdriver.Chrome(service=service,options=chrome_options)

class StaffData:

  def __init__(self, link_url='', name='', title='', twitter='', phone='', email='', dept=''):
    self.link_url = link_url
    self.name = name
    self.title = title
    self.twitter = twitter
    self.phone = phone
    self.email = email
    self.dept = dept
  
  def to_array(self):
    return [self.dept, self.name, self.link_url, self.title, self.phone, self.email, self.twitter]

def get_url_content(url, school_id):
  try:
    driver.get(url)
    wait = WebDriverWait(driver, 200)
    if school_id == 125:
      wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'table[summary="Athletic, Physical Education and Recreation Staff"]')))
    # elif school_id == 16:
    #   # Wait until the loading spinner is gone
    #   loading_spinner_locator = (By.CLASS_NAME, "loading")
    #   wait.until(EC.invisibility_of_element_located(loading_spinner_locator))
    elif school_id == 16:
      wait.until(EC.visibility_of_element_located((By.TAG_NAME, "table")))
    elif school_id == 551:
      wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class="wysiwyg__body"]')))
    elif school_id == 604 or school_id == 484:
      print("Hello world!")
      wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'section[class="staff-directory"]')))
    elif school_id == 1006:
      wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'section[class="comp-l855ktnz CohWsy wixui-column-strip"]')))
    elif school_id == 1321:
      wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class="flexbox content_body"]')))
    elif school_id == 593:
      wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'table[class="cols-3"]')))
    elif school_id == 2160:
      wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'section[id="maincontent"]')))
    elif school_id == 722:
      wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'table[aria-label="Employee Directory"]')))
    html_content = driver.page_source
  except:
    print("I am in")
    headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    page = requests.get(url, headers=headers)
    html_content = page.text
  soup = BeautifulSoup(html_content, "html.parser")
  return soup
def is_title(text):
    if text == '':
      return False
    patterns = ["Athletic", "Director", "Manager", "Sports", "Staff", "Defensive", "Offensive", "Receivers",
      "Safeties", "Broadcaster", "Strength", "Conditioning", "Center", "Office", "Cell", "Resource", "Advisors",
      "Assistant", "Head", "Associate", "Compliance", "President", "Follow", "Twitter", "Instagram",
      "Representative", "Senior", "Junior", "Registered", "Psychiatrist", "Primary", "Number", "Begin"
      "Supervisor", "Coordinator", "Volunteer", "Student", "Athlete", "Trainer", "Physician", "Invoices", "Science",
      "Account", "Statement", "Purchase", "Ticket", "Maintenance", "Cafeteria", "Campus Police", "Housing Lock Out Line",
      "Advisor", "Counselor", "Specialist", "Officer", "Recruiter", "Recruiting", "Recruitment"]
    
    sports_pattern = ["Acrobatics & Tumbling", "Archery", "Badminton", "Baseball", "Basketball",
    "Beach Volleyball", "Bowling", "Crew/Rowing", "Cycling/Biking", "Equestrian",
    "Fencing", "Field Hockey", "Football", "Golf", "Gymnastics", "Ice Hockey",
    "Lacrosse", "Martial Arts", "Polo", "Rifle/Shooting", "Rodeo", "Rugby",
    "Sailing", "Skiing", "Soccer", "Softball", "Sprint Football", "Squash",
    "Swimming & Diving", "Tennis", "Volleyball", "Water Polo", "Wrestling",
    "Swimming", "Diving", "Cheerleading", "Hockey", "Triathlon", "Cheerleader", "Dance",
    "Esports", "Handball", "Skating", "Waterski", "Athletic Staff", "Futsal",
    "Swim", "Dive", "Shotgun", "Stunt", "Surf", "Cheer & Stunt", "Cornhole",
    "Boxing", "Spirit Squad", "Cheer"
    "Climbing", "Club Sport", "Cross Country/Track & Field", "Fishing",
    "Flag Football", "JV Sport", "Logging Sport", "Marching Band/Band",
    "Outdoor Track & Field", "Indoor Track & Field", "Track and Field",
    "Motorsports", "Snowboarding"]
    
    patterns += sports_pattern
    return any(word.lower() in text.lower() for word in patterns)

def get_value(element):
  if element == None:
    return ""
  return element.text.strip()

def count_digits(input_string):
  # Use a list comprehension to iterate through characters in the string and count digits
  digit_count = sum(1 for char in input_string if char.isdigit())
  
  return digit_count

def find_phone_number(array):
  for index, data in enumerate(array):
    if (data.lower() == "phone:" or data.lower() == "phone number:" or data.lower() == "p") and index + 1 < len(array):
      return array[index + 1]
  for data in array:
    if count_digits(data) >= 5:
      return data
  return ""

def find_email(array):
  for index, data in enumerate(array):
    if (data.lower() == "email:" or data.lower() == "e") and index + 1 < len(array):
      return array[index + 1]
    if extract_emails(data) != []:
      return " ".join(extract_emails(data))
  
  return ""

def find_title(array):
  for index, data in enumerate(array):
    if ("position" in data.lower()) and index + 1 < len(array):
      return array[index + 1]
  return ""

def get_element_value(element):
  result_text = '|'.join(line.strip() for line in element.stripped_strings)
  return result_text

def extract_emails(text):
  # Define the regular expression pattern for an email address
  email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
  
  # Use re.findall to find all email addresses in the given text
  emails = re.findall(email_pattern, text)
  
  return emails

def crawl_script_school_16(url, school_id):
  soup = get_url_content(url, school_id)
  tables = soup.find_all('table', {'class': 'facultyTable'})
  member_list = []
  if len(tables) > 0:
    for table in tables:
      tr_rows = table.select('tr')
      print(len(tr_rows))
      for tr in tr_rows:
        staff_data = StaffData()
        td_list = tr.select('td')
        if len(td_list) < 2:
          continue
        data = td_list[1]
        name_url = data.find('h3')
        if name_url == None:
          continue
        staff_data.name = name_url.text.strip()
        link_url = name_url.find('a')
        if link_url != None:
          staff_data.link_url = urljoin(url, link_url['href'])
        else:
          staff_data.link_url = ""
        staff_data.title = get_value(data.find('span', {'class': 'title'}))
        staff_data.email = get_value(data.find('span', {'class': 'email'}))
        staff_data.phone = get_value(data.find('span', {'class': 'phone'}))
        staff_data.dept = "Athletic Staff"
        if staff_data.name == "" or staff_data.title == "":
          continue
        member = [16, "Atlantic Cape Community College"] + staff_data.to_array()
        print(member)
        member_list.append(member)
  return member_list

def crawl_script_school_41(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'testimonial-grid'})
  member_list = []
  if len(divs) == 0: 
    return member_list
  for div in divs:
    p_data_element = div.find('p', {'class': 'testimonial-grid-title'})
    text = get_value(p_data_element)
    staff_data = StaffData()
    staff_data.title = text.split("---")[0]
    staff_data.name = text.split("---")[1] if len(text.split("---")) > 1 else ""
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Delaware Technical Community College-Terry"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  
  return member_list

def crawl_script_school_46(url, school_id):
  urls = {
    "Employee Directory": url,
    "Falcuty Directory": "https://www.lenoircc.edu/aboutlcc/employeedirectory/faculty/",
    "Staff Directory": "https://www.lenoircc.edu/aboutlcc/employeedirectory/staff/"
  }
  member_list = []
  for key, url in urls.items():
    soup = get_url_content(url, school_id)
    divs = soup.find_all('div', {'class': 'directorysearchresults'})
    if len(divs) == 0:
      continue
    for div in divs:
      staff_data = StaffData()
      result_text = '|'.join(line.strip() for line in div.stripped_strings)
      if result_text == "":
        continue
      staff_data.name = result_text.split("|")[0]
      staff_data.title = result_text.split("|")[1] if len(result_text.split("|")) > 1 else ""
      staff_data.dept = key
      staff_data.phone = find_phone_number(result_text.split("|"))
      staff_data.email = find_email(result_text.split("|"))
      member = [school_id, "Lenoir Community College"] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_54(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'contact-info'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.select("div")[0])
    p_info_div = div.select("div")[1]
    staff_data.title = get_value(p_info_div.select('p')[0])
    staff_data.email = get_value(p_info_div.select('p')[1])
    staff_data.phone = get_value(p_info_div.select('p')[2])
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Chattahoochee Valley Community College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_97(url, school_name, school_id):
  soup = get_url_content(url, school_id)
  sections = soup.find_all('section', {'class': 'staff-directory'})
  member_list = []
  for section in sections:
    dept = get_value(section.find("h2"))
    divs = section.find_all('div', {'class': 'row no-gutters w-100'})
    if len(divs) == 0:
      continue
    print(len(divs))
    for div in divs:
      staff_data = StaffData()
      staff_data.name = get_value(div.find("h5"))
      find_div = div.find("div", {'class': 'card-text small'})
      result_text = '|'.join(line.strip() for line in find_div.stripped_strings)
      if result_text == "":
        continue
      staff_data.title = result_text.split("|")[0]
      staff_data.dept = dept
      staff_data.phone = result_text.split("|")[2] if len(result_text.split("|")) > 2 else ""
      staff_data.email = result_text.split("|")[1] if len(result_text.split("|")) > 1 else ""
      member = [school_id, school_name] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_100(url, school_id):
  soup = get_url_content(url, school_id)
  sections = soup.find_all('div', {'class': 'field-item even'})
  member_list = []
  for section in sections:
    h2s = section.find_all("h2")
    ps = section.find_all("p")
    if len(h2s) == 0:
      continue
    for index, h2 in enumerate(h2s):
      staff_data = StaffData()
      staff_data.dept = "Atheletic Staff"
      staff_data.name = get_value(h2)
      result_text = get_element_value(ps[index])
      staff_data.title = result_text.split("|")[0]
      staff_data.email = result_text.split("|")[1] if len(result_text.split("|")) > 1 else ""
      member = [school_id, "Quinsigamond Community College"] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_111(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'accordion-tab-inner'})
  member_list = []
  for div in divs:
    title_names = get_value(div.find("h3", {"class": "accordion-tab-title"}))
    staff_data = StaffData()
    staff_data.title = title_names.split(":")[0].strip()
    staff_data.name = title_names.split(":")[1].strip() if len(title_names.split(":")) > 1 else ""
    email_p = div.find("div", {"class": "accordion-tab-content"}).find("p")
    if email_p:
      staff_data.email = get_value(email_p.find("a"))
    member = [school_id, "Bunker Hill Community College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_140(url, school_name, school_id):
  soup = get_url_content(url, school_id)
  sections = soup.find_all('div', {'class': 'coach-bios-wrapper clearfix'})
  member_list = []
  for section in sections:
    dept = get_value(section.find("h1"))
    divs = section.find_all('div', {'class': 'span6'})
    if len(divs) == 0:
      continue
    for div in divs:
      staff_data = StaffData()
      p_infos = div.find("div", {'class': 'info'}).select("p")
      staff_data.name = get_value(p_infos[0])
      link_url = p_infos[0].find("a")["href"]
      if link_url:
        staff_data.link_url = urljoin(url, link_url)
      staff_data.title = get_value(p_infos[1]) if len(p_infos) > 1 else ""
      staff_data.dept = dept
      staff_data.email = get_value(p_infos[2]) if len(p_infos) > 2 else ""
      staff_data.phone = get_value(p_infos[3]).replace("Phone: ", "") if len(p_infos) > 3 else ""
      member = [school_id, school_name] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_342(url, school_id):
  soup = get_url_content(url, school_id)
  ul = soup.find('ul', {'class': 'lw_widget_results_profiles'})
  member_list = []
  for li in ul.select("li"):
    staff_data = StaffData()
    name_link = li.find("h4", {"class": "lw_profiles_name"})
    staff_data.name = get_value(name_link)
    link_url = name_link.find("a")
    if link_url:
      staff_data.link_url = urljoin(url, link_url["href"])
    staff_data.title = get_value(li.find("div", {"class": "lw_profiles_title"}))
    secondary_title = li.find("div", {"class": "lw_profiles_secondary_title"})
    if secondary_title:
      staff_data.title += " / " + get_value(secondary_title)
    staff_data.phone = get_value(li.find("a", {"class": "lw_profiles_phone"}))
    staff_data.dept = "Athletic Staff"
    email = li.find("a", {"class": "lw_profiles_email"})
    if email:
      staff_data.email = email["href"].replace("mailto:", "")
    member = [school_id, "Emory & Henry College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_448(url, school_id):
  soup = get_url_content(url, school_id)
  lis = soup.find_all('li', {'class': 'views-row'})
  member_list = []
  for li in lis:
    staff_data = StaffData()
    staff_data.name = get_value(li.find("h3"))
    staff_data.title = get_element_value(li.select_one(".contact--left p")).split("|")[0]
    staff_data.dept = "Athletic Staff"
    staff_data.email = get_value(li.find("div", {"class": "contact--email"}))
    staff_data.phone = get_value(li.find("div", {"class": "contact--phone"}))
    member = [school_id, "Pasco-Hernando State College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_463(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find('article').find_all("div", {"class": "row"})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    p_div = div.find("div", {"class": "col-md-8"})
    text = get_element_value(p_div)
    staff_data.name = text.split("|")[0]
    staff_data.title = text.split("|")[1] if len(text.split("|")) > 1 else ""
    staff_data.email = text.split("|")[2].replace("Email:", "").strip() if len(text.split("|")) > 2 else ""
    staff_data.phone = text.split("|")[3].replace("Phone:", "").strip() if len(text.split("|")) > 3 else ""
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Southern Union State Community College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_551(url, school_name, school_id):
  soup = get_url_content(url, school_id)
  parent_div = soup.find('div', {'class': 'wysiwyg__body'})
  child_elements = parent_div.find_all(recursive=False)
  member_list = []
  for element in child_elements:
    if element.name == "h3":
      dept = get_value(element)
    if element.name == "h2" and element.text == "Administration":
      dept = "Administration"
    if element.name == "p":
      text = get_element_value(element)
      staff_data = StaffData()
      staff_data.name = text.split("|")[0].strip()
      staff_data.title = text.split("|")[1] if len(text.split("|")) > 1 else ""
      staff_data.email = text.split("|")[2].replace("Email:", "").strip() if len(text.split("|")) > 2 else ""
      staff_data.phone = text.split("|")[3].replace("Phone:", "").strip() if len(text.split("|")) > 3 else ""
      staff_data.dept = dept
      if is_title(staff_data.name):
        continue
      member = [school_id, school_name] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_571(url, school_id):
  soup = get_url_content(url, school_id)
  parent_div = soup.find('div', {'class': 'staff-directory'})
  child_elements = parent_div.find_all("div", recursive=False)
  member_list = []
  for element in child_elements:
    if element.has_attr("class") and "category" in element["class"]:
      dept = get_value(element)
    if element.has_attr("class") and "member" in element["class"]:
      name_elemnet = element.find("div", {"class": "name"})
      staff_data = StaffData()
      staff_data.name = get_value(name_elemnet.find("a"))
      staff_data.link_url = urljoin(url, name_elemnet.find("a")["href"])
      staff_data.title = get_value(name_elemnet).replace(staff_data.name, "").strip()
      staff_data.phone = get_value(element.find("div", {"class": "phone"}))
      staff_data.email = get_value(element.find("div", {"class": "email"}))
      staff_data.dept = dept
      member = [school_id, "Valparaiso University"] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_604(url, school_name, school_id):
  soup = get_url_content(url, school_id)
  sections = soup.find_all('section', {'class': 'staff-directory'})
  member_list = []
  for section in sections:
    dept = get_value(section.find("h2"))
    divs = section.find_all('div', {'class': 'row no-gutters g-0 w-100'})
    if len(divs) == 0:
      continue
    print(len(divs))
    for div in divs:
      staff_data = StaffData()
      staff_data.name = get_value(div.find("h5"))
      find_div = div.find("div", {'class': 'card-text small'})
      result_text = '|'.join(line.strip() for line in find_div.stripped_strings)
      if result_text == "":
        continue
      staff_data.title = result_text.split("|")[0]
      staff_data.dept = dept
      staff_data.phone = result_text.split("|")[2] if len(result_text.split("|")) > 2 else ""
      staff_data.email = result_text.split("|")[1] if len(result_text.split("|")) > 1 else ""
      member = [school_id, school_name] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_621(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'empBlock'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("h3"))
    link_url = div.find("h3").find("a")
    if link_url:
      staff_data.link_url = urljoin(url, link_url["href"])
    staff_data.title = get_value(div.find("div", {'class': 'position'}))
    staff_data.phone = get_value(div.find("div", {'class': 'phone'}))
    staff_data.email = get_value(div.find("div", {'class': 'email'}))
    staff_data.dept = "Athletic Coaches"
    member = [school_id, "Southwestern Community College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_671(url, school_id):
  soup = get_url_content(url, school_id)
  articles = soup.find_all('article', {'class': 'directory_item'})
  member_list = []
  for article in articles:
    staff_data = StaffData()
    staff_data.name = get_value(article.find("h3"))
    link_url = article.find("h3").find("a")
    if link_url:
      staff_data.link_url = urljoin(url, link_url["href"])
    staff_data.title = get_value(article.find("span", {'class': 'directory_item_position'}))
    staff_data.email = get_value(article.find("a", {'class': 'contact_card_type_link_email'}))
    staff_data.phone = get_value(article.find("a", {'class': 'contact_card_type_link_phone'}))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Concordia College at Moorhead"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_702(url, school_id):
  soup = get_url_content(url, school_id)
  parent_div = soup.find('div', {'class': 'editable'})
  h6s = parent_div.find_all("h6")
  ps = parent_div.find_all("p")
  member_list = []
  for index, h6 in enumerate(h6s):
    staff_data = StaffData()
    staff_data.name = get_value(h6)
    text = get_element_value(ps[index])
    staff_data.title = text.split("|")[0]
    staff_data.phone = text.split("|")[1] if len(text.split("|")) > 1 else ""
    staff_data.email = text.split("|")[2] if len(text.split("|")) > 2 else ""
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Kankakee Community College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_721(url, school_id):
  soup = get_url_content(url, school_id)
  addresses = soup.find_all('address')
  member_list = []
  for address in addresses:
    staff_data = StaffData()
    staff_data.email = address.find("a")["href"].replace("mailto:", "")
    text = get_element_value(address)
    staff_data.name = text.split("|")[0]
    staff_data.title = find_title(text.split("|"))
    staff_data.phone = get_value(address.find("p", {'id': 'phone-number'}))
    staff_data.phone = re.sub(r'[\r\t\n]', '', staff_data.phone)
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Southeastern Illinois College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_769(url, school_id):
  soup = get_url_content(url, school_id)
  parent_div = soup.find('div', {'class': 'bulldog-roster-filter'})
  child_elements = parent_div.find_all(recursive=False)
  dept = ""
  member_list = []
  for element in child_elements:
    if element.name == "h2":
      dept = get_value(element)
    if element.name == "ul":
      lis = element.find_all("li")
      for li in lis:
        staff_data = StaffData()
        link_url = li.find(".filter-player-container a")
        if link_url:
          staff_data.link_url = urljoin(url, link_url["href"])
        p_div = li.find("div", {'class': 'player-name'})
        text = get_element_value(p_div)
        staff_data.name = text.split("|")[0].strip()
        staff_data.title = text.split("|")[1].strip() if len(text.split("|")) > 1 else ""
        p_div = li.find("div", {'class': 'player-header'}).find("p")
        text = get_element_value(p_div)
        staff_data.phone = text.split("|")[0].strip()
        staff_data.email = p_div.find("a", {'class': 'icon-mail u-email'})["href"].replace("mailto:", "")
        staff_data.dept = dept
        member = [school_id, "Concordia University-Nebraska"] + staff_data.to_array()
        print(member)
        member_list.append(member)
  return member_list

def crawl_script_school_789(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'person'})
  member_list = []
  for div in divs:
    text = get_element_value(div)
    staff_data = StaffData()
    staff_data.name = text.split("|")[0]
    staff_data.title = text.split("|")[1] if len(text.split("|")) > 1 else ""
    staff_data.phone = find_phone_number(text.split("|"))
    staff_data.email = find_email(text.split("|"))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Henderson State University"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_969(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'gridFourth ng-scope'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    p_info = div.select_one("p")
    staff_data.name = get_value(p_info.find("strong"))
    if is_title(staff_data.name):
      continue
    staff_data.title = get_value(p_info.find("span", {'ng-if': 'user.positions.organization1'})) + get_value(p_info.find("span", {'ng-if': 'user.positions.position1'}))
    link_url = p_info.find("span", {'ng-if': 'user.email'})
    if link_url and link_url.find("a"):
      staff_data.email = link_url.find("a")["href"].replace("mailto:", "")
    staff_data.phone = get_value(p_info.find("span", {'ng-if': 'user.phone'}))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "University of Portland"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1006(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'role': 'listitem'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("h2")).replace("Coach", "").strip()
    staff_data.title = get_value(div.select("p", {'style': 'font-size: 14px;'})[0]) 
    staff_data.phone = get_value(div.select("p", {'style': 'font-size: 14px;'})[1])
    staff_data.email = get_value(div.select("p", {'style': 'font-size: 14px;'})[2]) 
    if staff_data.name == "" or len(staff_data.name) < 4:
      continue
    staff_data.dept = "Athletic Staff"
    member = [school_id, "University of South Carolina-Salkehatchie"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1047(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'staffGroup'})
  member_list = []
  for div in divs:
    dept = get_value(div.find("h4"))
    ps = div.find_all("p")
    for p in ps:
      text = get_element_value(p)
      staff_data = StaffData()
      staff_data.name = text.split("|")[0]
      staff_data.title = text.split("|")[1] if len(text.split("|")) > 1 else ""
      link_url = p.find("a")
      if link_url:
        staff_data.link_url = urljoin(url, link_url["href"]).replace("mailto:", "")
      staff_data.dept = dept
      member = [school_id, "Roane State Community College"] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_1068(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'employee__details'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("h2"))
    staff_data.title = get_value(div.find("h3"))
    p_div = div.find("div", {'class': 'employee__details-info'})
    staff_data.phone = get_value(p_div.select_one("a"))
    staff_data.email = get_value(p_div.select("a")[1]) if len(p_div.select("a")) > 1 else ""
    remove_string = get_value(p_div.select("a")[1].find("span")) if len(p_div.select("a")) > 1 else ""
    staff_data.email = staff_data.email.replace(remove_string, "")
    staff_data.dept = "Athletic Staff"
    member = [school_id, "University of West Georgia"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1112(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'et_pb_css_mix_blend_mode_passthrough'})
  member_list = []
  for div in divs:
    dept = get_value(div.find("h3"))
    p_divs = div.find_all("div", {'class': 'abcfslTxtCntrLst'})
    for p_div in p_divs:
      staff_data = StaffData()
      staff_data.name = get_value(p_div.find("h3"))
      staff_data.title = get_value(p_div.find("div", {"class": "T-F2"}))
      if p_div.find("T-F3"):
        staff_data.title += " " + get_value(p_div.find("div", {"class": "T-F3"}))
      staff_data.phone = get_value(p_div.find("div", {"class": "LT-F4"})).replace("Office Phone", "").strip()
      if is_title(staff_data.name):
        continue
      email_link = p_div.find("div", {"class": "EM-F5"})
      if email_link and email_link.find("a"):
        staff_data.email = email_link.find("a")["href"].replace("mailto:", "")
      staff_data.dept = dept
      member = [school_id, "Bacone College"] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_1130(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('article', {'role': 'article'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("div", {"class": "views-field-title"}))
    link_url = div.find("div", {"class": "views-field-title"}).find("a")
    if link_url:
      staff_data.link_url = urljoin(url, link_url["href"])
    staff_data.title = get_value(div.find("div", {"class": "views-field-person-role"}))
    staff_data.email = get_value(div.find("div", {"class": "views-field-email"}))
    staff_data.phone = get_value(div.find("div", {"class": "views-field-phone-number"}))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Pennsylvania State University-Penn State Hazleton"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1255(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'views-row'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("div", {"class": "aProfile-name"}))
    staff_data.title = get_value(div.find("div", {"class": "aProfile-title"}))
    staff_data.email = get_value(div.find("div", {"class": "aProfile-email"}))
    staff_data.phone = get_value(div.find("div", {"class": "aProfile-phone"}))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Ohio University-Lancaster Campus"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1281(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'item-list'})
  member_list = []
  for div in divs:
    dept = get_value(div.find("h3"))
    ul = div.find("ul")
    for li in ul.select("li"):
      staff_data = StaffData()
      staff_data.title = get_value(li.find("div", {"class": "coaching-title"}))
      staff_data.name = get_value(li.find("div", {"class": "name"}))
      staff_data.dept = dept
      member = [school_id, "Manhattan Christian College"] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_1321(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'flex-grid-unit'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("div", {"class": "rtedit name"}))
    staff_data.title = get_value(div.find("div", {"class": "rtedit title"}))
    staff_data.email = get_value(div.find("div", {"class": "email"}))
    staff_data.phone = get_value(div.find("div", {"class": "phone"}))
    if staff_data.name == "":
      continue
    staff_data.dept = "Athletic Staff"
    member = [school_id, "George C Wallace State Community College-Selma"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1395(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'staff'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    text = get_element_value(div)
    staff_data.name = text.split("|")[0]
    link_url = div.select_one("a")
    if link_url:
      staff_data.link_url = urljoin(url, link_url["href"])
    staff_data.title = text.split("|")[1] if len(text.split("|")) > 1 else ""
    staff_data.email = text.split("|")[2] if len(text.split("|")) > 2 else ""
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Jackson State Community College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1439(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'team-contact team-contact--split'})
  member_list = []
  for parent_div in divs:
    dept = get_value(parent_div.find("h3"))
    divs = parent_div.find_all("div", {"class": "wysiwyg team-contact__body"})
    for div in divs:
      staff_data = StaffData()
      staff_data.name = get_value(div.find("h3"))
      link_url = div.find("h3").find("a")
      if link_url:
        staff_data.link_url = urljoin(url, link_url["href"])
      p_div = div.find("p")
      text = get_element_value(p_div)
      staff_data.title = text.split("|")[0]
      staff_data.email = find_email(text.split("|"))
      staff_data.phone = find_phone_number(text.split("|"))
      staff_data.dept = dept
      member = [school_id, "University of Redlands"] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_1463(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'elementor-image-box-content'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("h3", {"class": "elementor-image-box-title"}))
    title_email = get_value(div.find("p", {"class": "elementor-image-box-description"}))
    staff_data.email = " ".join(extract_emails(title_email))
    staff_data.title = title_email.replace(staff_data.email, "")
    staff_data.title = re.sub(r'[\r\t\n]', '', staff_data.title)
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Contra Costa College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1498(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'col-sm-6 inner-content vcard'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("span", {"class": "name"}))
    p_div = div.find("span", {"style": "font-size: 90%;"})
    text = get_element_value(p_div)
    staff_data.title = text.split("|")[0]
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    staff_data.dept = "Athletic Staff"
    staff_data.title = staff_data.title.replace(staff_data.email, "")
    member = [school_id, "Redlands Community College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1624(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'cn-list-row cn-list-item vcard individual athletics-department'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("span", {"class": "given-name"})) + " " + get_value(div.find("span", {"class": "family-name"}))
    staff_data.title = get_value(div.find("span", {"class": "title notranslate"}))
    phone_text = get_element_value(div.find("span", {"class": "tel cn-phone-number cn-phone-number-type-homephone"}))
    staff_data.phone = find_phone_number(phone_text.split("|"))
    staff_data.email = get_value(div.find("span", {"class": "email-address"}))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Glen Oaks Community College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1655(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'card'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    name_title = get_value(div.find("h3", {"class": "accordion-title"}))
    staff_data.name = name_title.split("-")[0].strip()
    staff_data.title = name_title.split("-")[1].strip()
    text = get_element_value(div.find("div", {"class": "accordion-content"}))
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Orange County Community College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1682(url, school_id):
  soup = get_url_content(url, school_id)
  parent_div = soup.find('div', {'class': 'article-text'})
  elments = parent_div.find_all(recursive=False)
  member_list = []
  dept = ""
  for element in elments:
    if element.name == "h1":
      dept = get_value(element)
    if element.name == "p":
      text = get_element_value(element)
      staff_data = StaffData()
      staff_data.name = text.split("|")[0]
      staff_data.title = text.split("|")[2] if len(text.split("|")) > 2 else ""
      link_url = element.find("a")
      if link_url:
        staff_data.link_url = urljoin(url, link_url["href"])
      staff_data.email = find_email(text.split("|"))
      staff_data.phone = find_phone_number(text.split("|"))
      staff_data.dept = dept
      member = [school_id, "Columbia Basin College"] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_1711(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'directory-card w-dyn-item'})
  member_list = []
  for div in divs:
    staff_data = StaffData() 
    staff_data.name = get_value(div.find("div", {'class': 'faculty-heading directory'}))
    staff_data.title = get_value(div.find("div", {'class': 'directory-name role'}))
    staff_data.email = get_value(div.find("div", {'class': 'directory-contact-container'}))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Champion Christian College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1817(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'employee'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("h4", {'itemprop': 'name'}))
    staff_data.title = get_value(div.find("span", {'itemprop': 'jobTitle'}))
    staff_data.email = get_value(div.find("a", {'itemprop': 'email'}))
    staff_data.phone = get_value(div.find("a", {'itemprop': 'telephone'}))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Columbia College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1838(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'profile-content'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("div", {'class': 'name'}))
    staff_data.title = get_value(div.find("div", {'class': 'title'}))
    staff_data.phone = get_value(div.find("div", {'class': 'phone'})).replace("Phone:", "").strip()
    staff_data.email = get_value(div.find("div", {'class': 'email'})).replace("Email:", "").strip()
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Western Wyoming Community College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1875(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'staff_member'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("span", {'class': 'first_name'})) + " " + get_value(div.find("span", {'class': 'last_name'}))
    staff_data.title = get_value(div.find("p", {'class': 'staff_title'}))
    p_div = div.find("ul", {'class': 'staff_contact_details'})
    if p_div:
      text = get_element_value(div.find("ul", {'class': 'staff_contact_details'}))
      staff_data.email = find_email(text.split("|"))
      staff_data.phone = find_phone_number(text.split("|"))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Central Carolina Community College"] + staff_data.to_array()// Function to set up the global query

    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1879(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'result-content'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.select_one("p"))
    staff_data.title = get_value(div.select("p")[1]) if len(div.select("p")) > 1 else ""
    staff_data.phone = get_value(div.find("p", {'ng-if': "result.phone"}))
    staff_data.email = get_value(div.find("a", {'ng-if': "result.email"}))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Johnson & Wales University-North Miami"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1884(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'vc_column-inner'})
  member_list = []
  for div in divs:
    staff_data = StaffData()

    p_div = div.find("div", {'class': 'wpb_text_column wpb_content_element'})
    if p_div:
      text_div = p_div.find("p")
      if text_div:
        text = get_element_value(text_div)
        staff_data.name = text.split("|")[0]
        staff_data.title = text.split("|")[1] if len(text.split("|")) > 1 else ""
        staff_data.email = find_email(text.split("|"))
        staff_data.phone = find_phone_number(text.split("|"))
        staff_data.dept = "Athletic Staff"
        member = [school_id, "Webb Institute"] + staff_data.to_array()
        if staff_data.title == "" or is_title(staff_data.name):
          continue
        print(member)
        member_list.append(member)
  member_list = member_list[1:]
  return member_list

def crawl_script_school_1889(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all('div', {'class': 'cn-list-row cn-list-item vcard individual faculty-staff'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    link_url = div.find("h2")
    if link_url and link_url.find("a"):
      staff_data.link_url = urljoin(url, link_url.find("a")["href"])
    staff_data.name = get_value(div.find("span", {'class': 'given-name'})) + " " + get_value(div.find("span", {'class': 'family-name'}))
    staff_data.title = get_value(div.find("span", {'class': 'title notranslate'}))
    staff_data.phone = get_value(div.find("span", {'class': 'tel cn-phone-number cn-phone-number-type-phone-extension'}))
    staff_data.email = get_value(div.find("span", {'class': 'email-address'}))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Davidson-Davie Community College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1921(url, school_id):
  soup = get_url_content(url, school_id)
  parent_div = soup.find("div", {'class': 'inner-content'})
  divs = parent_div.find_all("div", {'class': 'row'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("h4"))
    staff_data.title = get_value(div.find("h5"))
    text = get_element_value(div)
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Southern University at New Orleans"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1927(url, school_id):
  soup = get_url_content(url, school_id)
  parent_div = soup.find("div", {'class': 'snippetrow'})
  divs = parent_div.find_all("div")
  dept = ""
  member_list = []
  for div in divs:
    ps = div.find_all("p")
    for p in ps:
      staff_data = StaffData()
      dept_span = p.find("span", {'style': 'color: #7030a0;'})
      if dept_span:
        dept = get_value(dept_span)
      staff_data.name = get_value(p.find("strong")).replace(dept, "")
      text = get_element_value(p)
      staff_data.email = find_email(text.split("|"))
      staff_data.phone = find_phone_number(text.split("|"))
      ems = p.find_all("em")
      for em in ems:
        if len(get_value(em)) > 3:
          staff_data.title = get_element_value(em)
          break
      staff_data.dept = dept
      member = [school_id, "Harcum College"] + staff_data.to_array()
      if len(staff_data.name) < 4:
        continue
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_1933(url, school_id):
  member_list = []
  soup = get_url_content(url, school_id)
  dept_arr = ["Faculty", "Cabinet", "Administration", "Staff", "Resident Team", "Student Goverment", "Board of Trustees"]
  tab_div = soup.find("div", {'class': 'et_pb_all_tabs'})
  title_status = ["online", "graduate", "campus"]
  for index, tab in enumerate(tab_div.find_all("div", recursive=False)):
    team_divs = tab.find_all("div", {'class': 'team'})
    for team_div in team_divs:
      divs = team_div.find_all("div")
      for div in divs:
        staff_data = StaffData()
        staff_data.name = get_value(div.find("h2"))
        staff_data.title = get_value(div.find("h3"))
        staff_data.dept = dept_arr[index]
        member = [school_id, "Barclay College"] + staff_data.to_array()
        if staff_data.title == "" or staff_data.title.lower() in title_status:
          continue
        print(member)
        member_list.append(member)
  return member_list

def crawl_script_school_1945(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'ListCardImageOnSide-items-item'})
  member_list = []
  print(len(divs))
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("h3"))
    link_url = div.find("h3").find("a")
    if link_url:
      staff_data.link_url = urljoin(url, link_url["href"])
    text = get_element_value(div.find("div", {'class': 'PromoCardImageOnSide-description promo-description'}))
    staff_data.title = text.split("|")[0]
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Brigham Young University-Hawaii"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1954(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("article")
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("h3"))
    staff_data.title = get_value(div.find("h4"))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "New Hope Christian College-Eugene"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1999(url, school_id):
  soup = get_url_content(url, school_id)
  parent_div = soup.find("div", {"class": "module"})
  ps = parent_div.find_all("p")
  member_list = []
  for index, p_div in enumerate(ps):
    if index == 0:
      continue
    staff_data = StaffData()
    name_title = get_element_value(p_div.find("strong"))
    staff_data.name = name_title.split("|")[0]
    staff_data.title = name_title.split("|")[1] if len(name_title.split("|")) > 1 else ""
    staff_data.dept = "Athletic Staff"
    text = get_element_value(p_div)
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    member = [school_id, "Culinary Institute of America"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_2022(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'item-list'})
  member_list = []
  for div in divs:
    dept = get_value(div.find("h3"))
    ul = div.find("ul")
    for li in ul.find_all("li"):
      staff_data = StaffData()
      staff_data.name = get_value(li.find("div", {'class': 'name'}))
      staff_data.title = get_value(li.find("div", {'class': 'coaching-title'}))
      staff_data.dept = dept
      member = [school_id, "Central Christian College of the Bible"] + staff_data.to_array()
      if len(staff_data.name) < 4:
        continue
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_2025(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'col-sm-6 col-md-4 col-print-4'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("div", {'class': 'bluetxt name'}))
    staff_data.title = get_value(div.find("div", {'class': 'designation'}))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Providence University College"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_2032(url, school_id):
  soup = get_url_content(url, school_id)
  parent_div = soup.find("div", {"class": "fusion-portfolio-wrapper"})
  member_list = []
  articles = parent_div.find_all("article")
  for article in articles:
    staff_data = StaffData()
    staff_data.name = get_value(article.find("h2", {'class': 'entry-title'}))
    name_link = article.find("h2", {'class': 'entry-title'}).find("a")
    if name_link:
      staff_data.link_url = urljoin(url, name_link["href"])
    staff_data.dept = get_value(article.find("div", {'class': 'fusion-portfolio-meta'}))
    text = get_element_value(article.find("div", {'class': 'staff-details'}))
    staff_data.title = text.split("|")[0]
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    member = [school_id, "Leech Lake Tribal College"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_2045(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'et_pb_row_inner'})
  member_list = []
  for index, div in enumerate(divs):
    if index == 0:
      continue
    staff_data = StaffData()
    staff_data.name = get_value(div.find("h1"))
    staff_data.title = get_value(div.find("h2"))
    staff_data.dept = "Athletic Staff"
    text = get_element_value(div)
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    member = [school_id, "Oak Hills Christian College"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_2056(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'tableRow clearfix'})
  member_list = []
  for div in divs:
    p_divs = div.find_all("div", {'class': 'tableCell'})
    staff_data = StaffData()
    staff_data.name = get_value(p_divs[1])
    staff_data.title = get_value(p_divs[2]) if len(p_divs) > 2 else ""
    staff_data.dept = "Athletic Staff"
    staff_data.email = get_value(p_divs[3]) if len(p_divs) > 3 else ""
    staff_data.phone = get_value(p_divs[4]) if len(p_divs) > 4 else ""
    member = [school_id, "University of Maine at Fort Kent"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_2116(url, school_id):
  soup = get_url_content(url, school_id)
  parent_div = soup.find("div", {'id': 'main'})
  member_list = []
  for div in parent_div.find_all("div", {'class': 'col-md-6'}):
    staff_data = StaffData()
    text = get_element_value(div)
    staff_data.name = text.split("|")[1] if len(text.split("|")) > 1 else ""
    staff_data.title = text.split("|")[0]
    staff_data.phone = find_phone_number(text.split("|"))
    link_url = div.select_one("a")
    if link_url and "mailto:" not in link_url["href"]:
      staff_data.link_url = urljoin(url, link_url["href"])
    staff_data.dept = "Athletic Staff"
    email = div.find("a[href^=mailto]")
    if email:
      staff_data.email = email["href"].replace("mailto:", "")
    member = [school_id, "Rogue Community College"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_2132(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'col-12 col-md-6 mb-4 mb-md-10 faculty-staff-item'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("div", {"class": "faculty-staff-name"}))
    link_url = div.find("div", {"class": "faculty-staff-name"}).find("a")
    if link_url:
      staff_data.link_url = urljoin(url, link_url["href"])
    staff_data.title = get_value(div.find("div", {"class": "faculty-department"}))
    staff_data.dept = "Athletic Staff"
    staff_data.phone = get_value(div.find("div", {"class": "phone-numbers"}))
    staff_data.email = get_value(div.find("div", {"class": "faculty-email"}))
    member = [school_id, "Wytheville Community College"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_2133(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'fsConstituentItem'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("h3", {"class": "fsFullName"}))
    link_url = div.find("h3", {"class": "fsFullName"}).find("a")
    if link_url:
      staff_data.link_url = urljoin(url, link_url["href"])
    
    staff_data.title = get_value(div.find("div", {"class": "fsTitles"})).replace("Titles:", "")
    staff_data.title = re.sub(r'[\r\t\n]', '', staff_data.title).strip()
    staff_data.dept = "Athletic Staff"
    if div.find("div", {"class": "fsEmail"}):
      text = get_element_value(div.find("div", {"class": "fsEmail"}))
      staff_data.email = find_email(text.split("|"))
    if len(staff_data.name) < 4:
      continue
    member = [school_id, "Stratford University"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_2156(url, school_id):
  soup = get_url_content(url, school_id)
  address = soup.find_all("address")
  member_list = []
  for addr in address:
    staff_data = StaffData()
    staff_data.name = get_value(addr.find("strong"))
    staff_data.title = get_value(addr.find("p"))
    email = addr.find("a")
    if email:
      staff_data.email = email["href"].replace("mailto:", "")
    staff_data.dept = "Athletic Staff"
    staff_data.phone = get_value(addr.find("p", {"id": "phone-number"}))
    member = [school_id, "Carolina Christian College"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_2160(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'c-card shadow-1 hover mw300 ma3'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    staff_data.name = get_value(div.find("h2", {"class": "c-card--title mb0"}))
    text = get_element_value(div.find("div", {"class": "c-card--desc"}))
    staff_data.title = text.split("|")[0]
    staff_data.phone = find_phone_number(text.split("|"))
    staff_data.email = find_email(text.split("|"))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "National Park College"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_2168(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'panel-body'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    name_div = div.find("div", {"class": "panel-title"})
    if name_div and name_div.find("a"):
      staff_data.link_url = urljoin(url, name_div.find("a")["href"])
    staff_data.name = get_value(name_div)
    text = get_element_value(div.find("div", {"class": "panel-text"}))
    staff_data.title = text.split("|")[0]
    staff_data.dept = text.split("|")[1] if len(text.split("|")) > 1 else "Athletic Staff"
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    member = [school_id, "Virginia Peninsula Community College"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_2302(url, school_id):
  soup = get_url_content(url, school_id)
  parent_section = soup.find("section", {"class": "left-nav-main"})
  member_list = []
  for section in parent_section.find_all("section", recursive=False):
    dept = get_value(section.find("h2"))
    text = get_element_value(section.find("div", {"class": "employeeinfo"}))
    staff_data = StaffData()
    staff_data.dept = dept
    staff_data.name = text.split("|")[0]
    staff_data.title = text.split("|")[1] if len(text.split("|")) > 1 else ""
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    member = [school_id, "Spokane Community College"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_438(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {'class': 'lynn-mediaobject-body'})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    name_div = div.find("h2", {"class": "lynn-type--l lynn-text-align--left lynn-m-vertical--m"})
    if name_div and name_div.find("a"):
      link_url = name_div.find("a")
      staff_data.name = get_value(link_url)
      staff_data.link_url = urljoin(url, link_url["href"])
    staff_data.title = get_value(div.find("span", {"class": "lynn-heading-posttitle"}))
    p_div = div.find("div", {"class": "lynn-table-wrapper--scroll"})
    if p_div:
      text = get_element_value(p_div)
      staff_data.phone = find_phone_number(text.split("|"))
      staff_data.email = find_email(text.split("|"))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Lynn University"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_593(url, school_id):
  soup = get_url_content(url, school_id)
  parent_div = soup.find("table", {"class": "cols-3"})
  member_list = []
  print(len(parent_div.find_all("tr")))
  for tr in parent_div.find_all("tr"):
    tds = tr.select("td")
    if len(tds) == 0:
      continue
    staff_data = StaffData()
    text = get_element_value(tds[0])
    staff_data.name = text.split("|")[0]
    staff_data.title = get_value(tds[1]) if len(tds) > 1 else ""
    p_content = get_element_value(tds[2]) if len(tds) > 2 else ""
    staff_data.phone = find_phone_number(p_content.split("|"))
    staff_data.email = find_email(p_content.split("|"))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Henry Ford College"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_597(url, school_id):
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept": "application/json, text/plain, */*",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br",
  }
  response = requests.get(url, headers=headers)
  if response.status_code == 200 or response.status_code == 202:
    json_data = response.json()
  else:
    print("Error: ", response.status_code)
    return []
  member_list = []
  for member in json_data["data"]:
    staff_data = StaffData()
    staff_data.name = member["firstName"] + " " + member["lastName"]
    if len(member["positions"]) > 0:
      staff_data.title = member["positions"][-1]["title"].strip()
    if len(member["departments"]) > 0:
      for dept in member["departments"]:
        staff_data.dept += ", " + dept["description"]
      staff_data.dept = staff_data.dept.strip(",")
    if len(member["workPhones"]) > 0:
      staff_data.phone = member["workPhones"][0]["format"]
    if len(member["email"]) > 0:
      staff_data.email = member["email"][0]
    member = [school_id, "Mott Community College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_683(url, school_id):
  soup = get_url_content(url, school_id)
  tds = soup.find_all("td", {"class": "staffInfoCell"})
  member_list = []
  for td in tds:
    staff_data = StaffData()
    text = get_element_value(td)
    staff_data.name = text.split("|")[0]
    staff_data.title = text.split("|")[1].strip(",") if len(text.split("|")) > 1 else ""
    staff_data.phone = find_phone_number(text.split("|")).replace(" •", "")
    staff_data.email = find_email(text.split("|"))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Miles Community College"] + staff_data.to_array()
    if len(staff_data.name) < 4:
      continue
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1008(url, school_id):
  soup = get_url_content(url, school_id)
  tables = soup.find_all("table", {"class": "facultyTable"})
  member_list = []
  for table in tables:
    for index, tr in enumerate(table.select("tr")):
      if index == 0:
        continue
      staff_data = StaffData()
      name_link = tr.find("h3")
      if not name_link:
        continue
      staff_data.name = get_value(name_link)
      if name_link.find("a"):
        staff_data.link_url = urljoin(url, name_link.find("a")["href"])
      staff_data.title = get_value(tr.find("span", {"class": "title"}))
      staff_data.email = get_value(tr.find("span", {"class": "email"})).replace("Email: ", "")
      staff_data.dept = "Athletic Staff"
      staff_data.phone = get_value(tr.find("span", {"class": "phone"})).replace("Phone: ", "")
      member = [school_id, "Guilford Technical Community College"] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_1136(url, school_id):
  soup = get_url_content(url, school_id)
  parent_div = soup.find("div", {"class": "wpb_text_column wpb_content_element"})
  member_list = []
  h2s = parent_div.find_all("h2")
  ps = parent_div.find_all("p")
  for p in ps:
    if get_value(p) == "":
      ps.remove(p)
  for index, h2 in enumerate(h2s):
    staff_data = StaffData()
    staff_data.name = get_value(h2)
    text = get_element_value(ps[index])
    staff_data.title = text.split("|")[0]
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "County College of Morris"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1246(url, school_id):
  soup = get_url_content(url, school_id)
  parent_div = soup.find("table")
  member_list = []
  for tr in parent_div.select("tr"):
    staff_data = StaffData()
    staff_data.name = get_value(tr.find("h3"))
    text = get_element_value(tr.find("h4"))
    staff_data.dept = text.split("|")[0] if len(text.split("|")) > 0 else ""
    staff_data.title = text.split("|")[-1]
    p_text = get_element_value(tr.find("p"))
    staff_data.email = find_email(p_text.split("|"))
    staff_data.phone = find_phone_number(p_text.split("|"))
    member = [school_id, "East Georgia State College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1697(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {"class": "single-portfolio"})
  member_list = []
  for div in divs:
    text = get_element_value(div.find("div", {"class": "col-lg-2 col-md-2 col-sm-2 col-xs-12 text-right"}))
    staff_data = StaffData()
    staff_data.name = text.split("|")[0]
    staff_data.title = text.split("|")[1] if len(text.split("|")) > 1 else ""
    text = get_element_value(div)
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Caldwell Community College and Technical Institute"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_1776(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {"class": "small-12 medium-6 large-6 columns"})
  member_list = []
  for div in divs:
    for p in div.select("p"):
      text = get_element_value(p)
      staff_data = StaffData()
      staff_data.name = text.split("|")[0]
      staff_data.title = text.split("|")[1] if len(text.split("|")) > 1 else ""
      staff_data.phone = find_phone_number(text.split("|"))
      staff_data.email = find_email(text.split("|"))
      staff_data.dept = "Athletic Staff"
      member = [school_id, "Oakland Community College"] + staff_data.to_array()
      print(member)
      member_list.append(member)
  return member_list

def crawl_script_school_2028(url, school_id):
  soup = get_url_content(url, school_id)
  table = soup.find("table")
  member_list = []
  for tr in table.select("tr"):
    text = get_element_value(tr)
    staff_data = StaffData()
    staff_data.title = text.split("|")[0]
    staff_data.name = text.split("|")[1]
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    staff_data.dept = "Athletic Staff"
    member = [school_id, "Merritt College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_2046(url, school_id):
  soup = get_url_content(url, school_id)
  divs = soup.find_all("div", {"class": "personnel-card"})
  member_list = []
  for div in divs:
    staff_data = StaffData()
    name_link = div.find("h3")
    staff_data.name = get_value(name_link)
    link_url = name_link.find("a")
    if link_url:
      staff_data.link_url = urljoin(url, link_url.get("href"))
    staff_data.dept = "Athletic Staff"
    staff_data.title = get_value(div.select_one("p")) + " / " + get_value(div.select("p")[1]) if len(div.select("p")) > 1 else ""
    text = get_element_value(div)
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    member = [school_id, "Union College-NE"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_2182(url, school_id):
  soup = get_url_content(url, school_id)
  table = soup.find("table", {"id": "wpdtSimpleTable-4"})
  member_list = []
  for td in table.select("td"):
    text = get_element_value(td)
    staff_data = StaffData()
    staff_data.dept = get_value(td.select_one("h3"))
    staff_data.name = get_value(td.select("h3")[1]) if len(td.select("h3")) > 1 else ""
    staff_data.email = find_email(text.split("|"))
    staff_data.phone = find_phone_number(text.split("|"))
    staff_data.title = "Head Coach"
    member = [school_id, "University of Arkansas Community College at Morrilton"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def crawl_script_school_722(url, school_id):
  soup = get_url_content(url, school_id)
  table = soup.find("table", {"aria-label": "Employee Directory"})
  member_list = []
  for tr in table.select("tr"):
    staff_data = StaffData()
    tds = tr.select("td")
    if len(tds) == 0:
      continue
    staff_data.name = get_value(tds[0]) + " " + get_value(tds[1])
    staff_data.phone = "Ext." + get_value(tds[2])
    staff_data.email = get_value(tds[3])
    staff_data.dept = "Athletic Staff"
    staff_data.title = get_value(tds[5])
    member = [school_id, "Barton Community College"] + staff_data.to_array()
    print(member)
    member_list.append(member)
  return member_list

def save_to_excel(school_id):
  member_list = []
  member_list = crawl_script_school_604("https://milliganbuffs.com/information/directory/index", "Milligan College", school_id)
  if len(member_list) > 0:
    final_columns = ["school_id", "school_name", "dept", "name", "link_url", "title", "phone", "email", "twitter"]
    print(f"Total Members: {len(member_list)}")
    member_df = pd.DataFrame(member_list, columns=final_columns)
    member_df.to_excel("school_" + str(school_id) + ".xlsx", index=False)
  else:
    print("No Data Found!")

save_to_excel(484)