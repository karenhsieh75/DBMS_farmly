class Role():
    def __init__(self, user_id, name, password, phone_number, email, address):
        self.user_id = user_id
        self.name = name
        self.password = password
        self.phone_number = phone_number
        self.email = email
        self.address = address
        self.user_action = {}


    def get_username(self):
        return self.name
    
    def get_user_id(self):
        return self.user_id
    
    def get_email(self):
        return self.email
    
    def get_available_action(self):
        return list(self.user_action.keys())
    
    def get_function_name(self, action_str):
        return self.user_action[action_str]
    
    def get_info_msg_no_pwd(self):
        return f'userid: {self.user_id}, username: {self.name}, phone_number: {self.phone_number}, email: {self.email}, role: {type(self).__name__}'
    
    def get_info_msg(self):
        return f'userid: {self.user_id}, username: {self.name}, pwd: {self.password}, phone_number: {self.phone_number}, email: {self.email}, role: {type(self).__name__}'
