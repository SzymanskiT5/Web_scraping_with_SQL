from functionality.database import Database
from datetime import date
import sqlite3
import pytest

db = Database("calisthenics_articles.db")


def delete_and_create_db() -> Database:
    db.delete_all()
    new_db = Database("calisthenics_articles.db")
    return new_db


def insert_authors_and_articles(new_db) -> None:
    test_authors_list = ["test1", "test2"]
    for author in test_authors_list:
        new_db.insert_author_to_db(author)
    test_articles_list = [("test", "2019-12-09", "content", "category", 1),
                          ("test1", "1111-11-11", "content1", "category1", 2)]
    for title, date, content, category, author_id in test_articles_list:
        new_db.insert_article_to_db(title, date, content, category, author_id)


def test_should_delete_all_tables_from_database_and_raise_sqlite_error():
    db.delete_all()
    with pytest.raises(sqlite3.OperationalError):
        assert not db.get_authors_info()
        assert not db.get_article_info()


def test_should_check_if_author_table_is_created():
    assert db.check_if_author_table_exists()


def test_should_check_if_article_table_is_created():
    assert db.check_if_article_table_exists()


def test_should_insert_author_and_return_correct_author_id():
    new_db = delete_and_create_db()
    test_authors_list = [(1, "test1"), (2, "test2"), (3, "test3"), (4, "test6")]
    for author_id, name in test_authors_list:
        new_db.insert_author_to_db(name)
        assert new_db.get_author_id(name) == author_id


def test_should_return_authors_info():
    new_db = delete_and_create_db()
    test_authors_list = [(1, "test1"), (2, "test2"), (3, "test3"), (4, "test6")]
    for author_id, author in test_authors_list:
        new_db.insert_author_to_db(author)
    assert new_db.get_authors_info() == test_authors_list


def test_should_return_true_if_article_in_base():
    new_db = delete_and_create_db()
    test_articles_list = [(1, "test", "2019-12-09", "content", "category", 1),
                          (2, "test1", "1111-11-11", "content1", "category1", 2)]
    for article_id, title, date, content, category, author_id in test_articles_list:
        new_db.insert_article_to_db(title, date, content, category, author_id)
        assert new_db.is_article_title_in_base(title)


def test_should_return_false_if_article_not_in_base():
    new_db = delete_and_create_db()
    test_articles_list = [(1, "test", "2019-12-09", "content", "category", 1),
                          (2, "test1", "1111-11-11", "content1", "category1", 2)]
    for article_id, title, date, content, category, author_id in test_articles_list:
        assert new_db.is_article_title_in_base(title) is False


def test_should_return_authors_names():
    new_db = delete_and_create_db()
    test_authors_list = ["test1", "test2", "test3", "test6"]
    for authors in test_authors_list:
        new_db.insert_author_to_db(authors)
    result = new_db.get_authors_names()
    assert result == test_authors_list


def test_should_insert_article_and_return_whole_article():
    new_db = delete_and_create_db()
    test_articles_list = [(1, "test", "2019-12-09", "content", "category", 1),
                          (2, "test1", "1111-11-11", "content1", "category2", 2)]
    for article_id, title, date, content, category, author_id in test_articles_list:
        new_db.insert_article_to_db(title, date, content, category, author_id)
    result = new_db.get_article_info()
    assert result == test_articles_list


def test_should_join_two_tables_with_author_id():
    new_db = delete_and_create_db()
    insert_authors_and_articles(new_db)
    assert new_db.get_all_author_article_content_date() == [("test1", "test", "content", "2019-12-09", "category"),
                                                            ("test2", "test1", "content1", "1111-11-11", "category1")]


def test_should_return_categories():
    new_db = delete_and_create_db()
    test_articles_list = [("test", "2019-12-09", "content", "category", 1),
                          ("test1", "1111-11-11", "content1", "category1", 2)]
    for title, date, content, category, author_id in test_articles_list:
        new_db.insert_article_to_db(title, date, content, category, author_id)
    assert new_db.get_categories() == ["category", "category1"]


def test_should_join_two_tables_for_one_author():
    new_db = delete_and_create_db()
    insert_authors_and_articles(new_db)
    assert new_db.get_content_from_selected_author("test1") == [("test1", "test", "content", "2019-12-09", "category")]
    assert new_db.get_content_from_selected_author("test2") == [
        ("test2", "test1", "content1", "1111-11-11", "category1")]


def test_should_return_joined_tables_sorted_by_date():
    new_db = delete_and_create_db()
    insert_authors_and_articles(new_db)
    assert new_db.get_content_ordered_by_date("DESC") == [("test1", "test", "content", "2019-12-09", "category"),
                                                          ("test2", "test1", "content1", "1111-11-11", "category1")]
    assert new_db.get_content_ordered_by_date("ASC") == [("test2", "test1", "content1", "1111-11-11", "category1"),
                                                         ("test1", "test", "content", "2019-12-09", "category")]


def test_should_return_dates_from_articles():
    new_db = delete_and_create_db()
    insert_authors_and_articles(new_db)
    assert new_db.get_articles_dates() == ["2019-12-09", "1111-11-11"]


def test_should_return_articles_from_selected_date():
    new_db = delete_and_create_db()
    insert_authors_and_articles(new_db)
    assert new_db.get_articles_from_selected_date("2019-12-09") == [
        ("test1", "test", "content", "2019-12-09", "category")]
    assert new_db.get_articles_from_selected_date("1111-11-11") == [
        ("test2", "test1", "content1", "1111-11-11", "category1")]


def test_should_return_articles_from_selected_category():
    new_db = delete_and_create_db()
    insert_authors_and_articles(new_db)
    assert new_db.get_articles_from_selected_category("category") == [
        ("test1", "test", "content", "2019-12-09", "category")]
    assert new_db.get_articles_from_selected_category("category1") == [
        ("test2", "test1", "content1", "1111-11-11", "category1")]


def test_should_return_last_article_date():
    new_db = delete_and_create_db()
    insert_authors_and_articles(new_db)
    assert new_db.get_last_article_date() == date.fromisoformat("2019-12-09")
