import numpy as np
import heapq
import random
import time
import matplotlib.pyplot as plt

### Order Class ###
class Order:
    def __init__(self, order_id, side, price, quantity, order_type='limit'):
        self.order_id = order_id
        self.side = side  # 'buy' or 'sell'
        self.price = price
        self.quantity = quantity
        self.order_type = order_type  # 'market', 'limit', 'stop'
        self.timestamp = time.time()  # To simulate price-time priority
    
    def __lt__(self, other):
        # For price-time priority in the heap (buy orders: max-heap, sell orders: min-heap)
        if self.side == 'buy':
            return self.price > other.price if self.price != other.price else self.timestamp < other.timestamp
        else:
            return self.price < other.price if self.price != other.price else self.timestamp < other.timestamp
