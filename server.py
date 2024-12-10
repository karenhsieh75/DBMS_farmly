import socket
import traceback
from threading import Thread

from db_utils import *
from action_handler import *
from helper import *


welcome_action = ['farmer_signup', 'consumer_signup', 'farmer_login', 'consumer_login', 'exit']  


def handle_connection(conn, client_addr):
    try:
        
        while True: # Welcome Page
            conn.send("----------------------------------------\nWelcome to Farmly!\n".encode('utf-8'))
            conn.send(f'[INPUT]Please select your action:\n{list_option(welcome_action)}---> '.encode('utf-8'))
            action_str = get_selection(conn, welcome_action)


            # 獲取函數並執行
            if action_str in globals():
                func_to_call = globals()[action_str]
                if callable(func_to_call):
                    user = func_to_call(conn)
                else:
                    print(f"{action_str} is not callable.")
            else:
                print(f"{action_str} does not exist.")


            if user == -1:
                raise Exception("End connection")
            
            send_msg =  f'\n----------------------------------------\n\nHi {user.get_username()}!\n' + \
                        f'[ User Info ] {user.get_info_msg_no_pwd()}\n'
            conn.send(send_msg.encode('utf-8'))

            while True: # Function Page
                
                conn.send(f'\n----------------------------------------\n\n'.encode('utf-8'))
                actions = user.get_available_action()
                conn.send(f'[INPUT]Please select your option:\n{list_option(actions)}---> '.encode('utf-8'))
                action_atr = get_selection(conn, actions)
                func_to_call = user.get_function_name(action_atr)
                ret = func_to_call(conn, user)

                if ret == -1:
                    break

    except Exception as e:
        print(f"Connection with {client_addr} close.")
        print(f"Error occurred: {str(e)}")
        traceback.print_exc()  # 輸出完整的錯誤追蹤
        conn.close()
    finally:
        print(f"Connection with {client_addr} close.")
        conn.close()



if __name__ == '__main__':

    
    db = db_connect()
    cur = db.cursor()

    bind_ip = "127.0.0.1"
    bind_port = 8888

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((bind_ip, bind_port))
    server_socket.listen(5)

    print(f'Server listening on {bind_ip}:{bind_port} ...')


    try:
        while True:
            (conn, client_addr) = server_socket.accept()
            print("Connect to client:", client_addr)

            thread = Thread(target=handle_connection, args=(conn, client_addr))
            thread.start()
    finally:
        db.close()
        server_socket.close()