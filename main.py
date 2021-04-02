from handler import Handler, AuthorHandler, ArticleHandler



'''Web scraping from https://www.madbarz.com/blog'''


def main():
    ##TODO yapf na koniec
    executor = Handler()
    executor.user_interface()
    # executor.start_scraping()
    # print(executor.db.get_authors_info())
    # print(executor.db.get_article_info())

    # text = "Best PUSH UP TEST Ever - What's your score?"
    # new_text = executor.make_apostrophe_and_qutoes_escaped(text)
    # article = ArticleHandler(new_text, "date_added", "content", "article_category", 2)
    # # article2 = ArticleHandler("Best PUSH UP TEST Ever - What's your score?", "date_added", "content", "article_category",2)
    # # article.insert_article_to_db()
    # print(article.is_article_title_in_base_and_add_to_base())





if __name__ == "__main__":
    main()


