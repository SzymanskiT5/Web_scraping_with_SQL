from dataclasses import dataclass
from constants import SCROLL_PAUSE, URL, MONTH_DICT, CWD, AUTHOR_NAMES
from database import Database
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


class Handler:
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
    def reformat_date(article_date) -> date:
        """Making date format friendly to datetime library"""

        article_date = article_date.replace(",", "").replace("\n", "")
        month, day, year = article_date.split(" ")
        month = MONTH_DICT[month]
        new_date_format = f"{year}-{month}-{day}"
        date_time_object = date.fromisoformat(new_date_format)
        return date_time_object

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
        article_category = article_parser.find('div', class_="blog__single-category")
        for hrefs in article_category.find_all("a"):
            category_list.append(hrefs)
        article_category = category_list[1].text
        content = article_parser.find('div', id="blog_content").text
        author_name = self.get_author_name()
        author = AuthorHandler(author_name)
        author_id = author.get_author_id_or_add_to_base_new_one()
        article = ArticleHandler(title, date_added, content, article_category, author_id)
        article.is_article_title_in_base_and_add_to_base()




        # # TODO sprawdź datę i pobieraj tylko najnowsze do bazy
        # print(title)
        # print(article_category)
        # print(author_name)
        # print(date_added)
        # print(content)


@dataclass
class AuthorHandler(Handler):
    db = Database("calisthenics_articles.db")
    name: str

    def insert_author_to_db(self) -> None:
        self.db.insert_author_to_db(self.name)

    def get_author_id(self) -> int:
        return self.db.get_author_id(self.name)

    def get_author_id_or_add_to_base_new_one(self) -> int:
        id_check = self.get_author_id()
        if not id_check:
            self.insert_author_to_db()
            author_id = self.db.get_author_id(self.name)
            return author_id

        return id_check



@dataclass
class ArticleHandler(Handler):
    db = Database("calisthenics_articles.db")
    title: str
    article_date: date
    content: str
    category: str
    author_id: int

    def insert_article_to_db(self) -> None:
        self.db.insert_article_to_db(self.title, self.article_date, self.content, self.category, self.author_id)

    def is_article_title_in_base_and_add_to_base(self):
        title_check = self.db.is_article_title_in_base(self.title)
        if not title_check:
            self.insert_article_to_db()








