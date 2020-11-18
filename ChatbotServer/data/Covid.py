import json
from database import open_helper
import datetime
import pandas as pd


class Covid:
    @staticmethod
    def reset_table():
        conn = open_helper.get_connection()
        with conn.cursor() as cursor:
            sql = "DROP TABLE IF EXISTS COVID_TB"
            cursor.execute(sql)

            sql = """
            CREATE TABLE IF NOT EXISTS COVID_TB (
            _ID INT PRIMARY KEY AUTO_INCREMENT,
            DATE DATE NOT NULL,
            CATEGORY_1 CHAR(2),
            CATEGORY_2 CHAR(6),
            NEW_CONFIRM INT,
            CUM_CONFIRM INT,
            NEW_DEAD INT,
            CUM_DEAD INT,
            UNIQUE KEY (DATE, CATEGORY_2)
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
                INSERT IGNORE INTO COVID_TB (DATE, CATEGORY_1, CATEGORY_2, NEW_CONFIRM, CUM_CONFIRM, NEW_DEAD, CUM_DEAD) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
            for covid in covids:
                cursor.execute(sql,
                               (covid.date, covid.category_1, covid.category_2, covid.new_confirm, covid.cum_confirm,
                                covid.new_dead, covid.cum_dead))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all(max_date=None):
        conn = open_helper.get_connection()
        with conn.cursor(open_helper.DictCursor) as cursor:
            if max_date is None:
                sql = """
                    SELECT _ID, DATE, CATEGORY_1, CATEGORY_2, NEW_CONFIRM, CUM_CONFIRM, NEW_DEAD, CUM_DEAD 
                    FROM COVID_TB 
                    ORDER BY DATE
                """
                cursor.execute(sql)
            else:
                sql = """
                    SELECT _ID, DATE, CATEGORY_1, CATEGORY_2, NEW_CONFIRM, CUM_CONFIRM, NEW_DEAD, CUM_DEAD 
                    FROM COVID_TB 
                    WHERE DATE <= %s 
                    ORDER BY DATE
                """
                cursor.execute(sql, max_date)
            data = cursor.fetchall()
            covids = []
            for d in data:
                covids.append(Covid(
                    id=d['_ID'],
                    date=d['DATE'],
                    category_1=d['CATEGORY_1'],
                    category_2=d['CATEGORY_2'],
                    new_confirm=d['NEW_CONFIRM'],
                    cum_confirm=d['CUM_CONFIRM'],
                    new_dead=d['NEW_DEAD'],
                    cum_dead=d['CUM_DEAD']
                ))
        conn.close()
        return covids

    @staticmethod
    def get_by_date_locale(date=datetime.date.today(), locale='전국'):
        conn = open_helper.get_connection()
        with conn.cursor(open_helper.DictCursor) as cursor:
            sql = """
                SELECT _ID, DATE, CATEGORY_1, CATEGORY_2, NEW_CONFIRM, CUM_CONFIRM, NEW_DEAD, CUM_DEAD 
                FROM COVID_TB 
                WHERE DATE=%s AND CATEGORY_2=%s 
                ORDER BY DATE
            """
            cursor.execute(sql, (date, locale))
            data = cursor.fetchall()
            if len(data) > 0:
                d = data[0]
                ret = Covid(
                    id=d['_ID'],
                    date=d['DATE'],
                    category_1=d['CATEGORY_1'],
                    category_2=d['CATEGORY_2'],
                    new_confirm=d['NEW_CONFIRM'],
                    cum_confirm=d['CUM_CONFIRM'],
                    new_dead=d['NEW_DEAD'],
                    cum_dead=d['CUM_DEAD']
                )
            else:
                ret = None
        conn.close()
        return ret

    @staticmethod
    def get_as_dataframe(d_type: str, max_date=None):
        data = Covid.get_all(max_date)
        if d_type == 'confirm':
            return pd.DataFrame([[d.date, d.category_2, d.new_confirm] for d in data if d.category_1 in ['지역', '전국']], columns=['date', 'locale', 'new_confirm'])
        elif d_type == 'dead':
            return pd.DataFrame([[d.date, d.category_2, d.new_dead] for d in data if d.category_1 in ['지역', '전국']], columns=['date', 'locale', 'new_dead'])


    def __init__(self, id=-1, date: datetime.date = None, category_1: str = '', category_2: str = '',
                 new_confirm: int = -1, cum_confirm: int = -1, new_dead: int = -1,
                 cum_dead: int = -1):
        self.id = id
        self.date = date
        self.category_1 = category_1
        self.category_2 = category_2
        self.new_confirm = new_confirm
        self.cum_confirm = cum_confirm
        self.new_dead = new_dead
        self.cum_dead = cum_dead
