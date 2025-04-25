import hashlib
import re
import math
from collections import Counter

import sqlite3
from database import DB_PATH


def print_table(connection, table_name, col1, col2):
    try:
        cursor = connection.cursor()
        query = f"SELECT {col1}, {col2} FROM {table_name}"
        result = cursor.execute(query).fetchall()
        for row in result:
            print(row)
    except:
        print('Something went terribly wrong')


class FileProcessing:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_hash(self, content:str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def _is_file_processed(self, connection, file_name: str, file_hash: str) -> bool:
        cursor = connection.cursor()
        cursor.execute(
            """SELECT file_id FROM files
            WHERE file_name = ? OR file_hash = ?
            LIMIT 1""",
            (file_name, file_hash)
        )
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0
    
    def _insert_new_file(self, connection, file_name:str, file_hash: str) -> None:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO files (file_name, file_hash) VALUES (?, ?)",
            (file_name, file_hash)
        )
        return
    
    def _save_word_tfidf(self, connection, file_id: int, text: str) -> None:
        words = Counter(re.findall(r'\b\w+\b', text.lower()))
        cursor = connection.cursor()
        for word, tf in words.items():
            cursor.execute(
                "INSERT INTO word_tf (word, file_id, tf) VALUES (?, ?, ?)",
                (word, file_id, tf)
            )
            # Здесь мы сохраняем Первое вхождение с дефолтным idf=1.0
            cursor.execute(
                "INSERT OR IGNORE INTO word_idf (word) VALUES (?)",
                (word,)
            )
        
        # И сразу же обновляем idf для всей таблицы. Нужно ли это делать прямо здесь?..
        total_files = cursor.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        unique_words = cursor.execute("SELECT word FROM word_idf").fetchall()
        for word in unique_words:
            files_with_words = cursor.execute(
                "SELECT COUNT(DISTINCT file_id) FROM word_tf WHERE word = ?",
                (word)
            ).fetchone()[0]
            
            idf = math.log(total_files / files_with_words)
            cursor.execute(
                "UPDATE word_idf SET idf = ? WHERE word = ?",
                (idf, word[0])
            )


if __name__ == "__main__":
    # тест-тест
    FP = FileProcessing(DB_PATH)
    
    temp_path = "/home/gedfalk/Space/testProjects/lestaGames/tests/files/"
    file_name = "001.txt"
    PATH = temp_path+file_name

    with open(PATH, "r") as file:
        text = file.read()
    
    with sqlite3.connect(DB_PATH) as connection:
        file_hash = FP._get_hash(text)

        file_in = FP._is_file_processed(connection, PATH, file_hash)
        if file_in == 0:
            FP._insert_new_file(connection, PATH, file_hash)
            file_in = FP._is_file_processed(connection, PATH, file_hash)   
            print(f'{file_name} is inserted')
            FP._save_word_tfidf(connection, file_in, text)
        else:
            print(f"File is already there. It's id equals {file_in}")
            
        # print_table(connection, 'files', 'file_id', 'file_name')
        # print_table(connection, 'word_tf', 'word', 'file_id')
        # print_table(connection, 'word_idf', 'word', 'idf')
