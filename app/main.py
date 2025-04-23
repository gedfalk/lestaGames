from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import re
from collections import Counter
import sqlite3
from database import init_db, DB_PATH


def count_words(text: str):
    words = re.findall(r'\b\w+\b', text.lower())
    return Counter(words)

# Это нужно в любом случае переписывать
def save_to_db(counted_words):
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        # пока так... для однократного подсчёта очищаем таблицу
        cursor.execute("DELETE FROM word_count")

        cursor.executemany(
            "INSERT INTO word_count (word, count) VALUES (?, ?)",
            counted_words.items()
        )

        connection.commit()


init_db()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def upload_form(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})

@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    content = (await file.read()).decode()
    counted_words = count_words(content)
    save_to_db(counted_words)

    # получить то 50 словъ
    connection = sqlite3.connect(DB_PATH)
    top50 = connection.execute(
        "SELECT word, count FROM word_count ORDER BY count DESC LIMIT 50"
    ).fetchall()
    connection.close

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "uploaded": True, "word_count": top50}
    )


# Чисто затестить
@app.get("/test/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
            "test.html",
            {"request": request, "message": "Тестовое LestaGames"}
    )
