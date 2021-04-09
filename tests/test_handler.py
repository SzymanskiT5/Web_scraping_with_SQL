import pytest
import requests
from bs4 import BeautifulSoup
from functionality.handler import Handler, AuthorHandler, ArticleHandler
from functionality.constants import AUTHOR_NAMES
from datetime import date
from functionality.exceptions import UpToDateException


def make_connection_with_article():
    url = requests.get("https://www.madbarz.com/blog/301-running-benefits-why-you-should-run-regularly").text
    parser = BeautifulSoup(url, "lxml")
    return parser


def test_should_create_article_object():
    test_article = ArticleHandler(title="title", article_date="29-09-1998",
                                  content="hello", category="test", author_id=1)

    assert isinstance(test_article, ArticleHandler)


def test_should_escape_apostrophes_from_article_tittle():
    test_article = ArticleHandler(title="'title'", article_date="29-09-1998",
                                  content="hello", category="test", author_id=1)
    test_article.make_apostrophe_and_qutoes_escaped()
    assert test_article.title == "''title''"


def test_should_escape_quotes_from_article_tittle():
    test_article = ArticleHandler(title='"title"', article_date="29-09-1998",
                                  content="hello", category="test", author_id=1)
    test_article.make_apostrophe_and_qutoes_escaped()
    assert test_article.title == '""title""'


def test_should_create_author_object():
    test_author = AuthorHandler(name="test")

    assert isinstance(test_author, AuthorHandler)


def test_should_return_formatted_date_object():
    test_dates = [("January 28, 2020", date.fromisoformat("2020-01-28")),
                  ("December 09, 2019", date.fromisoformat("2019-12-09")),
                  ("September 16, 2019", date.fromisoformat("2019-09-16"))]
    for not_formatted_date, formatted_date in test_dates:
        assert Handler.reformat_date(not_formatted_date) == formatted_date


def test_should_return_random_name_from_AUTHOR_NAMES():
    name = Handler.get_author_name()
    assert name in AUTHOR_NAMES


def test_should_return_true_if_last_date_is_less_than_article_date_or_should_return_false_if_there_is_no_last_date():
    list_to_compare = [("", "2019-12-09"), ("2019-12-09", "2019-09-16"), ("3000-12-12", "23-09-15")]
    for last_date, article_date in list_to_compare:
        result = Handler.compare_dates(last_date, article_date)

        assert not last_date or result


def test_should_raise_up_to_date_exception_if_tittle_check_is_true_and_date_comparer_is_true():
    with pytest.raises(UpToDateException):
        assert Handler.is_up_to_date(True, True)


def test_should_return_todays_date():
    assert Handler.check_date() == Handler.check_date()


"""For scraping test, I used https://www.madbarz.com/blog/301-running-benefits-why-you-should-run-regularly article"""


def test_should_return_correct_title():
    article_link = make_connection_with_article()
    title = str(article_link.find(class_="blog__single--title").text)
    assert title == "Running benefits: why you should run regularly"


def test_should_return_correct_correct_article_date():
    """Date in article is January 28, 2020, but program formats it to 2020-01-28 """
    handler = Handler()
    article_link = make_connection_with_article()
    assert Handler.get_article_date(handler, article_link) == date.fromisoformat("2020-01-28")


def test_should_return_correct_article_category():
    article_link = make_connection_with_article()
    assert Handler.get_article_category(article_link) == "Workouts"
