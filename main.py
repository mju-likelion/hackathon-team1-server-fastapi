from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from nlp_task import detect_language, tagging_questions
from data_preprocessing import data_preprocessing
from typing import Optional


class Text_to_detect(BaseModel):
    text: str
    
class Text_to_recommend(BaseModel):
    text: str
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#언어 감지 기능
@app.post("/detect-language")
async def echo_text(text_to_detect:Text_to_detect):
    language = await detect_language(text_to_detect.text)
    return { "language" : language }

#보험 상품 추천 기능
@app.post("/recommendations")
async def insurances_recommend(text_to_recommend: Text_to_recommend):
    tags = await tagging_questions(text_to_recommend.text)
    print(tags)
    return tags

#보험 정보 db에 입력 기능
@app.post("/create-insurances")
async def create_insurances(file: UploadFile = File(...)):
    #파일 내용 읽기
    insurance_data = await file.read()
    response = await data_preprocessing(insurance_data)
    return response