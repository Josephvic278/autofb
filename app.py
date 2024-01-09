import requests
from bs4 import BeautifulSoup
import os
import json
import re
import schedule , time

json_path = os.getcwd()+"/database.json"

def read_db():
    with open(json_path, "r") as read_file:
        db = json.load(read_file)
    return db
    
fb_url = "https://graph.facebook.com/"
fb_post_url = "https://graph.facebook.com/v18.0/"
fb_pageid = "178991528619934"
fb_access_token = "EAAaoVZBbk8OQBOzD0VjtABtbZABewOiMqUld9t9l0ZB5uUlZC63JlGa4Dz9ZBhqZA9VbPH7v5euFkbNmJHkSiHrSEA8BRPphbXfvfAYAZAv3iMqK8G0rkaZAlRZCgaQfe99ddYMBsYICzVj0yhitteammN8ZB33pnnN7n3K9SZCZBR92hWUV7ByQ1JWY6lYe8NRZA1etqZCM6Ci2zHpHFNyCBofypdwCzj"
manchesterCityNewsUrl = "https://www.manchestercity.news/"
def format_headline(headline):
    format_headline_u = headline.lower()

def soup_data(url):
      r = requests.get(url)
      soup = BeautifulSoup(r.content, 'html.parser')      
      return soup

def extract_link(link):
    link_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    match = link_pattern.search(link)
    
    if match:
      return match.group()
      
def post_headline():
    soup = soup_data(manchesterCityNewsUrl)
    headline = None
    url = None
    banner_image = None
    headline_data = {}
    
    headline_a = soup.find('div', class_ = 'banner-title')
    headline_data = headline_a.find_all('a')
    str_link = str(headline_data[0])
    url = extract_link(str_link)
    
    for headline in headline_data[0]:
        headline = headline.text    
    
    for url in headline_data:
        url = url.get('href')
        
    banner_img = soup.find('a', class_ = 'banner-image')
    banner_image_data = banner_img.find_all('img')
    
    for get_img in banner_image_data:
        banner_image = get_img.get('src')
    
    getHeadlineDetail = soup_data(url)
    hd = getHeadlineDetail.find('div', id = 'page').find('div', class_ = 'content').find('main').find('article').find_all('h2')
    print(hd)
    
    postHeadlineHeader = {
        "Content-Type" : "application/json"
    }
    
    post_data = {
        "access_token" : fb_access_token,
        "message" : headline,
        "url" : banner_image
    }
    
    headline_data = {
        "headline" : headline,
        "banner_image" : banner_image       
    }
    
    db = read_db()
    if headline_data not in db["posted"]:
        db["posted"].append(headline_data)
        
        postHeadline = requests.post(url=f"{fb_post_url}/{fb_pageid}/photos", headers = postHeadlineHeader, data = post_data)
        
        with open(json_path, "w") as write_file:
            json.dump(db, write_file)                    
    
        if postHeadline.status_code == 200:
            print(postHeadline.json())
        else:
            print(postHeadline.json())
            
    print(headline_data)

schedule.every(30).minutes.do(post_headline)

while True:
    schedule.run_pending()