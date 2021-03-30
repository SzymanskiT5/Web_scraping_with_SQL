from handler import Handler, AuthorHandler, ArticleHandler



'''Web scraping from https://www.madbarz.com/blog'''


def main():
    executor = Handler()
    executor.start_scraping()


if __name__ == "__main__":
    main()


