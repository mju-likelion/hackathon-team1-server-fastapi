from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from nlp_task import detect_language
from typing import Optional

class Text_to_detect(BaseModel):
    text: str
    
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def getOne():
    print("hello_world")
    return detect_language("hello_world")


@app.post("/detect-language")
def echo_text(text_to_detect:Text_to_detect):
    print(text_to_detect.text)
    language = detect_language(text_to_detect.text)
    print(language)
    return { "language" : language }