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


@dataclass
class Handler:
    """Manager for controlling the process"""
    db = Database("calisthenics_articles.db")


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
        self.run_driver()
        # self.start_page_scrolling()
        #

    def run_driver(self) -> None:
        """Set browser driver"""

        print("Runing a driver...")
        print()
        try:
            driver = webdriver.Chrome(CWD + "/chromedriver.exe")
            self.start_page_scrolling(driver)
            print("Finish!")

        except common.exceptions.WebDriverException:
            print("Webdriver error!")

    def start_page_scrolling(self, driver) -> None:
        """Madbarz has dynamic site, we need first scroll all over to the end"""
        try:
            driver.implicitly_wait(30)
            driver.get(URL)

            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                last_height = self.scroll_down(driver, last_height)

        except EndOfPageException:
            main_blog_site_parser = BeautifulSoup(driver.page_source, "lxml")
            self.get_scrap_info(main_blog_site_parser)

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
            print("Scraping...")
            print()
            raise EndOfPageException

        return new_height

    def get_scrap_info(self, main_blog_site_parser):

        for article_parser in main_blog_site_parser.find_all('article', class_="blog__post"):
            article_link = self.get_article_link(article_parser)
            article_date = self.get_article_date(article_link)
            category = self.get_article_category(article_link)
            title = self.get_article_title(article_link)
            content = self.get_article_content(article_link)
            author = self.get_author_object()
            author_id = author.get_author_id_or_add_to_base_new_one()
            article =self.get_article_object(title, article_date, content, category, author_id)

            # author_id = author.get_author_id_or_add_to_base_new_one()
            # article.is_article_title_in_base_and_add_to_base()

    def get_article_link(self, article_parser) -> BeautifulSoup:
        """Get direct article links """
        blog_class = article_parser.find(class_="blog__post--content")
        article_link = blog_class.find('a').get('href')
        article_link_list = article_link.split("/")[2:]
        article_link = URL + "/".join(article_link_list)
        link_request = requests.get(article_link).text
        article_parser = BeautifulSoup(link_request, 'lxml')
        return article_parser

    def get_article_date(self, article_link) -> date:
        date_added = article_link.find(class_='date').text
        date_added = self.reformat_date(date_added)
        return date_added

    def get_article_title(self, article_link) -> str:
        title = str(article_link.find(class_="blog__single--title").text)
        return title

    def get_article_category(self, article_link) -> str:
        category_list = []
        article_category = article_link.find('div', class_="blog__single-category")
        for hrefs in article_category.find_all("a"):
            category_list.append(hrefs)
        article_category = category_list[1].text
        return article_category

    def get_article_content(self, article_link) -> str:
        content = article_link.find('div', id="blog_content").text
        return content

    def get_author_object(self):
        author_name = self.get_author_name()
        author = AuthorHandler(author_name)
        return author

    def get_article_object(self, title, date_added, content, article_category, author_id) :
        article = ArticleHandler(title, str(date_added), content, article_category, author_id)
        return article



        # # TODO sprawdź datę i pobieraj tylko najnowsze do bazy
        # print(title)
        # print(article_category)
        # print(author_name)
        # print(date_added)
        # print(content)


@dataclass
class AuthorHandler(Handler):
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


#date
@dataclass
class ArticleHandler(Handler):
    title: str
    article_date: str
    content: str
    category: str
    author_id: int

    def insert_article_to_db(self) -> None:
        self.db.insert_article_to_db(self.title, self.article_date, self.content, self.category, self.author_id)

    def is_article_title_in_base_and_add_to_base(self):
        title_check = self.db.is_article_title_in_base(self.title)
        return title_check
        # if not title_check:
        #     self.insert_article_to_db()








