import sys
import psycopg2
from tabulate import tabulate
from threading import Lock

DB_NAME = "Farmly"
DB_USER = "postgres"
DB_HOST = "127.0.0.1"
DB_PORT = 5432

cur = None
db = None
create_event_lock = Lock()

def db_connect():

    try:
        global db
        db = psycopg2.connect(database=DB_NAME, user=DB_USER, password='password', 
                              host=DB_HOST, port=DB_PORT)
        print("Successfully connect to DBMS.")
        global cur
        cur = db.cursor()
        return db
        
    except psycopg2.Error as err:
        print("DB error: ", err)
        return None, None

    except Exception as err:
        print("Internal Error: ", err)
        raise err

    
def print_table(cur, conn):
    # 從游標中取得所有行
    rows = cur.fetchall()
    
    # 提取列名（欄位名稱）
    columns = [desc[0] for desc in cur.description]
    
    # 使用tabulate格式化數據為表格字串
    table_str = tabulate(rows, headers=columns, tablefmt="github")
    
    conn.send(table_str.encode('utf-8'))  # 需要先將表格字串編碼為字節串傳送

# ------------------------------- functions for farmer ------------------------------------

def farmer_signup_db(name, phone_number, address, farm_address, password, email):
    try:
        # 檢查 phone_number 是否已存在（加鎖：For Update，確保一致性）
        check_phone_query = """
            SELECT farmer_id
            FROM Farmer
            WHERE phone = %s
            FOR UPDATE;
        """
        cur.execute(check_phone_query, [phone_number])
        existing_farmer = cur.fetchone()

        # 如果電話號碼已存在，則回滾並返回提示訊息
        if existing_farmer:
            db.rollback()
            print(f"電話號碼 {phone_number} 已經存在，無法註冊新農夫。")
            return {"success": False, "message": f"Phone number {phone_number} already exists."}

        # 插入新農夫資料
        insert_farmer_query = """
            INSERT INTO Farmer (name, phone, address, farm_address, password, email)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING farmer_id;
        """
        cur.execute(insert_farmer_query, [name, phone_number, address, farm_address, password, email])

        # 獲取新插入的 farmer_id
        new_farmer_id = cur.fetchone()[0]

        # 提交交易
        db.commit()
        print(f"農夫 {new_farmer_id} 已成功註冊。")
        return {"success": True, "farmer_id": new_farmer_id}

    except Exception as e:
        # 發生異常則回滾交易，並返回錯誤訊息
        db.rollback()
        print(f"註冊失敗，發生錯誤：{e}")
        return {"success": False, "message": str(e)}


def farmer_login_db(phone, password):
    try:
        # 檢查農夫的手機號碼和密碼是否匹配
        check_login_query = """
            SELECT *
            FROM Farmer
            WHERE phone = %s AND password = %s;
        """
        cur.execute(check_login_query, [phone, password])

        farmer = cur.fetchall()

        # 如果找不到匹配的農夫，則返回錯誤
        if not farmer:
            return {"success": False, "message": "Invalid phone number or password."}
        
        # 返回農夫的資訊，表示登錄成功
        farmer_id, name, phone_number, address, farm_address, password, email = farmer[0]
        
        return {"success": True, "farmer_info": [farmer_id, name, password, phone_number, email, address, farm_address]}

    except Exception as e:
        # 如果發生錯誤，則回滾交易並返回錯誤信息
        db.rollback()
        print(f"Login failed, error occurred: {e}")
        return {"success": False, "message": str(e)}


def get_farmer_products_db(conn, farmer_id):

    query = """
            SELECT product_id,
                   product_name,
                   product_type,
                   harvest_date
            FROM Product_batch
            WHERE farmer_id = %s
            ORDER BY harvest_date DESC;
            """
    cur.execute(query, [farmer_id])
    print_table(cur, conn)
    return 


def insert_product_upload_db(conn, farmer_id, product_id, upload_quantity):

    query = """
            INSERT INTO Product_upload_Batch (farmer_id, product_id, upload_quantity, upload_time)
            VALUES (%s, %s, %s, NOW());
            """
    cur.execute(query, [farmer_id, product_id, upload_quantity])
    db.commit()
    
    conn.send(f"Successfully added {upload_quantity} more of product #{product_id}!\n".encode('utf-8'))
    return


