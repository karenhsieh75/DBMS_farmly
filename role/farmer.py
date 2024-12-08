from .Role import Role
from action_handler import *

class Farmer(Role):
    def __init__(self, user_id, name, password, phone_number, email, address, farm_address):

        super().__init__(user_id, name, password, phone_number, email, address)

        self.farm_address = farm_address

        self.user_action = {
                                'view upload history': get_farmer_upload_records,
                                'upload amount to an existing product batch': upload_to_existing_products,
                                'create a new product batch and upload products': insert_new_product_and_upload,
                                'search for markets available for registration': get_open_markets,
                                'register for a new market': register_market,
                                'view market stall registration history': get_farmer_market_registrations,
                                'view my rating scores': get_farmer_ratings,
                                'leave system':exit
                           }