from bs4 import BeautifulSoup
import requests
import re
from data.Festival import Festival
import datetime


def run_crawling():
    prev_fest_names = [f.name for f in Festival.get_all()]

    url = 'https://www.mcst.go.kr/kor/s_culture/festival/festivalList.jsp?pMenuCD=&pCurrentPage=%d&pSearchType=&pSearchWord=&pSeq=&pSido=&pOrder=&pPeriod=&fromDt=&toDt='
    cur_page = 1
    total_data = []
    reach_prev = False
    while not reach_prev:
        response = requests.get(url % cur_page)
        soup = BeautifulSoup(response.content, 'html.parser')
        ul = soup.select('ul.mediaWrap.color01')[0]
        title = tuple((p.text,) for p in ul.select('p.title'))
        # Break if title is in previous data.
        if not title:
            break
        detail = tuple(
            tuple(re.sub('[\n\t]', '', d.text)[5:] for d in fest.select('li')) for fest in ul.select('ul.detail_info'))
        for t, d in zip(title, detail):
            if t[0] in prev_fest_names:
                reach_prev = True
                break
            total_data.append(t + d)
        cur_page += 1

    festivals = []
    for d in total_data:
        loc = d[2].split()
        loc[0] = loc[0][:2] if len(loc[0]) == 3 else loc[0][0] + loc[0][2] if len(loc[0]) == 4 else loc[0]
        if len(loc) == 1:
            loc.append(None)
        else:
            loc[1] = loc[1][:-1] if len(loc[1]) > 2 else loc[1]

        date = get_cleansed_date(d[1])
        time = d[1][d[1].find('/') + 2:] if d[1].find('/') != -1 else None

        fest = Festival(name=d[0], province=loc[0], city=loc[1], start=datetime.date(date[0], date[1], date[2]),
                        end=datetime.date(date[3], date[4], date[5]), time=time, contact=d[3])
        festivals.append(fest)
    Festival.insert(festivals)


def get_cleansed_date(d):
    date = [int(n.replace('.', '')) for n in re.findall('[0-9]+[.]|[.][0-9]+', d.replace('.', '..'))]
    if len(date) == 3:
        date.append(date[0])
        date.append(date[1])
        date.append(date[2])
    elif len(date) == 4:
        date.append(date[1])
        date.append(date[3])
        date[3] = date[0]
    elif len(date) == 5:
        date.append(date[4])
        date[3], date[4] = date[0], date[3]
    return date
