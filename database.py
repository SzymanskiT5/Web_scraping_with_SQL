import sqlite3
from typing import Tuple, List

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

    def get_author_id(self, author):
        with self as cursor:
            _SQL = f"SELECT id FROM author WHERE name like'{author}'"
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            if len(rows) == 0:
                return False
            return rows[0]


    def insert_author_to_db(self, author_name):
        with self as cursor:
            _SQL = "INSERT INTO author(name) VALUES (?)"
            cursor.execute(_SQL, [author_name])

    def authors_info(self) -> List[Tuple[str]]:
        with self as cursor:
            _SQL = f"SELECT * FROM author "
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            return rows

    def create_article_table(self) -> None:
        with self as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS article(
            id INTEGER PRIMARY KEY AUTOINCREMENT ,
            title TEXT NOT NULL,
            date DATE NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            author_id INTEGER,
            
            foreign key (author_id) REFERENCES author(id)
            )
    

            
            
            """)

    def insert_article_to_db(self, title, article_date, content, category, author_id):
        with self as cursor:
            _SQL = "INSERT INTO article(title, date, content, category, author_id) VALUES (?, ?, ?, ?, ?)" ##TODO something went wrong :)
            cursor.execute(_SQL, [title, article_date, content, category, author_id])

    def is_article_title_in_base(self, article_title):
        with self as cursor:
            _SQL = f"SELECT id FROM author WHERE name like'{article_title}'"
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            if len(rows) == 0:
                return False
            return rows[0]


    def authors_info(self) -> List[Tuple[str]]:
        with self as cursor:
            _SQL = f"SELECT * FROM article "
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            return rows


    def __enter__(self) -> sqlite3.Cursor:
        self.connector = sqlite3.connect(self.db)
        self.cursor = self.connector.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_trace) -> None:
        self.connector.commit()
        self.connector.close()


