from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Union
from typing import List
from pydantic import BaseModel
import pandas as pd

from location import GetLocation
from wheather import Wheather
from recommend_songs import Recommend_songs


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],  # 특정 도메인만 허용하려면 ["http://localhost:8080/"] 등 지정
    allow_credentials=True,
    allow_methods=[""],  # 모든 HTTP 메서드 허용 (GET, POST 등)
    allow_headers=["*"],  # 모든 헤더 허용
)

class RequestData(BaseModel):
    latitude: float
    longitude: float
    question: str
    pop: int
    

    class Config:
        orm_mode = True

class ResponseData(BaseModel):
    title: str
    artist: str

    class Config:
        orm_mode = True

class RecommendationResponse(BaseModel):
    recommendations: List[ResponseData]

    class Config:
        orm_mode = True

# Song artist Class 생성하기
# 테스트 데이터

@app.post("/api/music/recommend", response_model = RecommendationResponse)
async def response_process(data: RequestData):
    
    loca = GetLocation(data).convert_coordinates_to_address()
    now_whea = Wheather(f"{loca.split(sep = " ")[1]}", f"{loca.split(sep = " ")[2]}")

    playlist = Recommend_songs(data)
    my_musics = playlist.recommend(f"{loca}", f"{now_whea.get_sky()}", 5, 
    {"configurable": {"thread_id": "abc678"}}, "Korean")

    df = pd.DataFrame(my_musics.items(), columns=['artist', 'title'])
    df = df[['title', 'artist']]
    songs_list = df.to_dict(orient = 'records')

    return JSONResponse(content={"recommendations": songs_list})