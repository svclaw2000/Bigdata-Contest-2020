import json
from database import open_helper


class Clinic:
    @staticmethod
    def reset_table():
        conn = open_helper.get_connection()
        with conn.cursor() as cursor:
            sql = "DROP TABLE IF EXISTS CLINIC_TB"
            cursor.execute(sql)

            sql = """
            CREATE TABLE IF NOT EXISTS CLINIC_TB (
            _ID INT PRIMARY KEY AUTO_INCREMENT,
            PROVINCE VARCHAR(16),
            CITY VARCHAR(16),
            NAME VARCHAR(64) NOT NULL,
            ADDRESS VARCHAR(256),
            LOCATION POINT,
            WEEKDAY VARCHAR(32),
            SATURDAY VARCHAR(32),
            HOLIDAY VARCHAR(32),
            CONTACT VARCHAR(64)
            )
            """
            cursor.execute(sql)
        conn.commit()
        conn.close()

    @staticmethod
    def insert(clinics):
        conn = open_helper.get_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO CLINIC_TB (PROVINCE, CITY, NAME, ADDRESS, LOCATION, WEEKDAY, SATURDAY, HOLIDAY, CONTACT) 
                VALUES (%s, %s, %s, %s, POINT(%s, %s), %s, %s, %s, %s)
                """
            for clinic in clinics:
                cursor.execute(sql,
                               (clinic.province, clinic.city, clinic.name, clinic.address, clinic.location[0], clinic.location[1],
                                clinic.weekday, clinic.saturday, clinic.holiday, clinic.contact))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        conn = open_helper.get_connection()
        with conn.cursor(open_helper.DictCursor) as cursor:
            sql = """
                SELECT _ID, PROVINCE, CITY, NAME, ADDRESS, LOCATION, WEEKDAY, SATURDAY, HOLIDAY, CONTACT 
                FROM CLINIC_TB
            """
            cursor.execute(sql)
            data = cursor.fetchall()
            clinics = []
            for d in data:
                clinics.append(Clinic(
                    id=d['_ID'],
                    province=d['PROVINCE'],
                    city=d['CITY'],
                    name=d['NAME'],
                    address=d['ADDRESS'],
                    location=d['LOCATION'],
                    weekday=d['WEEKDAY'],
                    saturday=d['SATURDAY'],
                    holiday=d['HOLIDAY'],
                    contact=d['CONTACT']
                ))
        conn.close()
        return clinics

    @staticmethod
    def get_from_locale(province=None, city=None):
        if province is None and city is None:
            return None

        conn = open_helper.get_connection()
        with conn.cursor(open_helper.DictCursor) as cursor:
            if province is not None:
                if city is not None:
                    sql = """
                        SELECT _ID, PROVINCE, CITY, NAME, ADDRESS, LOCATION, WEEKDAY, SATURDAY, HOLIDAY, CONTACT 
                        FROM CLINIC_TB
                        WHERE PROVINCE=%s AND CITY=%s
                    """
                    cursor.execute(sql, (province, city))
                else:
                    sql = """
                        SELECT _ID, PROVINCE, CITY, NAME, ADDRESS, LOCATION, WEEKDAY, SATURDAY, HOLIDAY, CONTACT 
                        FROM CLINIC_TB
                        WHERE PROVINCE=%s
                    """
                    cursor.execute(sql, (province,))
            else:
                sql = """
                    SELECT _ID, PROVINCE, CITY, NAME, ADDRESS, LOCATION, WEEKDAY, SATURDAY, HOLIDAY, CONTACT 
                    FROM CLINIC_TB
                    WHERE CITY=%s
                """
                cursor.execute(sql, (city,))
            data = cursor.fetchall()
            clinics = []
            for d in data:
                clinics.append(Clinic(
                    id=d['_ID'],
                    province=d['PROVINCE'],
                    city=d['CITY'],
                    name=d['NAME'],
                    address=d['ADDRESS'],
                    location=d['LOCATION'],
                    weekday=d['WEEKDAY'],
                    saturday=d['SATURDAY'],
                    holiday=d['HOLIDAY'],
                    contact=d['CONTACT']
                ))
        conn.close()
        return clinics

    def __init__(self, id=-1, province: str = None, city: str = None, name: str = '', address: str = None,
                 location: tuple = None, weekday: str = None, saturday: str = None, holiday: str = None,
                 contact: str = None):
        self.id = id
        self.province = province
        self.city = city
        self.name = name
        self.address = address
        self.location = location
        self.weekday = weekday
        self.saturday = saturday
        self.holiday = holiday
        self.contact = contact

    def to_json(self):
        return {
            'id': self.id,
            'province': self.province,
            'city': self.city,
            'name': self.name,
            'address': self.address,
            'location': self.location,
            'weekday': self.weekday,
            'saturday': self.saturday,
            'holiday': self.holiday,
            'contact': self.contact
        }

    def to_json_string(self):
        return json.dumps(self.to_json())
