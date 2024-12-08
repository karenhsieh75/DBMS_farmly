
from action_handler import *

class Farmer():
    def __init__(self, farmer_id, name, password, phone_number, email, address, farm_address):

        super().__init__(self, farmer_id, name, password, phone_number, email, address)

        self.user_action = {
                                'view upload history': get_farmer_upload_records,
                                'upload amount to an existing product batch': upload_to_existing_products,
                                'create a new product batch and upload products': insert_new_product_and_upload,
                                'search for markets available for registration': get_open_markets,
                                'register for a new market': get_farmer_market_registrations,
                                'view market stall registration history': register_market,
                                'view my rating scores': get_farmer_ratings
                           }