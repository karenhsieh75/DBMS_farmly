from action_handler import *

class Consumer():
    def __init__(self, consumer_id, name, email, phone_number, address, password):

        super().__init__(name, consumer_id, email, phone_number, address, password)

        self.user_action = {
                                'search for product': get_available_products,
                                'add this product to cart': add_to_cart,
                                'view cart': get_cart_contents,
                                'remove some products from cart': remove_from_cart,
                                'purchase product from cart': purchase_products,
                                'view order history': get_consumer_order_history,
                                'rate a farmer': add_consumer_rating,
                                'view past ratings': get_consumer_ratings
                           }
        