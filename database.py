import sqlite3
from datetime import date, datetime

class Database:
    def __init__(self, db: str):
        self.db = db
        self.create_article_table()
        self.create_author_table()

    def create_author_table(self) -> None:
        with self as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS author(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
    
                  )
              """)

    def author_id_query(self, author):
        with self as cursor:
            _SQL = f"SELECT id FROM author WHERE name like'{author}%'"
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            if len(rows) == 0: ##TODO zwaracanie
                return False
            return rows[0]

    # def check_if_author_exists(self, author):
    #     with self as cursor:
    #         _SQL = f"SELECT id FROM author WHERE name like'{author}%'"
    #         cursor.execute(_SQL)
    #         rows = cursor.fetchall()
    #         if len(rows) == 0:
    #             return False
    #         else:
    #             return True

    def insert_author_to_db(self, author):
        with self as cursor:
            _SQL = 'INSERT INTO author(name) VALUES (?)'
            cursor.execute(_SQL, author)

    def create_article_table(self)-> None:
        with self as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS article(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            date DATE NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            author_id INTEGER,
            
            foreign key (author_id) REFERENCES author(id)
            )

            
            
            
            """)

    def authors_info(self):
        with self as cursor:
            _SQL = f"SELECT * FROM author "
            cursor.execute(_SQL)
            rows = cursor.fetchall()
            return rows

    def __enter__(self):
        self.connector = sqlite3.connect(self.db)
        self.cursor = self.connector.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_trace) -> None:
        self.connector.commit()
        self.connector.close()
