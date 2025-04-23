from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def upload_form(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})

@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "uploaded": True}
    )


# Чисто затестить
@app.get("/test/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
            "test.html",
            {"request": request, "message": "Тестовое LestaGames"}
    )
