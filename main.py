from constans import SCROLL_PAUSE, URL, MONTH_DICT, CWD, AUTHOR_NAMES
from database import Database, Author, Article
from exceptions import EndOfPageException
from selenium import webdriver, common
from datetime import date, datetime
from bs4 import BeautifulSoup
import requests
import random
import sqlite3
import time
import lxml
import os

'''Web scraping from https://www.madbarz.com/blog'''

class Manager:
    """Manager for controlling the process"""

    def __init__(self):
        self.db = Database("calisthenics_articles.db")

    @staticmethod
    def check_date() -> date:
        """Checking current date"""

        return datetime.date(datetime.now())


    @staticmethod
    def get_author_name() -> str:
        """Unfortunately articles don't have authors, but for the needs
            I've made some random names table."""

        return random.choice(AUTHOR_NAMES)

    @staticmethod
    def reformat_date(article_date) -> str:
        """Making date format friendly to datetime library"""

        article_date = article_date.replace(",", "").replace("\n", "")
        month, day, year = article_date.split(" ")
        month = MONTH_DICT[month]
        new_date_format = f"{year}-{month}-{day}"
        return new_date_format

    def start_scraping(self) -> None:
        self.start_page_scrolling()

    def start_page_scrolling(self) -> None:
        """Madbarz has dynamic site, we need first scroll all over to the end"""

        driver = webdriver.Chrome(CWD + "/chromedriver.exe")
        driver.implicitly_wait(30)
        driver.get(URL)
        try:
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                last_height = self.scroll_down(driver, last_height)

        except EndOfPageException:
            main_blog_site_parser = BeautifulSoup(driver.page_source, "lxml")
            self.get_article_link(main_blog_site_parser)

        except common.exceptions.JavascriptException:
            print("JS command error!")

        finally:
            driver.quit()

    @staticmethod
    def scroll_down(driver, curr_height) -> int:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == curr_height:
            raise EndOfPageException

        return new_height

    def get_article_link(self, main_blog_parser) -> None:
        """Getting direct article links """

        for article in main_blog_parser.find_all('article', class_="blog__post"):
            blog_class = article.find(class_="blog__post--content")
            article_link = blog_class.find('a').get('href')
            article_link_list = article_link.split("/")[2:]
            article_link = URL + "/".join(article_link_list)
            link_request = requests.get(article_link).text
            article_parser = BeautifulSoup(link_request, 'lxml')
            self.get_article_info(article_parser)

    def get_article_info(self, article_parser) -> None:
        category_list = []
        date_added = article_parser.find(class_='date').text
        date_added = self.reformat_date(date_added)
        title = article_parser.find(class_="blog__single--title").text
        print(title)
        article_category = article_parser.find('div', class_="blog__single-category")
        for hrefs in article_category.find_all("a"):
            category_list.append(hrefs)
        article_category = category_list[1].text
        content = article_parser.find('div', id="blog_content").text
        author_name = self.get_author_name()
        author_check = self.db.get_author_id(author_name)
        self.check_author_id_or_add_to_base_new_one(author_check, author_name)




    def check_author_id_or_add_to_base_new_one(self, author_check, author_name):
        if not author_check:
            self.db.insert_author_to_db(author_name)
            author_id = self.db.get_author_id(author_name)
            return author_id

        return author_check

        pass
        # print(title)
        # print(article_category)
        # print(author_name)
        # print(date_added)
        # print(content)





        # # TODO sprawdź datę i pobieraj tylko najnowsze do bazy



def main():
    executor = Manager()
    # start.start_scraping()
    # executor.db.insert_author_to_db("fiut")
    print(executor.db.get_author_id("kuku"))
    # print(executor.check_author_id_or_add_to_base_new_one(False,"seba"))
if __name__ == "__main__":
    main()
