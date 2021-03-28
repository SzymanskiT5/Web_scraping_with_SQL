from datetime import date, datetime
from dataclasses import dataclass
from selenium import webdriver
from database import Database
from bs4 import BeautifulSoup
from constans import SCROLL_PAUSE, URL, MONTH_DICT, CWD
import requests
import random
import sqlite3
import time
import lxml
import os

'''Web scraping from https://www.madbarz.com/blog, 
unfortunately articles don't have authors, but for the needs
I've made some random names table.'''


class Manager:

    def __init__(self):
        self.db = Database("calisthenics_articles.db")
        self.author_names = ["John", "Anna", "Robert", "Matthew", "George", "Kamil"]

    def check_date(self):
        return datetime.date(datetime.now())

    def get_author_name(self):
        return random.choice(self.author_names)

    def reformat_date(self, date):

        date = date.replace(",", "")
        date = date.replace("\n", "")
        month, day, year = date.split(" ")
        month = MONTH_DICT[month]
        new_date_format = f"{year}-{month}-{day}"
        return new_date_format


    def start_page_scrolling(self):
        '''Madbarz has dynamic site, we need first scroll all over to the end'''
        driver = webdriver.Chrome(CWD + "/chromedriver.exe")

        try:
            driver.implicitly_wait(30)
            driver.get(URL)

            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(SCROLL_PAUSE)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                self.get_info_from_site(driver.page_source)

        finally:
            driver.quit()


    def get_info_from_site(self, selenium_driver):
        main_blog_site_parser = BeautifulSoup(selenium_driver, "lxml")

        for article in main_blog_site_parser.find_all('article', class_="blog__post"):
            category_list = []
            blog_class = article.find(class_="blog__post--content")
            article_link = blog_class.find('a').get('href')
            article_link_list = article_link.split("/")[2:]
            article_link = URL + "/".join(article_link_list)
            link_request = requests.get(article_link).text
            article_parser = BeautifulSoup(link_request, 'lxml')
            date_added = article_parser.find(class_='date').text
            date_added = self.reformat_date(date_added)
            title = article_parser.find(class_="blog__single--title").text
            article_category = article_parser.find('div', class_="blog__single-category")
            for hrefs in article_category.find_all("a"):
                category_list.append(hrefs)
            article_category = category_list[1].text
            content = article_parser.find('div', id="blog_content").text
            author_name = self.get_author_name()
            author_check = self.db.author_id_query(author_name)
            if author_check is False:
                self.db.insert_author_to_db(author_name)
            else:
                print(f"mam : {author_name}")

    def start_scraping(self):
        self.start_page_scrolling()



        # # TODO sprawdź datę i pobieraj tylko najnowsze do bazy


@dataclass
class Author:
    name: str


@dataclass
class Article:
    tittle: str
    date: date
    content: str
    category: str
    author_id: int


def main():
    start = Manager()
    # start.start_scraping()
    # data.author_id_query("kuku"))
    # print(start.db.authors_info())
    # data = start.db
    #
    #


if __name__ == "__main__":
    main()
