import numpy as np
import heapq
import random
import time
import matplotlib.pyplot as plt
from orderbook import Order

### Market-Maker Bot with Advanced Features ###
class MarketMakerBotAdvanced:
    def __init__(self, spread=0.02, inventory_limit=100, latency=0.1, slippage_factor=0.001):
        self.spread = spread
        self.inventory_limit = inventory_limit
        self.latency = latency
        self.slippage_factor = slippage_factor
        self.inventory = 0
        self.cash = 100000  # Starting with $100k
        self.order_book = None
        self.order_id = 0

    def set_order_book(self, order_book):
        """Sets the order book for the market-making bot."""
        self.order_book = order_book

    def quote(self):
        """Generate dynamic bid and ask quotes based on market conditions."""
        best_bid, best_ask = self.order_book.get_top_of_book()
        if best_bid and best_ask:
            bid = best_bid * (1 - self.spread / 2)
            ask = best_ask * (1 + self.spread / 2)
        else:
            bid, ask = 100 * (1 - self.spread / 2), 100 * (1 + self.spread / 2)
        return bid, ask

    def apply_slippage(self, price, quantity):
        """Apply slippage based on order size."""
        slippage = 1 + self.slippage_factor * (quantity / self.inventory_limit)
        return price * slippage

    def handle_order(self, side, price, quantity):
        """Handles orders with latency, slippage, and market impact."""
        time.sleep(self.latency)  # Simulate latency

        if side == 'buy':
            trades = self.order_book.match_sell_order(Order(self.order_id, side, price, quantity, 'market'))
            for trade_price, trade_qty in trades:
                executed_price = self.apply_slippage(trade_price, trade_qty)
                self.inventory += trade_qty
                self.cash -= executed_price * trade_qty
                print(f"Executed BUY for {trade_qty} @ {executed_price:.2f}")
        elif side == 'sell':
            trades = self.order_book.match_buy_order(Order(self.order_id, side, price, quantity, 'market'))
            for trade_price, trade_qty in trades:
                executed_price = self.apply_slippage(trade_price, trade_qty)
                self.inventory -= trade_qty
                self.cash += executed_price * trade_qty
                print(f"Executed SELL for {trade_qty} @ {executed_price:.2f}")
        
        self.order_id += 1  # Increment order ID for the next order

    def market_make(self, duration=60, interval=0.1, performance_tracker=None):
        """Main market-making loop with advanced features."""
        for _ in range(int(duration / interval)):
            self.order_book.update_order_book()
            bid, ask = self.quote()
            print(f"Bot Quoting: Bid {bid:.2f}, Ask {ask:.2f}")

            # Simulate random market orders
            if random.random() < 0.5:
                self.handle_order('buy', ask, random.randint(5, 20))
            if random.random() < 0.5:
                self.handle_order('sell', bid, random.randint(5, 20))

            # Track performance after each interval
            if performance_tracker:
                performance_tracker.track(self)

            time.sleep(interval)