import sqlite3
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

    def insert_article_to_db(self, title, article_date, content, category, author_id)-> None:
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

    def get_all_author_article_content_date(self):
        with self as cursor:
            _SQL = f"SELECT name, title, content, date_added FROM author INNER JOIN article on author.id = article.author_id"
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            return rows



    def get_content_from_selected_author(self, author_name):
        with self as cursor:
            _SQL = f"SELECT name, title, content, date_added FROM author INNER JOIN article on " \
                   f"author.id = article.author_id WHERE name like {author_name}"

            cursor.execute(_SQL)
            rows = cursor.fetchall()

    def __enter__(self) -> sqlite3.Cursor:
        self.connector = sqlite3.connect(self.db)
        self.cursor = self.connector.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_trace) -> None:
        self.connector.commit()
        self.connector.close()


