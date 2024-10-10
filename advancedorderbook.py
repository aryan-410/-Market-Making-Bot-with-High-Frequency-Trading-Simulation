import numpy as np
import heapq
import random
import time
import matplotlib.pyplot as plt
from orderbook import Order

class AdvancedOrderBook:
    def __init__(self, levels=5):
        self.levels = levels
        self.buy_orders = []  # Max-heap for buy orders
        self.sell_orders = []  # Min-heap for sell orders
        self.order_id = 0  # Unique ID for orders
        self.order_map = {}  # Order ID to order mapping for easy removal

    def add_order(self, side, price, quantity, order_type='limit'):
        """Adds a new order to the order book."""
        order = Order(self.order_id, side, price, quantity, order_type)
        if side == 'buy':
            heapq.heappush(self.buy_orders, order)
        else:
            heapq.heappush(self.sell_orders, order)
        self.order_map[self.order_id] = order
        self.order_id += 1
        return order.order_id

    def cancel_order(self, order_id):
        """Cancels an order by removing it from the heap and the order map."""
        if order_id in self.order_map:
            order = self.order_map[order_id]
            if order.side == 'buy':
                self.buy_orders = [o for o in self.buy_orders if o.order_id != order_id]
                heapq.heapify(self.buy_orders)  # Rebuild the heap after removal
            else:
                self.sell_orders = [o for o in self.sell_orders if o.order_id != order_id]
                heapq.heapify(self.sell_orders)
            del self.order_map[order_id]

    def match_order(self, incoming_order):
        """Matches an incoming order against the order book."""
        if incoming_order.side == 'buy':
            return self.match_buy_order(incoming_order)
        else:
            return self.match_sell_order(incoming_order)

    def match_buy_order(self, buy_order):
        """Matches a buy order against the sell side of the book."""
        trades = []
        while buy_order.quantity > 0 and len(self.sell_orders) > 0 and buy_order.price >= self.sell_orders[0].price:
            best_sell_order = heapq.heappop(self.sell_orders)
            trade_quantity = min(buy_order.quantity, best_sell_order.quantity)
            trades.append((best_sell_order.price, trade_quantity))
            buy_order.quantity -= trade_quantity
            best_sell_order.quantity -= trade_quantity
            if best_sell_order.quantity > 0:
                heapq.heappush(self.sell_orders, best_sell_order)
        return trades

    def match_sell_order(self, sell_order):
        """Matches a sell order against the buy side of the book."""
        trades = []
        while sell_order.quantity > 0 and len(self.buy_orders) > 0 and sell_order.price <= self.buy_orders[0].price:
            best_buy_order = heapq.heappop(self.buy_orders)
            trade_quantity = min(sell_order.quantity, best_buy_order.quantity)
            trades.append((best_buy_order.price, trade_quantity))
            sell_order.quantity -= trade_quantity
            best_buy_order.quantity -= trade_quantity
            if best_buy_order.quantity > 0:
                heapq.heappush(self.buy_orders, best_buy_order)
        return trades

    def get_top_of_book(self):
        """Returns the top of the order book (best bid and ask)."""
        best_bid = self.buy_orders[0].price if len(self.buy_orders) > 0 else None
        best_ask = self.sell_orders[0].price if len(self.sell_orders) > 0 else None
        return best_bid, best_ask

    def update_order_book(self):
        """Simulate random new orders and cancellations over time."""
        # Randomly add new orders to the book
        if random.random() < 0.5:
            side = 'buy' if random.random() < 0.5 else 'sell'
            price = random.uniform(90, 110)
            quantity = random.randint(1, 100)
            self.add_order(side, price, quantity)
        # Randomly cancel orders from the book
        if random.random() < 0.2:
            if random.random() < 0.5 and len(self.buy_orders) > 0:
                self.cancel_order(self.buy_orders[0].order_id)
            elif len(self.sell_orders) > 0:
                self.cancel_order(self.sell_orders[0].order_id)

    def print_order_book(self):
        """Prints the current state of the order book."""
        print("Buy Orders:")
        for order in self.buy_orders:
            print(f"Price: {order.price}, Quantity: {order.quantity}")
        print("Sell Orders:")
        for order in self.sell_orders:
            print(f"Price: {order.price}, Quantity: {order.quantity}")