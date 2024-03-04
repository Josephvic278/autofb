import requests, json, os, time
from bs4 import BeautifulSoup

base_url = "https://www.manchestercity.news/"
fb_app_id = '1873945349648612'
fb_app_secret = '55bba1eeeb0d144e74093c05d8c09010'
fb_page_id = '178991528619934'

def get_article_img(url):
    responce = requests.get(url)

    soup = BeautifulSoup(responce.content, 'html5lib')
    image_url = soup.find('div', attrs={'class','banner-image'}).find('img').get('src')

    return image_url

def get_articles_data():
    articles_data = []

    base_responce = requests.get(base_url)
    soup = BeautifulSoup(base_responce.content, 'html5lib')

    get_aricle_class = soup.find_all('article', attrs={'class':'article'})

    for sort_url in get_aricle_class:
        get_url = sort_url.find('a')
        author = sort_url.find('div', attrs={'class','post-meta post-author'}).find('a').text
        url = get_url.get('href')
        image = get_article_img(url)

        articles_data.append({
            'url':url,
            'author':author,
            'image':image
        })
    
    return articles_data
        
def summarized_article():
    articles = [

    ]
    ai21_summarise_url = "https://api.ai21.com/studio/v1/summarize-by-segment"
    aricles_data = get_articles_data()
    ai21_apikey = '5ms71gHrJ8u9JOyjiAnpqoB6AcseeLDC'

    for get_url_data in aricles_data:
        ai21_payload = json.dumps(
            {
                "sourceType": "URL",
                "source": get_url_data['url']
            }
        )

        ai21_headers = {
            'Authorization': f'bearer {ai21_apikey}',
            'Content-Type': 'application/json'
        }

        ai21_responce = requests.post(ai21_summarise_url, headers=ai21_headers, data=ai21_payload)

        if ai21_responce.status_code == 200:
            summary_data = ai21_responce.json()
            if summary_data['segments'][0]['highlights'] != []:
                article = summary_data['segments'][0]['highlights'][0]['text']
                article_image = get_url_data['image']
                author = get_url_data['author']
                
                articles.append({'article': article, 'image': article_image, 'author': author})
            else:
                continue
        
        else:
            print(ai21_responce.json())

    return articles

def get_long_lived_uat():
    tokens_path = os.path.dirname(os.path.abspath(__file__))+'\\tokens.json'

    with open(tokens_path, 'r') as json_file:
        tokens_json = json.load(json_file)
        
        if tokens_json['long_lived_uat']!=[]:
            long_lived_uat = tokens_json['long_lived_uat']
            responce = requests.get(
        f"https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id={fb_app_id}&client_secret={fb_app_secret}&fb_exchange_token={long_lived_uat}"
        )
            if responce.status_code == 200:
                new_uat = responce.json()['access_token']

                tokens_json['long_lived_uat'] = new_uat

                with open(tokens_path, 'w') as write_token:
                    json.dump(tokens_json, write_token)

                    return new_uat
            else:
                print('error retrieving long lived user access token', responce.json())
        else:
            print('error in access token file')

def get_long_lived_pat():
    tokens_path = os.path.dirname(os.path.abspath(__file__))+'\\tokens.json'

    with open(tokens_path, 'r') as tokens_file:
        tokens_json = json.load(tokens_file)
        long_lived_uat = get_long_lived_uat()

        if tokens_json['long_lived_pat'] != []:
            responce = requests.get(f"https://graph.facebook.com/v19.0/186932934202197/accounts?access_token={long_lived_uat}")
            if responce.status_code == 200:
                new_long_lived_pat = responce.json()['data'][1]['access_token']

                tokens_json['long_lived_pat'] = new_long_lived_pat
                with open(tokens_path, 'w') as write_token:
                    json.dump(tokens_json, write_token)


                    return new_long_lived_pat
            else:
                print('error retrieving long lived page access token', responce.json())

def post_articles():
    db_path = os.path.dirname(os.path.abspath(__file__))+r"\db.json"

    post_feed_url = f'https://graph.facebook.com/v18.0/{fb_page_id}/photos'
    post_feed_header = {
        'Content-Type': 'application/json'
    }
    with open(db_path, 'r') as open_db:
        article_data = summarized_article()
        db_data = json.load(open_db)

        for confirm_post in article_data:
            if confirm_post['image'] not in db_data:               
                data = {
                    'access_token': get_long_lived_pat(),
                    'message': f"{confirm_post['article']}\n\n{confirm_post['author']}",
                    'url': confirm_post['image']
                }
                print(confirm_post['article'])
                responce = requests.post(url=post_feed_url, headers=post_feed_header, data=data)
                if responce.status_code == 200:
                    print(responce.json())

                    db_data.append(confirm_post['image'])
                    with open(db_path, 'w') as write_db:
                        json.dump(db_data, write_db)
                        time.sleep(1)
                else:
                    print('error in making feed post', responce.json())