from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from bs4 import BeautifulSoup
import requests
# import re
import os
import sys
import pandas as pd
from datetime import datetime
import logging


stdout_file = "/Users/jadonng/Desktop/Computer_Science/Data_Scraping/Google_News/stdout.log"
logging.basicConfig(filename=stdout_file, level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')

error_file = "/Users/jadonng/Desktop/Computer_Science/Data_Scraping/Google_News/stderror.log"
logging.basicConfig(filename=error_file, level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] %(message)s')

totalNumArticle = 0

TOPICS = {
    'Headlines': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen',
    'WorldWide': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen', 
    'Business': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen', 
    'Technology': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen', 
    'Entertainment': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen', 
    'Sports': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen', 
    'Science': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen', 
    'Health': 'https://news.google.com/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ?hl=en-US&gl=US&ceid=US%3Aen',
}
# --------------------------------------------------------------- #
# Selenium scroll and get full page source
for cur_topic, topic_link in TOPICS.items():
    try: 
        service = Service() # temporary fix to 114v+ bug

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")

        driver = webdriver.Chrome(service=service, options=options)

        driver.get(topic_link)

        # scroll down to bottom to grab all dynamically loaded data
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

            def __repr__(self): 
                return self.title + ' | ' + self.datetime + ' | ' + self.publisher

            def get_title(self): # from the google news page, scrape the title
                try:
                    title = self.html.find('a',{'class':'gPFEn'}).text
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

        #     def get_content(self): # redirect to the actual news article website and scrape all the p tag
        #         response = requests.get(self.link).text
        #         doc = BeautifulSoup(response, 'html.parser')
        #         try:
        #             text_collections = []
        #             p_tags = doc.find_all('p')
        #             for p in p_tags:
        #                 text_collections.append(p.text)
        #             text = ' '.join(text_collections)
        #             cleaned_text = re.sub('\n', '', text) # remove '\n'
        #             cleaned_text = re.sub('\s+', ' ', cleaned_text) # remove extra space

        #         except:
        #             return None
        #         return cleaned_text

            def return_dict(self): # call this function to get dictionary object of the article
                dict_object = {
                    'Title': self.title,
                    'Publisher': self.publisher,
                    'DateTime': self.datetime,
                    'Link': self.link,
                }
                return dict_object

        # --------------------------------------------------------------- #

        # --------------------------------------------------------------- #
        # scrape the info and store results in all_articles page
        all_articles = []
        for article_html in news_page.find_all('article'):
            try:
                article = GoogleNews_Article(article_html)
                all_articles.append(article.return_dict())
            except RuntimeError:
                continue
        
        totalNumArticle += len(all_articles)
        
        application_path = os.path.dirname(sys.executable)

        now = datetime.now()
        month_day_year = now.strftime("%m%d%Y")

        logging.info(f"{cur_topic}_{month_day_year}: Scraped {len(all_articles)} articles")

        os.chdir('/Users/jadonng/Desktop/Computer_Science/Data_Scraping/Google_News')
        df_articles = pd.DataFrame(all_articles)
        # file_name = f'{cur_topic}_{month_day_year}.csv'
        # final_path = os.path.join(application_path, file_name)
        try: 
            df_articles.to_csv(f'News/{cur_topic}_{month_day_year}.csv', index=False)
            logging.info(f"{cur_topic}_{month_day_year}: Successfully saved")

        except: 
            logging.error(f'Error in saving News/{cur_topic}_{month_day_year}.csv')
        
    except Exception as e:
        logging.error(str(e))

        
logging.info(f"Scraped a total of {totalNumArticle}")
