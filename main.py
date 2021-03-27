from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import date, datetime
from selenium import webdriver
import random
import requests
import time
import lxml
import os
import sqlite3

'''Web scraping from https://www.madbarz.com/blog, 
unfortunately articles don't have authors, but for the needs
I've made some random names table.'''


class Manager:

    def __init__(self):
        self.db = Database("calisthenics_articles.db")
        self.author_names = ["John", "Anna", "Robert", "Matthew", "George", "Kamil"]

    def check_date(self):
        return datetime.date(datetime.now())

    def return_author_name(self):
        return random.choice(self.author_names)

    def reformat_date(self, date):
        month_dict = {"January": "01",
                        "February": "02",
                        "March": "03",
                        "April":  "04",
                        "May": "05",
                        "June": "06",
                        "July": "07",
                        "August": "08",
                        "September": "09",
                        "October": "10",
                        "November": "11",
                        "December": "12"}

        date = date.replace(",","")
        date = date.replace("\n","")
        month, day, year = date.split(" ")
        month = month_dict[month]
        new_date_format = f"{year}-{month}-{day}"
        return new_date_format


    def start_scraping(self):
        '''Madbarz has dynamic site, we need first scroll all over to the end'''


        url = "https://www.madbarz.com/blog/"
        cwd = os.getcwd()
        driver = webdriver.Chrome(cwd + "/chromedriver.exe")
        driver.implicitly_wait(30)

        try:
            SCROLL_PAUSE = 0.5
            driver.get(url)

            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(SCROLL_PAUSE)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            main_blog_site_parser = BeautifulSoup(driver.page_source, "lxml")
            for article in main_blog_site_parser.find_all('article', class_="blog__post"):
                category_list = []
                blog_class = article.find(class_="blog__post--content")
                article_link = blog_class.find('a').get('href')
                article_link_list = article_link.split("/")[2:]
                article_link = url + "/".join(article_link_list)
                link_request = requests.get(article_link).text
                article_parser = BeautifulSoup(link_request, 'lxml')
                title = article_parser.find(class_="blog__single--title").text
                date_added = article_parser.find(class_='date').text
                date_added = self.reformat_date(date_added)
                article_category = article_parser.find('div', class_="blog__single-category")
                for hrefs in article_category.find_all("a"):
                    category_list.append(hrefs)
                article_category = category_list[1].text
                print(article_category)






        finally:
            driver.quit()

        #

        # url = "https://www.madbarz.com/blog"
        # source = requests.get(url).text
        # soup = BeautifulSoup(source, 'lxml')
        # for article in soup.find_all('article', class_="blog__post"):
        #     print(article.text)


class Database:
    def __init__(self, db:str):
        self.db = db

@dataclass
class Author:
    name: str


@dataclass
class Article:
    tittle: str
    date: date
    content: str
    author_id: int
    category: str




def main():
    start = Manager()
    start.start_scraping()




if __name__ == "__main__":
    main()


