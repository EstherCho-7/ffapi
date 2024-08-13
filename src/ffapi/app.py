from typing import Union

from fastapi import FastAPI, HTTPException
import pandas as pd
import requests #(req() 만들기 위함)

app = FastAPI()

df=pd.read_parquet("/home/esthercho/code/ffapi/data")

@app.get("/")
def read_root():
    return {"Hello": "World"}

def gen_url(movieCd="20156962"):
    base_url="http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json"
    import os
    key=os.getenv("MOVIE_API_KEY")
    url=f"{base_url}?key={key}&movieCd={movieCd}"
#    for k, v in url_param.items():
#        url=url+f"&{k}={v}"
    return url

def req(movie_cd="20156962"):
    url=gen_url(movie_cd)
    r=requests.get(url)
    data=r.json()
    nations=data['movieInfoResult']['movieInfo']['nations']
    nationNm = nations[0]['nationNm'] if nations else '정보 없음'
    if nationNm=='한국':
        nationNm = 'K'
    else:
        nationNm = 'F'

    return nationNm

@app.get("/sample")
def sample_data(movie_cd: int):
    sample_df=df.sample(n=5)
    r=sample_df.to_dict(orient='records')
    
    return r

@app.get("/movie/{movie_cd}")
def movie_meta(movie_cd: str):
    meta_df = df[df['movieCd']== movie_cd]
    if meta_df.empty:
        raise HTTPException(status_code=404, detail="영화를 찾을 수 없습니다.")
    
    r = meta_df.iloc[0].to_dict()
    if r['repNationCd'] is None:
        r['repNationCd']=req(movie_cd)

    return r