def insert_new_product_and_upload_db(conn, farmer_id, product_name, product_type, unit, weight, harvest_date, exp_date, price, upload_quantity):

    # 插入 product_batch 並獲取 product_id
    insert_product_query = """
        INSERT INTO Product_batch (farmer_id, product_name, product_type, unit, weight, harvest_date, exp_date, price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING product_id;
    """
    cur.execute(insert_product_query, [farmer_id, product_name, product_type, unit, weight, harvest_date, exp_date, price])
    product_id = cur.fetchone()[0]

    # 用獲取的 product_id 插入 product_upload_batch
    insert_upload_query = """
        INSERT INTO Product_upload_Batch (farmer_id, product_id, upload_quantity, upload_time)
        VALUES (%s, %s, %s, NOW());
    """
    cur.execute(insert_upload_query, [farmer_id, product_id, upload_quantity])

    conn.send(f"Successfully created new product #{product_id} and uploaded {upload_quantity} (unit = {unit})!\n".encode('utf-8'))
    db.commit()



def get_farmer_upload_records_db(conn, farmer_id):

    query = """
            SELECT pb.product_name,
                   pu.upload_quantity,
                   pu.upload_time,
                   pb.exp_date
            FROM Product_batch AS pb
            JOIN Product_upload_Batch AS pu ON pb.product_id = pu.product_id
            WHERE pb.farmer_id = %s
            ORDER BY pu.upload_time DESC;
            """
    cur.execute(query, [farmer_id])
    print_table(cur,conn)
    return 


# 小農查詢開放中市集
def get_open_markets_db(conn):

    query = """
        SELECT m.market_id,
               m.name AS market_name,
               m.start_date,
               m.end_date,
               COUNT(s.stall_id) - COUNT(sf.farmer_id) AS available_stalls
        FROM Market m
        JOIN Stall s ON m.market_id = s.market_id
        LEFT JOIN Stall_assign_farmer sf ON s.stall_id = sf.stall_id
        WHERE m.start_date > CURRENT_DATE
        GROUP BY m.market_id, m.name, m.start_date, m.end_date
        HAVING COUNT(s.stall_id) - COUNT(sf.farmer_id) > 0
        ORDER BY m.start_date ASC;
    """
    cur.execute(query)
    print_table(cur,conn)
    return 

def register_market_db(conn, farmer_id, market_id):

    # 檢查市集是否符合條件（加鎖：For Update）
    check_market_query = """
        WITH StallCounts AS (
            SELECT m.market_id,
                   COUNT(s.stall_id) AS total_stalls,
                   COUNT(sf.farmer_id) AS allocated_stalls
            FROM Market m
            JOIN Stall s ON m.market_id = s.market_id
            LEFT JOIN Stall_assign_farmer sf ON s.stall_id = sf.stall_id
            WHERE m.market_id = %s
              AND m.start_date > CURRENT_DATE
            GROUP BY m.market_id
        )
        SELECT sc.market_id
        FROM StallCounts sc
        WHERE sc.market_id = %s
          AND (sc.total_stalls - sc.allocated_stalls) > 0
        FOR UPDATE;
    """
    cur.execute(check_market_query, [market_id, market_id])
    result = cur.fetchone()

    # 如果市集不符合條件，則 rollback
    if not result:
        db.rollback()
        print(f"市集 {market_id} 未開放登記。")
        return False

    # 如果市集符合條件，在farmer_register_market新增記錄
    insert_register_query = """
        INSERT INTO Farmer_register_market (farmer_id, market_id, register_time, status)
        VALUES (%s, %s, NOW(), 'Registered');
    """
    cur.execute(insert_register_query, [farmer_id, market_id])

    db.commit()
    conn.send(f"Successfully registered market #{market_id} for farmer #{farmer_id}!\n".encode('utf-8'))
    return True


# 小農查詢攤位登記記錄
def get_farmer_market_registrations_db(conn, farmer_id):

    query = """
            SELECT fr.market_id,
                   m.name AS market_name,
                   fr.register_time,
                   fr.status
            FROM Farmer_register_market AS fr
            JOIN Market AS m ON fr.market_id = m.market_id
            WHERE fr.farmer_id = %s
            ORDER BY fr.register_time DESC;
            """
    cur.execute(query, [farmer_id])
    print_table(cur,conn)
    return 


