# db/words.db and word_count

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db/tfidf.db"

def init_db():
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        # Очищаем таблицы после прошлых использований... Ну пока только так
        cursor.executescript("""
            DROP TABLE IF EXISTS  word_count;
            DROP TABLE IF EXISTS  word_idf;
            DROP TABLE IF EXISTS  files;
            DROP TABLE IF EXISTS  word_tf;
            """)

        # проверить, работают ли индексы      
        cursor.executescript("""
            CREATE TABLE files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL UNIQUE,
                file_hash TEXT NOT NULL UNIQUE,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                             
            CREATE TABLE word_idf (
                word TEXT PRIMARY KEY,
                idf REAL DEFAULT 1.0
                );
            
            CREATE TABLE word_tf (
                word TEXT NOT NULL,
                file_id INTEGER NOT NULL,
                tf INTEGER NOT NULL,
                PRIMARY KEY (word, file_id),
                FOREIGN KEY (word) REFERENCES words(word),
                FOREIGN KEY (file_id) REFERENCES files(file_id)
                );
              
            CREATE TABLE word_count (
                word TEXT NOT NULL,
                count INTEGER NOT NULL
                );
                             
            CREATE INDEX idx_word_tf_file ON word_tf(file_id);
            CREATE INDEX idx_word_tf_word ON word_tf(word);
            """)
        
        connection.commit()


if __name__ == "__main__":
    init_db()
    print("Базы данных созданы")