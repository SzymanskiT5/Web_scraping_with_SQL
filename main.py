from handler import Handler, AuthorHandler, ArticleHandler



'''Web scraping from https://www.madbarz.com/blog'''


def main():
    executor = Handler()
    # executor.start_scraping()
    # executor.db.get_authors_info()
    # executor.db.get_article_info()
    article = ArticleHandler('Intense Full Body No Equipment Workout - "Dirty Dozen" Challenge', "date_added", "content", "article_category", 2)
    article.insert_article_to_db()
    print(article.is_article_title_in_base_and_add_to_base())


if __name__ == "__main__":
    main()


