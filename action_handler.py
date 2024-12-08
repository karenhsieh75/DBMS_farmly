from db_utils import *        


# (server)if role == farmer:
# (server):conn.send(f'[INPUT]Please choose a following action :\n{list_option(farmer_action)}---> '.encode('utf-8'))
# (server) get_selection(conn, farmer_action)
# (server) 呼叫相應的函式 farmer_action = {  "view upload history":get_farmer_upload_records(),get_farmer_upload_records_db()
                        #                  "upload amount to an existing product batch":upload_to_existing_products(),get_farmer_products_db(),insert_product_upload_db()
                        #                  "create a new product batch and upload products":insert_new_product_and_upload(),insert_new_product_and_upload_db()
                        #                  "search for markets available for registration":get_open_markets(),get_open_markets_db()
                        #                  "view market stall registration history":get_farmer_market_registrations(),get_farmer_market_registrations_db()
                        #                  "register for a new market":register_market(),register_market_db()
                        #                  "view my rating scores":get_farmer_ratings(),get_farmer_ratings_db()
#                                       }



consumer_action_basic = ['search for product', #step1
                   'view cart', #step1
                   'view order history',
                   'rate a farmer',
                   'view past ratings']

consumer_action_advance_searchforproduct = ['search for product', #step1
                   'add this product to cart', #step2
                   'view cart', #step1
                   'view order history',
                   'rate a farmer',
                   'view past ratings']

consumer_action_advance_viewcart = ['search for product', #step1
                   'view cart', #step1
                   'remove products from cart', #step2
                   'purchase products from cart', #step2
                   'view order history',
                   'rate a farmer',
                   'view past ratings']

# (server) if role == consumer:
#             if consumer is now after 'search for product':
#                 consumer_action_list = consumer_action_advance_searchforproduct
#             elif consumer is now after 'view cart':
#                 consumer_action_list = consumer_action_advance_viewcart
#             else:
#                 consumer_action_list = consumer_action_basic
# (server) conn.send(f'[INPUT]Please choose a following action :\n{list_option(consumer_action_list)}---> '.encode('utf-8'))
# (server) get_selection(conn, consumer_action)
# (server) 呼叫相應的函式 consumer_action = {"search for product":get_available_products(),get_available_products_db()
#                    "add this product to cart":add_to_cart(),add_to_cart_db()
#                    "view cart":get_cart_contents(),get_cart_contents_db()
#                    "remove some products from cart":remove_from_cart(),remove_from_cart_db()
#                    "purchase product from cart":purchase_products(),purchase_products_db()
#                    "view order history":get_consumer_order_history(),get_consumer_order_history_db()
#                    "rate a farmer":add_consumer_rating(),add_consumer_rating_db()
#                    "view past ratings":get_consumer_ratings(),get_consumer_ratings_db()
# }

    


def list_option(list):
    list_string = '\n'.join(list)
    return list_string

def read_input(conn, show_str):
        ret = conn.send(f'[INPUT]Please enter {show_str}: '.encode('utf-8'))
        recv_msg = conn.recv(100).decode("utf-8")
        return recv_msg


# welcome action
def farmer_signup(conn):
    from role.farmer import Farmer  # 延遲導入避免循環引用

    show_str_farmer_signup = ["your name","your phone number","your address","your farm_address","your password","your email"]
    name = read_input(conn, show_str_farmer_signup[0])
    phone_number = read_input(conn, show_str_farmer_signup[1])
    address = read_input(conn, show_str_farmer_signup[2])
    farm_address = read_input(conn, show_str_farmer_signup[3])
    password = read_input(conn, show_str_farmer_signup[4])
    email = read_input(conn, show_str_farmer_signup[5])
    
    # 調用 farmer_signup_db 並獲取返回值
    result = farmer_signup_db(name, phone_number, address, farm_address, password, email)

    # 根據返回值處理反饋
    if result["success"]:
        farmer_id = result['farmer_id']
        conn.send(f"Registration successful! Welcome, Farmer #{farmer_id}.\n".encode('utf-8'))
    else:
        conn.send(f"Registration failed: {result['message']}\n".encode('utf-8'))
    
    return Farmer(farmer_id, name, password, phone_number, email, address, farm_address)


def consumer_signup(conn):
    from role.consumer import Consumer

    show_str_consumer_signup = ["your name", "your email", "your phone number", "your address", "your password"]
    # 提示用戶輸入信息
    name = read_input(conn, show_str_consumer_signup[0])
    email = read_input(conn, show_str_consumer_signup[1])
    phone_number = read_input(conn, show_str_consumer_signup[2])
    address = read_input(conn, show_str_consumer_signup[3])
    password = read_input(conn, show_str_consumer_signup[4])

    # 調用 consumer_signup_db 並獲取返回值
    result = consumer_signup_db(name, email, phone_number, address, password)

    # 根據返回值處理反饋
    if result["success"]:
        consumer_id = result['consumer_id']
        conn.send(f"Registration successful! Welcome, Consumer #{consumer_id}.\n".encode('utf-8'))
    else:
        conn.send(f"Registration failed: {result['message']}\n".encode('utf-8'))
    return Consumer(consumer_id, name, password, phone_number, email, address)


def farmer_login(conn):
    from role.farmer import Farmer

    show_str_farmer_login = ["your phone", "your password"]
    
    # 提示用戶輸入手機號碼和密碼
    phone = read_input(conn, show_str_farmer_login[0])
    password = read_input(conn, show_str_farmer_login[1])

    # 調用 farmer_login_db 函數進行登錄驗證
    result = farmer_login_db(phone, password)

    # 根據登錄結果處理反饋
    if result["success"]:
        farmer_id, name, password, phone_number, email, address, farm_address = result['farmer_info']
        conn.send(f"Farmer login successful! Welcome, Farmer #{farmer_id}.\n".encode('utf-8'))
    else:
        conn.send(f"Login failed: {result['message']}\n".encode('utf-8'))
    
    return Farmer(farmer_id, name, password, phone_number, email, address, farm_address)

