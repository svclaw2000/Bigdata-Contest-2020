import pandas as pd
from data.Clinic import Clinic
import requests
import json

def get_from_csv(path : str = 'data/clinic.csv'):
    df = pd.read_csv(path, encoding='cp949')
    clinics = []
    for i, d in df.iterrows():
        html = requests.get('https://dapi.kakao.com/v2/local/search/address.json?query=%s' %d['주소'],
                            headers= {'Authorization': 'KakaoAK fe0f5cc0490311461e289f6aa831e2cc'})
        loc = json.loads(html.content)['documents']

        if len(loc) > 0:
            loc = loc[0]
        else:
            html = requests.get('https://dapi.kakao.com/v2/local/search/keyword.json?query=%s' %d['주소'],
                                headers= {'Authorization': 'KakaoAK fe0f5cc0490311461e289f6aa831e2cc'})
            loc = json.loads(html.content)['documents'][0]

        clinics.append(Clinic(
            province=d['시도'],
            city=d['시군구'][:2] if len(d['시군구']) > 5 else d['시군구'][:-1] if len(d['시군구']) > 2 else d['시군구'],
            name=d['의료기관명'],
            address=d['주소'],
            location=(loc['x'], loc['y']),
            weekday=d['평일 운영시간'],
            saturday=d['토요일 운영시간'],
            holiday=d['일요일/공휴일\n운영시간'],
            contact=d['대표 전화번호']
        ))
    Clinic.insert(clinics)