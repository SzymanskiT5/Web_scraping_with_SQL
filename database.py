import sqlite3
from datetime import date
from typing import Tuple, List, Union


class Database:
    def __init__(self, db: str):
        self.db = db
        self.create_article_table()
        self.create_author_table()

    def create_author_table(self) -> None:
        with self as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS author(
            id INTEGER PRIMARY KEY AUTOINCREMENT ,
            name TEXT NOT NULL
    
                  )
              """)

    def get_author_id(self, author) -> Union[int, bool]:
        with self as cursor:
            _SQL = f'SELECT id FROM author WHERE name like "{author}"'
            cursor.execute(_SQL)
            rows = cursor.fetchone()
            if not rows:
                return False
            return rows[0]

    def insert_author_to_db(self, author_name)-> None:
        with self as cursor:
            _SQL = "INSERT INTO author(name) VALUES (?)"
            cursor.execute(_SQL, [author_name])

    def get_authors_info(self) -> List[Tuple[int, str]]:
        with self as cursor:
            _SQL = f"SELECT * FROM author "
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            return rows

    def get_authors_names(self) -> List:
        with self as cursor:
            _SQL = f"SELECT name FROM author "
            cursor.execute(_SQL)
            cursor.row_factory = lambda cursor, row: row[0]
            rows = cursor.fetchall()
            return rows

    def create_article_table(self) -> None:
        with self as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS article(
            id INTEGER PRIMARY KEY AUTOINCREMENT ,
            title TEXT NOT NULL,
            date_added text NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            author_id INTEGER,
            
            foreign key (author_id) REFERENCES author(id)
            )
    

            
            
            """)

    def insert_article_to_db(self, title, article_date, content, category, author_id) -> None:
        with self as cursor:
            _SQL = "INSERT INTO article(title, date_added, content, category, author_id) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(_SQL, (title, str(article_date), content, category, int(author_id)))

    def is_article_title_in_base(self, article_title) -> bool:

        with self as cursor:
            _SQL = f"SELECT id FROM article WHERE title LIKE '{article_title}'"
            cursor.execute(_SQL)
            rows = cursor.fetchone()
            if rows:
                return True
            return False

    def get_article_info(self) -> List[Tuple[str]]:
        with self as cursor:
            _SQL = f"SELECT * FROM article "
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            return rows

    def get_all_author_article_content_date(self) -> List[Tuple[str]]:
        with self as cursor:
            _SQL = f"SELECT name, title, content, date_added, category FROM author INNER JOIN article on author.id = article.author_id"
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            return rows

    def get_categories(self) -> List:
        with self as cursor:
            _SQL = f"SELECT DISTINCT category FROM article"
            cursor.execute(_SQL)
            cursor.row_factory = lambda cursor, row: row[0]
            rows = cursor.fetchall()
            return rows


    def get_content_from_selected_author(self, author_name):
        with self as cursor:
            _SQL = f"SELECT name, title, content, date_added, category  FROM author INNER JOIN article on " \
                   f"author.id = article.author_id WHERE name LIKE '{author_name}'"
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            return rows

    def get_content_ordered_by_date(self, order) -> List[Tuple[str]]:
        with self as cursor:
            _SQL = f"SELECT name, title, content, date_added, category FROM author INNER JOIN article on " \
                    f"author.id = article.author_id ORDER BY date_added {order}"
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            return rows

    def get_articles_dates(self) -> List:
        with self as cursor:
            _SQL = f"SELECT DISTINCT date_added FROM article"
            cursor.execute(_SQL)
            cursor.row_factory = lambda cursor, row: row[0]
            rows = cursor.fetchall()
            return rows

    def get_articles_from_selected_date(self, date_added) -> List[Tuple[str]]:
        with self as cursor:
            _SQL = f"SELECT  name, title, content, date_added, category FROM author INNER JOIN article on " \
                    f"author.id = article.author_id WHERE date_added LIKE '{date_added}'"
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            return rows

    def get_articles_from_selected_category(self, category) -> List[Tuple[str]]:
        with self as cursor:
            _SQL = f"SELECT  name, title, content, date_added, category FROM author INNER JOIN article on " \
                    f"author.id = article.author_id WHERE category LIKE '{category}'"
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            return rows

    def get_last_article_date(self):
        with self as cursor:
            _SQL = f"SELECT date_added FROM article ORDER BY date_added DESC"
            cursor.execute(_SQL)
            rows = cursor.fetchone()
            if rows:
                date_time_object = date.fromisoformat(rows[0])
                return date_time_object
            return

    def delete_last_article(self, title):
        '''To make sure that up to date logic works'''
        with self as cursor:
            _SQL = f"DELETE FROM article WHERE title LIKE '{title}' "
            cursor.execute(_SQL)

    def delete_all(self):
        with self as cursor:
            _SQL = f"DROP TABLE author"
            cursor.execute(_SQL)
            _SQL1 = f"DROP TABLE article"
            cursor.execute(_SQL1)

    def __enter__(self) -> sqlite3.Cursor:
        self.connector = sqlite3.connect(self.db)
        self.cursor = self.connector.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_trace) -> None:
        self.connector.commit()
        self.connector.close()


