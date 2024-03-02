import requests
from bs4 import BeautifulSoup
import os
import json
import re
import schedule , time
#import ai21

json_path = os.getcwd()+"/database.json"
access_token_path = os.getcwd()+"/access_token.txt"

def read_db():
    with open(json_path, "r") as read_file:
        db = json.load(read_file)
    return db

sum_url = "https://api.apyhub.com/ai/summarize-url" 
fb_url = "https://graph.facebook.com/"
fb_post_url = "https://graph.facebook.com/v18.0/"
fb_pageid = "178991528619934"
user_id = "186932934202197"
ai21_api = "5ms71gHrJ8u9JOyjiAnpqoB6AcseeLDC"
fb_access_token = "EAAaoVZBbk8OQBO2QNGecW1YNoMHbLiufXyUMQKhtFxQ48N5ehy3Bo1xiphT35ZB5ndVfHkjTlPvapSqZAoMfGHjcbM0JCAp4MSSuCZCyf5TadHitAZCGdLpmwf4ETQp9pxJuYdkMz2eGfzZCKrGVZArnYUGmreZARjFQCG9P28h8SZB6OoPH5G7VrN1Xins4w2iYRZAbdJBEb3GqNZAPHheZAgZDZD"
manchesterCityNewsUrl = "https://www.manchestercity.news/"

fb_post_header = {
        "Content-Type" : "application/json"
    }

def summarise_article(url):
    payload = {
    "url": url
    }
    headers = {
    'apy-token': "APY0v5n80CH5uKwtKKntcsZb601G87bsLt0mnlyZhRuODBIwUw0SsitjL9Rba1glzs",
    'Content-Type': "application/json"
    }

    response = requests.post(sum_url, json=payload,headers=headers).json()["data"]["summary"]

    #print(response.text)
    
    return response
    
def format_headline(headline):
    format_headline_u = headline.lower()

def soup_data(url):
      r = requests.get(url)
      soup = BeautifulSoup(r.content, 'html.parser')      
      return soup

def exchange_token():
    access_token = None
    with open(access_token_path, "r") as read_prev_token:
        access_token = read_prev_token.read()
    
    return access_token

def get_access_token():
    access_token = exchange_token()
    #print (access_token)
    
    user_access_token = requests.get(f"https://graph.facebook.com/v18.0/oauth/access_token? grant_type=fb_exchange_token& client_id=1873945349648612& client_secret=55bba1eeeb0d144e74093c05d8c09010& fb_exchange_token={access_token}").json()
    #print(user_access_token)
    
    with open(access_token_path, "w") as write_token:
        write_token.write(str(user_access_token["access_token"]))
    
    get_token = requests.get(f"https://graph.facebook.com/{user_id}/accounts?access_token={user_access_token}").json()
    
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

def post_article(article_list, article_summary_list):
    
    db = read_db()
    article_count = 0
    for get_article in article_list:
        
        article_summary = article_summary_list[article_count]
        article_count+=1
        if get_article not in db["posted"]:
            
            for content_data , photo_data in get_article.items():
                content = content_data
                photo = photo_data
                
            new_access_token = get_access_token()
            post_data = {
                "access_token" : new_access_token,
                "message" : f"{content} /n{article_summary} /n#mancity",
                "url" :  photo
            }
            
            postArticle = requests.post(url = f"{fb_post_url}/{fb_pageid}/photos", headers = fb_post_header, data=post_data)
            #print(postArticle.json())
            if postArticle.status_code == 200:
                print(postArticle.json())
                
                db["posted"].append(get_article)
                with open(json_path, 'w') as write_db:
                    json.dump(db, write_db)
                    
            else:
                print(postArticle.json())
            
            #postArticle = requests.post(url=f"{fb_post_url}/{fb_pageid}/photos", headers = fb_post_header, data=post_data)
    
def get_articles():
    soup = soup_data(manchesterCityNewsUrl)
    content_article = None
    content_image = None
    
    db = read_db()
    articles_data = []
    articles_list = []
    
    get_articles = soup.find_all('article', class_ = 'article')
    for article in get_articles:        
        article_content = article.find('div', class_ = 'article-content').find('div', class_='article-excerpt')
        articles_url = article.find('div', class_ = 'article-content').find('a').get('href')
        
        if article_content!= None:
            content = article_content.find('p')
            content_article = cut_sentence(content.text)         
                                                                  
            if content_article!=None and len(content_article)>20:
                article_summary = summarise_article(str(articles_url))
                #time.sleep(10)
                articles_list.append(article_summary)        
                #print (articles_url)
                     
                article_image = article.find('div', class_ = 'article-image').find('a')
                content_image = article_image.find('img').get('src')
            
                #print (content_article, content_image)
                #print("...")
            
                articles_data.append({content_article:content_image})
        
        #print(article_content)
    post_article(articles_data, articles_list)
    return articles_data
    #print(get_articles)
    
schedule.every(30).minutes.do(post_headline)
schedule.every(5).seconds.do(get_articles)

#print (get_access_token())
while True:
    schedule.run_pending()