# 小農查詢評分紀錄
def get_farmer_ratings_db(conn, farmer_id):

    query = """
            SELECT rate_date,
                   consumer_id,
                   rating,
                   comment
            FROM Consumer_rate_Farmer AS crf
            WHERE farmer_id = %s
            ORDER BY rating DESC, rate_date DESC;
            """
    cur.execute(query, [farmer_id])
    print_table(cur,conn)
    return 



# ------------------------------- functions for user --------------------------------------

def consumer_signup_db(name, email, phone_number, address, password):
    try:
        # 檢查 phone_number 是否已存在於 Consumer 表中（加鎖：For Update，確保一致性）
        check_phone_query = """
            SELECT consumer_id
            FROM Consumer
            WHERE phone = %s
            FOR UPDATE;
        """
        cur.execute(check_phone_query, [phone_number])
        existing_consumer = cur.fetchone()

        # 如果電話號碼已存在，則回滾並返回提示訊息
        if existing_consumer:
            db.rollback()
            print(f"電話號碼 {phone_number} 已經存在，無法註冊新消費者。")
            return {"success": False, "message": f"Phone number {phone_number} already exists."}

        # 插入新消費者資料
        insert_consumer_query = """
            INSERT INTO Consumer (name, email, phone, address, password)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING consumer_id;
        """
        cur.execute(insert_consumer_query, [name, email, phone_number, address, password])

        # 獲取新插入的 consumer_id
        new_consumer_id = cur.fetchone()[0]

        # 提交交易
        db.commit()
        print(f"消費者 {new_consumer_id} 已成功註冊。")
        return {"success": True, "consumer_id": new_consumer_id}

    except Exception as e:
        # 發生異常則回滾交易，並返回錯誤訊息
        db.rollback()
        print(f"註冊失敗，發生錯誤：{e}")
        return {"success": False, "message": str(e)}
    

def consumer_login_db(phone, password):
    try:
        # 檢查消費者的手機號碼和密碼是否匹配
        check_login_query = """
            SELECT *
            FROM Consumer
            WHERE phone = %s AND password = %s;
        """
        cur.execute(check_login_query, [phone, password])
        consumer = cur.fetchall()

        # 如果找不到匹配的農夫，則返回錯誤
        if not consumer:
            return {"success": False, "message": "Invalid phone number or password."}
        
        # 返回消費者的資訊，表示登錄成功
        consumer_id, name, email, phone_number, address, password = consumer[0]
        
        return {"success": True, "consumer_info": [consumer_id, name, password, phone_number, email, address]}

    except Exception as e:
        # 如果發生錯誤，則回滾交易並返回錯誤信息
        db.rollback()
        print(f"Login failed, error occurred: {e}")
        return {"success": False, "message": str(e)}



def get_available_products_db(conn, product_type, exp_date):

    query = """
            SELECT pb.product_id,
                   pb.product_name,
                   pb.unit,
                   pb.weight,
                   pb.price,
                   SUM(pu.upload_quantity) - COALESCE(SUM(ocp.quantity), 0) AS available_stock
            FROM Product_batch pb
            JOIN Product_upload_Batch pu ON pb.product_id = pu.product_id
            LEFT JOIN Order_contain_product ocp ON pb.product_id = ocp.product_id
            LEFT JOIN Consumer_order co ON ocp.order_id = co.order_id AND co.status IN ('Paid', 'Completed')
            WHERE pb.exp_date > %s
              AND pb.product_type = %s
            GROUP BY pb.product_id, pb.product_name, pb.unit, pb.weight, pb.price
            HAVING SUM(pu.upload_quantity) - COALESCE(SUM(ocp.quantity), 0) > 0;
            """
    cur.execute(query, [exp_date, product_type])
    print_table(cur,conn)
    return 


