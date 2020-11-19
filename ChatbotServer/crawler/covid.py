import pandas as pd
from data.Covid import Covid
import requests
import json
import datetime


def get_from_csv(con_path: str = 'data/confirmed.csv', dead_path: str = 'data/dead.csv',
                 etc_path: str = 'data/etc.csv'):
    con = pd.read_csv(con_path, encoding='cp949')
    con = con[con['구분별(2)'] != '검역']
    dead = pd.read_csv(dead_path, encoding='cp949')
    dead = dead[dead['구분별(2)'] != '검역']
    etc = pd.read_csv(etc_path, encoding='cp949')

    con = con.fillna(-1).replace('-', -1).iloc[2:]
    dead = dead.fillna(-1).replace('-', -1).iloc[2:]

    date_cols = list(con.columns)[2:]
    new_idx = ['구분별(2)'] + [date_cols[i] for i in range(len(date_cols)) if i % 2 == 0]
    cum_idx = ['구분별(2)'] + [date_cols[i] for i in range(len(date_cols)) if i % 2 == 1]

    etc = etc.fillna(-1).loc[:, ['구분별', '상태별'] + new_idx[1:]]

    new_con = pd.melt(con.loc[:, new_idx], id_vars=['구분별(2)'], var_name='date', value_name='new_confirm')
    cum_con = pd.melt(con.loc[:, cum_idx], id_vars=['구분별(2)'], var_name='date', value_name='cum_confirm')
    cum_con['date'] = cum_con['date'].str[:-2]

    new_dead = pd.melt(dead.loc[:, new_idx], id_vars=['구분별(2)'], var_name='date', value_name='new_dead')
    cum_dead = pd.melt(dead.loc[:, cum_idx], id_vars=['구분별(2)'], var_name='date', value_name='cum_dead')
    cum_dead['date'] = cum_dead['date'].str[:-2]

    place_data = pd.concat([new_con, cum_con[['cum_confirm']], new_dead[['new_dead']], cum_dead[['cum_dead']]], axis=1)
    place_data['date'] = place_data['date'].str.replace('. ', '-')

    total_data = place_data[place_data['구분별(2)'] == '소계']
    total_data['구분별(2)'] = '전국'

    place_data = place_data[place_data['구분별(2)'] != '소계']

    gender = etc[(etc['구분별'] == '남성') | (etc['구분별'] == '여성')].drop(['상태별'], axis=1)
    gender_new_con = pd.melt(gender.iloc[[i for i in range(gender.shape[0]) if i % 4 == 0]], id_vars=['구분별'],
                             var_name='date', value_name='new_confirm')
    gender_cum_con = pd.melt(gender.iloc[[i for i in range(gender.shape[0]) if i % 4 == 1]], id_vars=['구분별'],
                             var_name='date', value_name='cum_confirm')
    gender_new_dead = pd.melt(gender.iloc[[i for i in range(gender.shape[0]) if i % 4 == 2]], id_vars=['구분별'],
                              var_name='date', value_name='new_dead')
    gender_cum_dead = pd.melt(gender.iloc[[i for i in range(gender.shape[0]) if i % 4 == 3]], id_vars=['구분별'],
                              var_name='date', value_name='cum_dead')
    gender_data = pd.concat(
        [gender_new_con, gender_cum_con[['cum_confirm']], gender_new_dead[['new_dead']], gender_cum_dead[['cum_dead']]],
        axis=1)
    gender_data['date'] = gender_data['date'].str.replace('. ', '-')

    age = etc[(etc['구분별'] != '전국') & (etc['구분별'] != '남성') & (etc['구분별'] != '여성')].drop(['상태별'], axis=1)
    age_new_con = pd.melt(age.iloc[[i for i in range(age.shape[0]) if i % 4 == 0]], id_vars=['구분별'], var_name='date',
                          value_name='new_confirm')
    age_cum_con = pd.melt(age.iloc[[i for i in range(age.shape[0]) if i % 4 == 1]], id_vars=['구분별'], var_name='date',
                          value_name='cum_confirm')
    age_new_dead = pd.melt(age.iloc[[i for i in range(age.shape[0]) if i % 4 == 2]], id_vars=['구분별'], var_name='date',
                           value_name='new_dead')
    age_cum_dead = pd.melt(age.iloc[[i for i in range(age.shape[0]) if i % 4 == 3]], id_vars=['구분별'], var_name='date',
                           value_name='cum_dead')
    age_data = pd.concat(
        [age_new_con, age_cum_con[['cum_confirm']], age_new_dead[['new_dead']], age_cum_dead[['cum_dead']]], axis=1)
    age_data['date'] = age_data['date'].str.replace('. ', '-')

    covids = []
    for i, row in total_data.iterrows():
        covids.append(Covid(
            date=row['date'],
            category_1='전국',
            category_2=row['구분별(2)'],
            new_confirm=row['new_confirm'],
            cum_confirm=row['cum_confirm'],
            new_dead=row['new_dead'],
            cum_dead=row['cum_dead']
        ))
    for i, row in place_data.iterrows():
        covids.append(Covid(
            date=row['date'],
            category_1='지역',
            category_2=row['구분별(2)'],
            new_confirm=row['new_confirm'],
            cum_confirm=row['cum_confirm'],
            new_dead=row['new_dead'],
            cum_dead=row['cum_dead']
        ))
    for i, row in gender_data.iterrows():
        covids.append(Covid(
            date=row['date'],
            category_1='성별',
            category_2=row['구분별'],
            new_confirm=row['new_confirm'],
            cum_confirm=row['cum_confirm'],
            new_dead=row['new_dead'],
            cum_dead=row['cum_dead']
        ))
    for i, row in age_data.iterrows():
        covids.append(Covid(
            date=row['date'],
            category_1='연령',
            category_2=row['구분별'],
            new_confirm=row['new_confirm'],
            cum_confirm=row['cum_confirm'],
            new_dead=row['new_dead'],
            cum_dead=row['cum_dead']
        ))
    Covid.insert(covids)


def get_from_web():
    url = 'https://kosis.kr/covid/covid_getSidoMapData.do'
    conf_response = requests.post(url, data={'statusGubun': 'confirm'})
    dead_response = requests.post(url, data={'statusGubun': 'dead'})
    conf_data = json.loads(conf_response.content)
    dead_data = json.loads(dead_response.content)
    conf_data = conf_data['resultSidoData']
    dead_data = dead_data['resultSidoData']

    covids = []
    for conf, dead in zip(conf_data, dead_data):
        locale = conf['ovL1Kor']
        category = '지역'
        if locale == '전체':
            locale = '전국'
            category = '전국'
        elif locale == '검역':
            continue

        covids.append(Covid(
            date=datetime.date.today(),
            category_1=category,
            category_2=locale,
            new_confirm=conf['dtvalCo2'],
            cum_confirm=conf['dtvalCo1'],
            new_dead=dead['dtvalCo2'],
            cum_dead=dead['dtvalCo1']
        ))
    Covid.insert(covids)