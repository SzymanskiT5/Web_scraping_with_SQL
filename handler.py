from dataclasses import dataclass
from constants import SCROLL_PAUSE, URL, MONTH_DICT, CWD, AUTHOR_NAMES, ORDER_DICT
from database import Database
from exceptions import EndOfPageException, UpToDateException
from selenium import webdriver, common
from datetime import date, datetime
from bs4 import BeautifulSoup
import pyinputplus as pyip
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
    choice_to_print = None



    def check_if_database_has_data_or_is_empty(self):
        """To make a choice, we need to first have a database with some record"""
        print("Welcome!")
        print("Madbarz webscraping made by Sebastian")
        print(f"Today is {self.check_date()}")
        while True:
            try:
                check_database = self.db.get_authors_info()
                if not check_database:
                    raise sqlite3.OperationalError
                self.user_interface()

            except sqlite3.OperationalError:
                print("Your database is empty! We need to scrap!")
                user_choice = pyip.inputYesNo("Do you want to start? Y/N\n", yesVal="Y", noVal="N")
                if user_choice == "Y":
                    self.check_for_updates()
                elif user_choice == "N":
                    print("Bye!")

    def user_interface(self):

        user_choice = pyip.inputMenu(["Check for updates",
                                      "Show authors",
                                      "Show all content from all authors",
                                      "Show all content from one author",
                                     "Show articles sorted by adding date",
                                      "Show articles selected from date",
                                      "Show articles selected from category",
                                      "Delete all"],
                                     "What would you like to do?\n",
                                     numbered=True)

        self.execute_user_choice(user_choice)

    def execute_user_choice(self, user_choice) -> None:
        if user_choice == "Check for updates":
            self.check_for_updates()

        elif user_choice == "Show authors":
            result = self.db.get_authors_info()
            for author_id, author_name in result:
                print(f"{author_id}. {author_name}")

        elif user_choice == "Show all content from all authors":
            self.choice_to_print = self.db.get_all_author_article_content_date()
            self.print_author_title_content_date_added()

        elif user_choice == "Show all content from one author":
            authors_list = self.db.get_authors_names()
            author_choice = pyip.inputMenu(authors_list, "From?\n", numbered=True)
            self.choice_to_print = self.db.get_content_from_selected_author(author_choice)
            self.print_author_title_content_date_added()

        elif user_choice == "Show articles sorted by adding date":
            order = pyip.inputMenu(["Descending", "Ascending"], "How would you like to show?\n", numbered=True)
            choice = ORDER_DICT[order]
            self.choice_to_print = self.db.get_content_ordered_by_date(choice)
            self.print_author_title_content_date_added()

        elif user_choice == "Show articles selected from date":
            articles_date = self.db.get_articles_dates()
            date_choice = pyip.inputMenu(articles_date, "From?\n", numbered=True)
            self.choice_to_print = self.db.get_articles_from_selected_date(date_choice)
            self.print_author_title_content_date_added()

        elif user_choice == "Show articles selected from category":
            articles_category = self.db.get_categories()
            article_choice = pyip.inputMenu(articles_category, "From?\n", numbered=True)
            self.choice_to_print = self.db.get_articles_from_selected_category(article_choice)
            self.print_author_title_content_date_added()

        elif user_choice == "Delete all":
            self.db.delete_all()




    def print_author_title_content_date_added(self) -> None:
        for author_name, article_title, content, date_added, category in self.choice_to_print:
            print(category)
            print(f"{author_name} : {article_title}")
            print(content)
            print(f"Date added: {date_added} ")
            print()


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


    def check_for_updates(self) -> None:
        self.run_driver()

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

    def get_scrap_info(self, main_blog_site_parser) -> None:

        for article_parser in main_blog_site_parser.find_all('article', class_="blog__post"):
            article_link = self.get_article_link(article_parser)
            title = self.get_article_title(article_link)
            article_date = self.get_article_date(article_link)
            last_date_added = self.db.get_last_article_date()
            date_comparer = self.compare_dates(last_date_added, article_date)
            title_check = self.db.is_article_title_in_base(title)
            try:
                self.is_up_to_date(title_check, date_comparer)
            except UpToDateException:
                print("Everything is up to date!")
                break
            category = self.get_article_category(article_link)
            content = self.get_article_content(article_link)
            author = self.get_author_object()
            author_id = author.get_author_id_or_add_to_base_new_one()
            article = self.get_article_object(title, article_date, content, category, author_id)
            article.insert_article_to_db()

    def is_up_to_date(self, tittle_check, date_comparer):
        if tittle_check and date_comparer:
            raise UpToDateException



    @staticmethod
    def compare_dates(last_date, article_date) -> bool:
        if not last_date:
            return False
        if last_date > article_date:
            return True


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

    @staticmethod
    def get_article_title(article_link) -> str:
        title = str(article_link.find(class_="blog__single--title").text)
        return title

    @staticmethod
    def get_article_category(article_link) -> str:
        category_list = []
        article_category = article_link.find('div', class_="blog__single-category")
        for hrefs in article_category.find_all("a"):
            category_list.append(hrefs)
        article_category = category_list[1].text
        if article_category:
            return article_category
        return "Other"


    @staticmethod
    def get_article_content(article_link) -> str:
        content = article_link.find('div', id="blog_content").text
        return content

    def get_author_object(self):
        author_name = self.get_author_name()
        author = AuthorHandler(author_name)
        return author

    @staticmethod
    def get_article_object(title, date_added, content, article_category, author_id):
        article = ArticleHandler(title, str(date_added), content, article_category, author_id)
        article.make_apostrophe_and_qutoes_escaped()
        return article

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


@dataclass
class ArticleHandler(Handler):
    title: str
    article_date: str
    content: str
    category: str
    author_id: int

    def insert_article_to_db(self) -> None:
        self.db.insert_article_to_db(self.title, self.article_date, self.content, self.category, self.author_id)

    def is_article_title_in_base_and_add_to_base(self)-> None:
        title_check = self.db.is_article_title_in_base(self.title)
        if not title_check:
            self.insert_article_to_db()

    def make_apostrophe_and_qutoes_escaped(self) -> None:
        '''If we don't escape apostorophes and quotes it can causes SQL queries problems'''
        self.title = self.title.replace('"', '""').replace("'", "''")










