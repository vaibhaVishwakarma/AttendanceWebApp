from fastapi import FastAPI, Form, Request 
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
app=FastAPI()
# Allow all origins for simplicity (configure this appropriately for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory = "templates")

@app.get("/",response_class = HTMLResponse)
async def getpage(request : Request):
    return templates.TemplateResponse("./index.html ",{"request":request}) 
@app.post("/submitTable")

async def handle_form_submission(request: Request):
    form_data = await request.form()
    data_dict = {key: value for key, value in form_data.items()}
    return data_dict
    