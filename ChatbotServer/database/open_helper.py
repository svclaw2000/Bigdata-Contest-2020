import pymysql
from config.config_handler import ConfigParser
from pymysql.cursors import DictCursor

def get_config():
    config = ConfigParser()
    config.load_from_file('config/mysql.conf')
    return config

def get_connection():
    try:
        config = get_config()
        return pymysql.connect(host=config['host'],
                               port=config['port'],
                               database=config['database'],
                               user=config['user'],
                               passwd=config['passwd'])
    except:
        return None

def check_connection():
    conn = get_connection()
    if conn:
        conn.close()
        return True
    else:
        return False