def consumer_login(conn):
    from role.consumer import Consumer
    show_str_consumer_login = ["your phone", "your password"]
    
    # 提示用戶輸入手機號碼和密碼
    phone = read_input(conn, show_str_consumer_login[0])
    password = read_input(conn, show_str_consumer_login[1])

    # 調用 consumer_login_db 函數進行登錄驗證
    result = consumer_login_db(phone, password)

    # 根據登錄結果處理反饋
    if result["success"]:
        role = 'consumer'
        consumer_id, name, password, phone_number, email, address = result['consumer_info']
        conn.send(f"Consumer login successful! Welcome, Consumer #{consumer_id}.\n".encode('utf-8'))
    else:
        conn.send(f"Login failed: {result['message']}\n".encode('utf-8'))
    
    return Consumer(consumer_id, name, password, phone_number, email, address)

def exit(conn, user=None):
    conn.send(f'[EXIT]Exit system. Bye~\n'.encode('utf-8'))
    return -1
    

#farmer_action
def get_farmer_upload_records(conn, user):
    get_farmer_upload_records_db(conn, user.get_user_id())
    return

def upload_to_existing_products(conn, user):
    get_farmer_products_db(conn, user.get_user_id())
    conn.send(f'\n'.encode('utf-8'))
    product_id = read_input(conn,"the product_id of the product that you'd like to add amount to")
    upload_quantity = read_input(conn,"the amount (numerical) you wish to add to this product")
    insert_product_upload_db(conn, user.get_user_id(), product_id, upload_quantity)
    return

def insert_new_product_and_upload(conn, user):
    product_name = read_input(conn,"the name of the product that you'd like to upload")
    product_type = read_input(conn,"the type of the product that you'd like to upload")
    unit = read_input(conn,"the unit of the product that you'd like to upload")
    weight = read_input(conn,"the weight per unit of the product that you'd like to upload")
    harvest_date = read_input(conn,"the harvest date of the product that you'd like to upload")
    exp_date = read_input(conn,"the expiration date of the product that you'd like to upload")
    price = read_input(conn,"the price per unit of the product that you'd like to upload")
    upload_quantity = read_input(conn,"the amount of the product that you'd like to upload")
    insert_new_product_and_upload_db(conn, user.get_user_id(), product_name, product_type, unit, weight, harvest_date, exp_date, price, upload_quantity)
    return

def get_open_markets(conn, user):
    get_open_markets_db(conn)
    return

def get_farmer_market_registrations(conn, user):
    get_farmer_market_registrations_db(conn, user.get_user_id())
    return

def register_market(conn, user):
    market_id = read_input(conn,"the market_id of the market you'd like to register for")
    register_market_db(conn, user.get_user_id(), market_id)
    return

def get_farmer_ratings(conn, user):
    get_farmer_ratings_db(conn, user.get_user_id())
    return



# consumer_action
def get_available_products(conn, user):
    product_type = read_input(conn, "the type of the product that you'd like to search")
    exp_date = read_input(conn, "the expiration date after which you'd like to search")
    get_available_products_db(conn, product_type, exp_date)
    return


def add_to_cart(conn, user):
    product_id = read_input(conn, "the product ID of the item you'd like to add to your cart")
    quantity = read_input(conn, "the quantity of the product you'd like to add to your cart")
    add_to_cart_db(user.get_user_id(), product_id, quantity)
    return


def get_cart_contents(conn, user):
    get_cart_contents_db(conn, user.get_user_id())
    return


def remove_from_cart(conn, user):
    product_id = read_input(conn, "the product ID of the item you'd like to remove from your cart")
    quantity = read_input(conn, "the quantity of the product you'd like to remove from your cart")
    remove_from_cart_db(user.get_user_id(), product_id, quantity)
    return



def purchase_products(conn, user):
    # 讀取必要的輸入
    product_quantities = {}
    while True:
        product_id = read_input(conn, "the product ID you'd like to purchase, type 'end' to end product selection")
        if product_id == 'end':
            break    
        elif not check_if_productid_in_cart_db(user.get_user_id(), product_id):
            continue  # 讓用戶再次輸入
        quantity = int(read_input(conn, f"the quantity of product #{product_id} you'd like to purchase"))
        product_quantities[product_id] = quantity

    payment_type = read_input(conn, "your payment type (select between Card, Bank Transfer or Line Pay)")
    shipping_address = read_input(conn, "your shipping address")
    shipping_type = read_input(conn, "your shipping type (select between Standard, Refrigerated or Frozen)")
    purchase_products_db(user.get_user_id(), product_quantities, payment_type, shipping_address, shipping_type)
    return


def get_consumer_order_history(conn, user):
    get_consumer_order_history_db(conn, user.get_user_id())
    return 

def add_consumer_rating(conn, user):
    # 讀取評價資料
    farmer_id = read_input(conn, "the farmer ID you want to rate")
    rating = int(read_input(conn, "the rating (1 to 5)"))
    comment = read_input(conn, "your comment (optional)")

    # 呼叫資料庫操作的函數
    add_consumer_rating_db(user.get_user_id(), farmer_id, rating, comment)
    return

def get_consumer_ratings(conn, user):
    # 呼叫資料庫操作的函數來查詢消費者的評價
    get_consumer_ratings_db(conn, user.get_user_id())
    return



