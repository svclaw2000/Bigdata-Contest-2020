import json
from database import open_helper
import datetime
import pandas as pd


class CovidResult:
    @staticmethod
    def reset_table():
        conn = open_helper.get_connection()
        with conn.cursor() as cursor:
            sql = "DROP TABLE IF EXISTS COVID_RESULT_TB"
            cursor.execute(sql)

            sql = """
            CREATE TABLE IF NOT EXISTS COVID_RESULT_TB (
            _ID INT PRIMARY KEY AUTO_INCREMENT,
            DATE DATE NOT NULL,
            LOCALE CHAR(2),            
            CONFIRM INT,
            DEAD INT,
            UNIQUE KEY (DATE, LOCALE)
            )
            """
            cursor.execute(sql)
        conn.commit()
        conn.close()

    @staticmethod
    def insert(covids):
        conn = open_helper.get_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT IGNORE INTO COVID_RESULT_TB (DATE, LOCALE, CONFIRM, DEAD)  
                VALUES (%s, %s, %s, %s)
                """
            for covid in covids:
                cursor.execute(sql,
                               (covid.date, covid.locale, covid.confirm, covid.dead))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        conn = open_helper.get_connection()
        with conn.cursor(open_helper.DictCursor) as cursor:
            sql = """
                SELECT _ID, DATE, LOCALE, CONFIRM, DEAD  
                FROM COVID_RESULT_TB 
                ORDER BY DATE
            """
            cursor.execute(sql)
            data = cursor.fetchall()
            covids = []
            for d in data:
                covids.append(CovidResult(
                    id=d['_ID'],
                    date=d['DATE'],
                    locale=d['LOCALE'],
                    confirm=d['CONFIRM'],
                    dead=d['DEAD']
                ))
        conn.close()
        return covids

    @staticmethod
    def get_by_date_locale(date=datetime.date.today(), locale='전국'):
        conn = open_helper.get_connection()
        with conn.cursor(open_helper.DictCursor) as cursor:
            sql = """
                SELECT _ID, DATE, LOCALE, CONFIRM, DEAD  
                FROM COVID_RESULT_TB 
                WHERE DATE=%s AND LOCALE=%s
            """
            cursor.execute(sql, (date, locale))
            data = cursor.fetchall()
            if len(data) > 0:
                d = data[0]
                ret = CovidResult(
                    id=d['_ID'],
                    date=d['DATE'],
                    locale=d['LOCALE'],
                    confirm=d['CONFIRM'],
                    dead=d['DEAD']
                )
            else:
                ret = None
        conn.close()
        return ret

    def __init__(self, id=-1, date: datetime.date = None, locale: str = None, confirm = -1, dead = -1):
        self.id = id
        self.date = date
        self.locale = locale
        self.confirm = confirm
        self.dead = dead
