from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import sqlite3
from database import init_db, DB_PATH
from file_processor import FileProcessing


init_db()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def upload_form(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})

@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    text = (await file.read()).decode()
    FP = FileProcessing(DB_PATH)
    file_name = file.filename
    file_hash = FP._get_hash(text)

    with sqlite3.connect(DB_PATH) as connection:
        file_id = FP._is_file_processed(connection, file_name, file_hash)
        if file_id == 0:
            FP._insert_new_file(connection, file_name, file_hash)
            file_id = FP._is_file_processed(connection, file_name, file_hash)   
            print(f'{file_name} is inserted')
            FP._save_word_tfidf(connection, file_id, text)
        else:
            print(f"File is already there. It's id equals {file_id}")

        cursor = connection.cursor()
        cursor.execute("""
            SELECT wt.word, wt.tf, wi.idf
            FROM word_tf wt
            JOIN word_idf wi ON wt.word = wi.word
            WHERE wt.file_id = ?
            ORDER BY wi.idf DESC
            LIMIT 50""",
            (file_id,)
        )

        content = cursor.fetchall()
        content = [{"word": row[0], "tf": row[1], "idf": round(row[2], 2)} for row in content]

    return templates.TemplateResponse(
        "index.html", {"request": request, 
                       "uploaded": True, 
                       "file_name": file_name,
                       "file_id": file_id,
                       "content": content,                    
                    }
    )


# Тестовая страничка
@app.get("/test/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
            "test.html",
            {"request": request, "message": "Тестовое LestaGames"}
    )
