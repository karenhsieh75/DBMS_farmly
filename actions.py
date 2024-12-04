import sys
import psycopg2
# from tabulate import tabulate
from threading import Lock

DB_NAME = "I'M_IN"
DB_USER = "dbta"
DB_HOST = "127.0.0.1"
DB_PORT = 5432

cur = None
db = None
create_event_lock = Lock()


def db_connect():
    exit_code = 0
    try:
        global db
        db = psycopg2.connect(database=DB_NAME, user=DB_USER, password='1234', 
                              host=DB_HOST, port=DB_PORT)
        print("Successfully connect to DBMS.")
        global cur
        cur = db.cursor()
        return db
        
    except psycopg2.Error as err:
        print("DB error: ", err)
        exit_code = 1
    except Exception as err:
        print("Internal Error: ", err)
        raise err
    # finally:
    #     if db is not None:
    #         db.close()
    sys.exit(exit_code)



def leave_study_group(conn, user_id, event_id):

    # if not isInEvent(user_id, event_id):
    #         conn.send(f'\nYou are not in this event!\n'.encode('utf-8'))
    #         return

    query = """
            Delete From "PARTICIPATION"
            Where Event_id = %s And User_id = %s;
            """
    
    cur.execute(query, [event_id, user_id])
    db.commit()

    conn.send(f'\nLeave study group successfully!\n'.encode('utf-8'))


def alter_cart():
    # sql query 跟 server 查詢/新增/修改資料
    # 用 conn.send 傳送結果或訊息給 client 
    pass



