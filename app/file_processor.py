import hashlib
import re
from collections import Counter

# delete sqlite3 and dbpath
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
        print('something went terribly wrong')


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
    
    def _save_word_tf(self, connection, file_id: int, text: str) -> None:
        words = Counter(re.findall(r'\b\w+\b', text.lower()))
        cursor = connection.cursor()
        for word, tf in words.items():
            cursor.execute(
                "INSERT INTO word_tf (word, file_id, tf) VALUES (?, ?, ?)",
                (word, file_id, tf)
            )
            # здесь же добавляем в таблицу word_idf, где дефолт равен 1.0
            # нужно обработать случай, когда слово уже есть в таблице
            # cursor.execute(
            #     "INSERT INTO word_idf (word) VALUES (?)",
            #     (word,)
            # )



if __name__ == "__main__":
    FP = FileProcessing(DB_PATH)
    
    temp_path = "/home/gedfalk/Space/testProjects/lestaGames/tests/files/"
    file_name = "004.txt"
    PATH = temp_path+file_name

    with open(PATH, "r") as file:
        text = file.read()
    
    with sqlite3.connect(DB_PATH) as connection:
        file_hash = FP._get_hash(text)
        print(text[:20], file_hash)

        file_in = FP._is_file_processed(connection, PATH, file_hash)
        if file_in == 0:
            FP._insert_new_file(connection, PATH, file_hash)
            file_in = FP._is_file_processed(connection, PATH, file_hash)   
            print(f'{file_name} is inserted')
            FP._save_word_tf(connection, file_in, text)
        else:
            print(f"File is already there. It's id equals {file_in}")

        # print_table(connection, 'files', 'file_id', 'file_name')
        print_table(connection, 'word_tf', 'word', 'file_id')
    
