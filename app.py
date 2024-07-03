from typing import List
from fastapi import FastAPI, Form, Request 
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
app=FastAPI()
# Allow all origins for simplicity (configure this appropriately for production)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DataItem(BaseModel):
    values: List[List[str]]

class ResponseModel(BaseModel):
    status: str
    data_received: List[List[str]]
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory = "templates")

@app.get("/",response_class = HTMLResponse)
async def getpage(request : Request):
    return templates.TemplateResponse("./index.html ",{"request":request}) 
@app.post("/submit" , response_model=ResponseModel)
async def handle_form_submission(data:DataItem):
    print("hello ",data)
    return JSONResponse({"name":"success"})
    