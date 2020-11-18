import json
from database import open_helper
import datetime

class Festival:
    @staticmethod
    def reset_table():
        conn = open_helper.get_connection()
        with conn.cursor() as cursor:
            sql = "DROP TABLE IF EXISTS FESTIVAL_TB"
            cursor.execute(sql)

            sql = """
            CREATE TABLE IF NOT EXISTS FESTIVAL_TB (
            _ID INT PRIMARY KEY AUTO_INCREMENT,
            NAME VARCHAR(64) NOT NULL,
            PROVINCE VARCHAR(16),
            CITY VARCHAR(16),
            START DATE,
            END DATE,
            TIME VARCHAR(128),
            CONTACT VARCHAR(64)
            )
            """
            cursor.execute(sql)
        conn.commit()
        conn.close()

    @staticmethod
    def insert(fests):
        conn = open_helper.get_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO FESTIVAL_TB (NAME, PROVINCE, CITY, START, END, TIME, CONTACT) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
            for fest in fests:
                cursor.execute(sql,
                               (fest.name, fest.province, fest.city, fest.start, fest.end, fest.time, fest.contact))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        conn = open_helper.get_connection()
        with conn.cursor(open_helper.DictCursor) as cursor:
            sql = """
                SELECT _ID, NAME, PROVINCE, CITY, START, END, TIME, CONTACT 
                FROM FESTIVAL_TB
            """
            cursor.execute(sql)
            data = cursor.fetchall()
            fests = []
            for d in data:
                fests.append(Festival(id=d['_ID'],
                                      name=d['NAME'],
                                      province=d['PROVINCE'],
                                      city=d['CITY'],
                                      start=d['START'],
                                      end=d['END'],
                                      time=d['TIME'],
                                      contact=d['CONTACT']))
        conn.close()
        return fests

    @staticmethod
    def get_from_date_locale(date=datetime.date.today(), province=None, city=None):
        if province is None and city is None:
            return None

        conn = open_helper.get_connection()
        with conn.cursor(open_helper.DictCursor) as cursor:
            if province is not None:
                if city is not None:
                    sql = """
                        SELECT _ID, NAME, PROVINCE, CITY, START, END, TIME, CONTACT 
                        FROM FESTIVAL_TB 
                        WHERE %s >= START AND %s <= END AND PROVINCE=%s AND CITY=%s
                    """
                    cursor.execute(sql, (date, date, province, city))
                else:
                    sql = """
                        SELECT _ID, NAME, PROVINCE, CITY, START, END, TIME, CONTACT 
                        FROM FESTIVAL_TB 
                        WHERE %s >= START AND %s <= END AND PROVINCE=%s
                    """
                    cursor.execute(sql, (date, date, province))
            else:
                sql = """
                    SELECT _ID, NAME, PROVINCE, CITY, START, END, TIME, CONTACT 
                    FROM FESTIVAL_TB 
                    WHERE %s >= START AND %s <= END AND CITY=%s
                """
                cursor.execute(sql, (date, date, city))
            data = cursor.fetchall()
            fests = []
            for d in data:
                fests.append(Festival(id=d['_ID'],
                                      name=d['NAME'],
                                      province=d['PROVINCE'],
                                      city=d['CITY'],
                                      start=d['START'],
                                      end=d['END'],
                                      time=d['TIME'],
                                      contact=d['CONTACT']))
        conn.close()
        return fests

    def __init__(self, id=-1, name='', province: str = None, city: str = None, start: datetime.date = None, end: datetime.date = None,
                 time: str = None, contact: str = None):
        self.id = id
        self.name = name
        self.province = province
        self.city = city
        self.start = start
        self.end = end
        self.time = time
        self.contact = contact

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'province': self.province,
            'city': self.city,
            'start': self.start.strftime('%Y-%m-%d'),
            'end': self.end.strftime('%Y-%m-%d'),
            'time': self.time,
            'contact': self.contact
        }

    def to_json_string(self):
        return json.dumps(self.to_json())