def add_to_cart_db(conn, consumer_id, product_id, quantity):

    # 交易開始
    # db.autocommit = False

    # 1：檢查存貨是否足夠
    check_stock_query = """
            WITH AvailableStock AS (
                SELECT pu.product_id,
                       SUM(pu.upload_quantity) - COALESCE(SUM(ocp.quantity), 0) AS available_stock
                FROM Product_upload_Batch pu
                LEFT JOIN Order_contain_product ocp ON pu.product_id = ocp.product_id
                WHERE pu.product_id = %s
                GROUP BY pu.product_id
            )
            SELECT product_id
            FROM AvailableStock
            WHERE available_stock >= %s
            FOR UPDATE;
        """
    cur.execute(check_stock_query, [product_id, quantity])
    result = cur.fetchone()

    # 若存貨不足，則rollback
    if not result:
        db.rollback()
        # db.autocommit = True
        print(f"product #{product_id} inventory not enough")
        return False

    # 2：將商品新增至購物車
    insert_cart_query = """
        INSERT INTO Consumer_alter_Cart (consumer_id, product_id, alter_type, alter_quantity, alter_time)
        VALUES (%s, %s, 'Increase', %s, NOW());
    """
    cur.execute(insert_cart_query, [consumer_id, product_id, quantity])

    db.commit()
    # db.autocommit = True
    conn.send(f"product #{product_id} x {quantity} successfully added to cart\n".encode('utf-8'))
    return True


def get_cart_contents_db(conn, consumer_id):

    query = """
        SELECT cac.product_id,
               pb.product_name,
               pb.product_type,
               SUM(CASE WHEN cac.alter_type = 'Increase' THEN cac.alter_quantity ELSE -cac.alter_quantity END) AS current_quantity
        FROM Consumer_alter_Cart cac
        JOIN Product_batch pb ON cac.product_id = pb.product_id
        WHERE cac.consumer_id = %s
        GROUP BY cac.product_id, pb.product_name, pb.product_type
        HAVING SUM(CASE WHEN cac.alter_type = 'Increase' THEN cac.alter_quantity ELSE -cac.alter_quantity END) > 0
        ORDER BY pb.product_name ASC;
    """

    cur.execute(query, [consumer_id])
    print_table(cur,conn)
    return 


def remove_from_cart_db(conn, consumer_id, product_id, quantity):

    # 交易開始
    #db.autocommit = False

    # 1：檢查現有數量是否足夠減少
    check_quantity_query = """
        SELECT SUM(CASE WHEN alter_type = 'Increase' THEN alter_quantity ELSE -alter_quantity END) AS current_quantity
        FROM Consumer_alter_Cart
        WHERE consumer_id = %s AND product_id = %s
        GROUP BY product_id
        HAVING SUM(CASE WHEN alter_type = 'Increase' THEN alter_quantity ELSE -alter_quantity END) >= %s;
    """
    cur.execute(check_quantity_query, [consumer_id, product_id, quantity])
    result = cur.fetchone()

    # 若數量不足，則rollback
    if not result:
        db.rollback()
        #db.autocommit = True
        print(f"product #{product_id} amount in cart not enough to reduce {quantity}.")
        return False

    # 2：新增減少數量的記錄
    insert_cart_query = """
        INSERT INTO Consumer_alter_Cart (consumer_id, product_id, alter_type, alter_quantity, alter_time)
        VALUES (%s, %s, 'Decrease', %s, NOW());
    """
    cur.execute(insert_cart_query, [consumer_id, product_id, quantity])

    db.commit()
    #db.autocommit = True
    conn.send(f"successfully reduced product {quantity} of product #{product_id} from cart.\n".encode('utf-8'))
    return True


def check_if_productid_in_cart_db(conn, consumer_id, product_id):
    # 1：查詢購物車中所有的 product_id
    query = """
        SELECT cac.product_id
        FROM Consumer_alter_Cart cac
        WHERE cac.consumer_id = %s
        GROUP BY cac.product_id
        HAVING SUM(CASE WHEN cac.alter_type = 'Increase' THEN cac.alter_quantity ELSE -cac.alter_quantity END) > 0;
    """
    cur.execute(query, [consumer_id])
    cart_products = [row[0] for row in cur.fetchall()]  # 取得所有的 product_id

    # 2：檢查輸入的 product_id 是否在購物車內
    if int(product_id) in cart_products:
        return True  # Product is in cart
    else:
        conn.send(f"Product #{product_id} is not in your cart. Please add it to your cart first.\n".encode('utf-8'))
        return False  # Product is not in cart


