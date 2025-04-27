from fastapi import FastAPI, Request, UploadFile, File, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import sqlite3
from database import init_db, DB_PATH
from file_processor import FileProcessing
from utils import get_page_list


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

    return RedirectResponse(
        url=f"/results?file_name={file_name}&file_id={file_id}",
        status_code=303
    )    
     
@app.get("/results")
async def show_results(
    request: Request,
    file_name: str,
    file_id: int,
    sort_by: str = Query("idf", enum=["word", "tf", "idf"]),
    order: str = Query("desc", enum=["asc", "desc"]),
    page: int = Query(1, ge=1)
):
    items_per_page = 50
    db_offset = (page-1) * items_per_page

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        # Общее число элементов... возожно, стоит вынести в таблицу files и там хранить?..
        query = f"""
        SELECT COUNT(*)
        FROM word_tf wt
        JOIN word_idf wi ON wt.word = wi.word
        WHERE wt.file_id = ?
        """
        total_words = cursor.execute(query, (file_id,)).fetchone()[0]

        # Просто вывести 50 элементов, упорядоченных согласно sort_by и order
        # query = f"""
        # SELECT wt.word as word, wt.tf as tf, wi.idf as idf
        # FROM word_tf wt
        # JOIN word_idf wi ON wt.word = wi.word
        # WHERE wt.file_id = ?
        # ORDER BY {sort_by} {order.upper()}
        # LIMIT 50
        # """
        # words = cursor.execute(query, (file_id,)).fetchall()

        # Вывести 50 элементов с позиции db_offset
        query = f"""
        SELECT wt.word as word, wt.tf as tf, wi.idf as idf
        FROM word_tf wt
        JOIN word_idf wi ON wt.word = wi.word
        WHERE wt.file_id = ?
        ORDER BY {sort_by} {order.upper()}
        LIMIT 50 OFFSET ?
        """
        words = cursor.execute(query, (file_id, db_offset)).fetchall()

    words = [{"word": row[0], "tf": row[1], "idf": round(row[2], 2)} for row in words]
    total_pages = total_words // items_per_page
    if total_words % items_per_page > 0:
        total_pages += 1
    page_list = get_page_list(page, total_pages)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "file_name": file_name,
            "file_id": file_id,
            "current_sort": sort_by,
            "current_order": order,
            "words": words,
            "pagination": {
                "total_pages": total_pages,
                "current_page": page,
                "page_list": page_list
            }
        }
    )


# Тестовая страничка
@app.get("/test/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
            "test.html",
            {"request": request, "message": "Тестовое LestaGames"}
    )
