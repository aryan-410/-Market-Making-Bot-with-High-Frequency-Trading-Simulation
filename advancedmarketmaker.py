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


### Advanced Order Book ###
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


### Performance Tracker ###
class PerformanceTracker:
    def __init__(self):
        self.profits = []
        self.inventory = []
        self.cash = []

    def track(self, bot):
        """Tracks the total profit, cash, and inventory over time."""
        best_bid = bot.order_book.get_top_of_book()[0]  # Get the best bid
        inventory_value = best_bid * bot.inventory if best_bid is not None else 0  # If best bid is None, inventory value is 0
        total_assets = bot.cash + inventory_value  # Cash + inventory value
        self.profits.append(total_assets)
        self.inventory.append(bot.inventory)
        self.cash.append(bot.cash)
        
    def plot(self):
        """Plots the performance metrics over time."""
        plt.figure(figsize=(12, 8))

        plt.subplot(3, 1, 1)
        plt.plot(self.profits, label='Total Profit')
        plt.title('Total Profit Over Time')
        plt.xlabel('Time')
        plt.ylabel('Profit')
        plt.grid(True)

        plt.subplot(3, 1, 2)
        plt.plot(self.inventory, label='Inventory Level')
        plt.title('Inventory Over Time')
        plt.xlabel('Time')
        plt.ylabel('Inventory')
        plt.grid(True)

        plt.subplot(3, 1, 3)
        plt.plot(self.cash, label='Cash Balance')
        plt.title('Cash Balance Over Time')
        plt.xlabel('Time')
        plt.ylabel('Cash')
        plt.grid(True)

        plt.tight_layout()
        plt.show()


### Running the Market Maker with Performance Tracking ###
# Create an advanced order book with multiple price levels
order_book = AdvancedOrderBook(levels=5)

# Create the advanced market maker bot
market_maker = MarketMakerBotAdvanced()

# Set the order book for the market-making bot
market_maker.set_order_book(order_book)

# Instantiate the performance tracker
performance_tracker = PerformanceTracker()

# Run the market maker for 60 seconds with performance tracking
market_maker.market_make(duration=60, performance_tracker=performance_tracker)

# Plot the performance of the bot over time
performance_tracker.plot()
