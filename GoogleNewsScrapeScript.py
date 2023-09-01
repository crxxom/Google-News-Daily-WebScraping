from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from bs4 import BeautifulSoup
import requests
import re
import os
import sys
import pandas as pd
from datetime import datetime
from interruptingcow import timeout

# --------------------------------------------------------------- #
# Selenium scroll and get full page source

service = Service() # temporary fix to 114v+ bug

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")

driver = webdriver.Chrome(service=service, options=options)

driver.get('https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen')

i = 0
scroll_pause_time = 2  # Pause between each scroll
screen_height = driver.execute_script("return document.body.scrollHeight;")
while True:
    # Scroll down
    driver.execute_script(f"window.scrollTo(0, {screen_height});")
    i += 1
    time.sleep(scroll_pause_time)

    # Check if reaching the end of the page
    scroll_height = driver.execute_script("return document.body.scrollHeight;")
    if screen_height == scroll_height:
        break
    screen_height = scroll_height
    if i == 20: # safety break
        break

# Fetch the data using BeautifulSoup after all data is loaded
news_page = BeautifulSoup(driver.page_source, "html.parser")
# Process and save the data as needed

# Close the WebDriver session
driver.quit()

# --------------------------------------------------------------- #

# --------------------------------------------------------------- #
# scrape relevant data from page source using GoogleNews_Article Class Object

class GoogleNews_Article:
    def __init__(self, html):
        self.html = html
        self.title = self.get_title()
        self.publisher = self.get_publisher()
        self.link = self.get_link()
        self.datetime = self.get_publish_time()
        self.content = self.get_content()
        
    def __repr__(self): 
        return self.title + ' | ' + self.datetime + ' | ' + self.publisher
    
    def get_title(self): # from the google news page, scrape the title
        try:
            title = self.html.find('h4').text
        except:
            return None
        return title
 
    def get_publisher(self): # from the google news page, scrape the publisher
        try:
            publisher = self.html.find('div',{'class': 'vr1PYe'}).text
        except:
            return None
        return publisher
    
    def get_link(self): # from the google news page, scrape the link
        try:
            link = 'https://news.google.com/' + (self.html.find('a', {'class': 'WwrzSb'}).get('href'))[2:]
        except:
            return None
        return link
    
    def get_publish_time(self): # from the google news page, scrape the datetime
        try:
            datetime = self.html.find('time').get('datetime')
        except:
            return None
        return datetime
        
    def get_content(self): # redirect to the actual news article website and scrape all the p tag
        response = requests.get(self.link).text
        doc = BeautifulSoup(response, 'html.parser')
        try:
            text_collections = []
            p_tags = doc.find_all('p')
            for p in p_tags:
                text_collections.append(p.text)
            text = ' '.join(text_collections)
            cleaned_text = re.sub('\n', '', text) # remove '\n'
            cleaned_text = re.sub('\s+', ' ', cleaned_text) # remove extra space
            
        except:
            return None
        return cleaned_text
        
    def return_dict(self): # call this function to get dictionary object of the article
        dict_object = {
            'Title': self.title,
            'Publisher': self.publisher,
            'DateTime': self.datetime,
            'Link': self.link,
            'Text': self.content,
        }
        return dict_object
    
# --------------------------------------------------------------- #

# --------------------------------------------------------------- #
# scrape the info and store results in all_articles page
all_articles = []
for article_html in news_page.find_all('article'):
    try:
        with timeout(20, exception=RuntimeError):
            article = GoogleNews_Article(article_html)
            print(article)
            all_articles.append(article.return_dict())
    except RuntimeError:
        continue

application_path = os.path.dirname(sys.executable)

now = datetime.now()
month_day_year = now.strftime("%m%d%Y")

df_articles = pd.DataFrame(all_articles)
file_name = f'../News/GoogleWorldNews_{month_day_year}.csv'
final_path = os.path.join(application_path, file_name)
try: # if you are running an exe locally
    df_articles.to_csv(final_path, index=False)
except: # if you are running the py script directly
    df_articles.to_csv(f"News/GoogleWorldNews_{month_day_year}.csv", index=False)