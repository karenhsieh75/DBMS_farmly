from .Role import Role
from action_handler import *

class Consumer(Role):
    def __init__(self, user_id, name, password, phone_number, email, address):

        super().__init__(user_id, name, password, phone_number, email, address)

        self.user_action = {
                                'search for product': get_available_products,
                                'add product to cart': add_to_cart,
                                'view cart': get_cart_contents,
                                'remove some products from cart': remove_from_cart,
                                'purchase product from cart': purchase_products,
                                'view order history': get_consumer_order_history,
                                'rate a farmer': add_consumer_rating,
                                'view past ratings': get_consumer_ratings,
                                'leave system':exit
                           }
        