def purchase_products_db(conn, consumer_id, product_quantities, payment_type, shipping_address, shipping_type):
    """
        product_quantities: 商品和購買數量字典，例如 {101916: 5, 102234: 3}
    """
    try:
        # 交易開始
        #db.autocommit = False

        total_price = 0

        # 1：檢查所有商品庫存(加鎖)
        for product_id, quantity in product_quantities.items():
            check_stock_query = """
            WITH AvailableStock AS (
                SELECT pu.product_id,
                       SUM(pu.upload_quantity) - COALESCE(SUM(ocp.quantity), 0) AS available_stock
                FROM Product_upload_Batch pu
                LEFT JOIN Order_contain_product ocp ON pu.product_id = ocp.product_id
                WHERE pu.product_id = %s
                GROUP BY pu.product_id
            )
            SELECT product_id
            FROM AvailableStock
            WHERE available_stock >= %s
            FOR UPDATE;
            """
            cur.execute(check_stock_query, [product_id, quantity])
            result = cur.fetchone()

            if not result:
                db.rollback()
                conn.send(f"product #{product_id} inventory not enough for purchase\n".encode('utf-8'))
                return False

            # 計算 total price
            cur.execute("SELECT price FROM Product_batch WHERE product_id = %s", [product_id])
            price = cur.fetchone()[0]
            total_price += price * quantity

            # 在購物車裡面插入減少紀錄
            insert_cart_decrease_query = """
                INSERT INTO Consumer_alter_Cart (consumer_id, product_id, alter_type, alter_quantity, alter_time)
                VALUES (%s, %s, 'Decrease', %s, NOW());
            """
            cur.execute(insert_cart_decrease_query, [consumer_id, product_id, quantity])

        # 2：插入訂單
        create_order_query = """
            INSERT INTO Consumer_order (consumer_id, total_price, create_time, payment_type, shipping_address, shipping_type)
            VALUES (%s, %s, NOW(), %s, %s, %s)
            RETURNING order_id;
        """
        cur.execute(create_order_query, [consumer_id, total_price, payment_type, shipping_address, shipping_type])
        order_id = cur.fetchone()[0]

        # 3：插入訂單商品
        insert_order_item_query = """
            INSERT INTO Order_contain_product (order_id, product_id, quantity)
            VALUES (%s, %s, %s);
        """
        for product_id, quantity in product_quantities.items():
            cur.execute(insert_order_item_query, [order_id, product_id, quantity])

        # 交易結束
        db.commit()
        # db.autocommit = True
        conn.send(f"Successfully placed order #{order_id}:\n consumer_id:{consumer_id}, product_quantities:{product_quantities}, payment_type:{payment_type}, shipping_address:{shipping_address}, shipping_type:{shipping_type}\n".encode('utf-8'))
        return True

    except Exception as e:
        db.rollback()
        # db.autocommit = True
        conn.send(f"Error: {e}\n".encode('utf-8'))
        return False


def get_consumer_order_history_db(conn, consumer_id):

    query = """
            SELECT co.order_id,
                   co.create_time,
                   co.total_price,
                   co.status,
                   pb.product_name,
                   pb.price,
                   ocp.quantity
            FROM Consumer_order co
            JOIN Order_contain_product ocp ON co.order_id = ocp.order_id
            JOIN Product_batch pb ON ocp.product_id = pb.product_id
            WHERE co.consumer_id = %s
            ORDER BY co.create_time DESC;
            """
    cur.execute(query, [consumer_id])
    print_table(cur,conn)
    return 


# 消費者新增評分
def add_consumer_rating_db(conn, consumer_id, farmer_id, rating, comment):

    query = """
            INSERT INTO Consumer_rate_Farmer (consumer_id, farmer_id, rate_date, rating, comment)
            VALUES (%s, %s, NOW(), %s, %s);
            """
    cur.execute(query, [consumer_id, farmer_id, rating, comment])
    db.commit()
    conn.send(f"Successfully rated farmer #{farmer_id} score of {rating}\n".encode('utf-8'))
    return


# 消費者查詢評分紀錄
def get_consumer_ratings_db(conn, consumer_id):

    query = """
            SELECT crf.rate_date,
                   f.name AS farmer_name,
                   crf.rating,
                   crf.comment
            FROM Consumer_rate_Farmer AS crf
            JOIN Farmer AS f ON crf.farmer_id = f.farmer_id
            WHERE crf.consumer_id = %s
            ORDER BY crf.rate_date DESC;
            """
    cur.execute(query, [consumer_id])
    print_table(cur,conn)
    return 
