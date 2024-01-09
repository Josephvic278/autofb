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
user_id = "186932934202197"
fb_access_token = "EAAaoVZBbk8OQBO2QNGecW1YNoMHbLiufXyUMQKhtFxQ48N5ehy3Bo1xiphT35ZB5ndVfHkjTlPvapSqZAoMfGHjcbM0JCAp4MSSuCZCyf5TadHitAZCGdLpmwf4ETQp9pxJuYdkMz2eGfzZCKrGVZArnYUGmreZARjFQCG9P28h8SZB6OoPH5G7VrN1Xins4w2iYRZAbdJBEb3GqNZAPHheZAgZDZD"
manchesterCityNewsUrl = "https://www.manchestercity.news/"

fb_post_header = {
        "Content-Type" : "application/json"
    }

def format_headline(headline):
    format_headline_u = headline.lower()

def soup_data(url):
      r = requests.get(url)
      soup = BeautifulSoup(r.content, 'html.parser')      
      return soup

def get_access_token():
    get_token = requests.get(f"https://graph.facebook.com/{user_id}/accounts?access_token={fb_access_token}").json()["data"][0]["access_token"]
    
    return get_token
                  
def cut_sentence(sentence):
    
    cut_sentence = None
    result = re.search(r'^.*?\.', sentence)
    if result:
        cut_sentence = result.group(0)
        
    return cut_sentence

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
    new_access_token = get_access_token()
    post_data = {
        "access_token" : new_access_token,
        "message" : headline+" #mancity",
        "url" : banner_image
    }
    
    headline_data = {
        "headline" : headline,
        "banner_image" : banner_image       
    }
    
    db = read_db()
    if headline_data not in db["posted"]:
        db["posted"].append(headline_data)
        
        postHeadline = requests.post(url=f"{fb_post_url}/{fb_pageid}/photos", headers = fb_post_header, data = post_data)
        
        with open(json_path, "w") as write_file:
            json.dump(db, write_file)                    
    
        if postHeadline.status_code == 200:
            print(postHeadline.json())
        else:
            print(postHeadline.json())
            
    print(headline_data)

def post_article(article_list):
    
    db = read_db()
    for get_article in article_list:
        if get_article not in db["posted"]:
            
            for content_data , photo_data in get_article.items():
                content = content_data
                photo = photo_data
                
            new_access_token = get_access_token()
            post_data = {
                "access_token" : new_access_token,
                "message" : content+" #mancity",
                "url" :  photo
            }
            
            postArticle = requests.post(url = f"{fb_post_url}/{fb_pageid}/photos", headers = fb_post_header, data=post_data)
            print(postArticle.json())
            if postArticle.status_code == 200:
                postArticle.json()
                
                db["posted"].append(get_article)
                with open(json_path, 'w') as write_db:
                    json.dump(db, write_db)
                    
            else:
                postArticle.json()
            
            #postArticle = requests.post(url=f"{fb_post_url}/{fb_pageid}/photos", headers = fb_post_header, data=post_data)
    
def get_articles():
    soup = soup_data(manchesterCityNewsUrl)
    content_article = None
    content_image = None
    
    db = read_db()
    articles_data = []
    
    get_articles = soup.find_all('article', class_ = 'article')
    for article in get_articles:        
        article_content = article.find('div', class_ = 'article-content').find('div', class_='article-excerpt')
        
        if article_content!= None:
            content = article_content.find('p')
            content_article = cut_sentence(content.text)
            if content_article!=None and len(content_article)>20:                
                article_image = article.find('div', class_ = 'article-image').find('a')
                content_image = article_image.find('img').get('src')
            
                #print (content_article, content_image)
                #print("...")
            
                articles_data.append({content_article:content_image})
        
        #print(article_content)
    post_article(articles_data)
    return articles_data
    #print(get_articles)
    
schedule.every(30).minutes.do(post_headline)
schedule.every(1).minute.do(get_articles)
while True:
    schedule.run_pending()