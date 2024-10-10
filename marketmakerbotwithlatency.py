import time
import random

class MarketMakerBotWithLatency:
    def __init__(self, spread=0.02, inventory_limit=100, latency=0.1, slippage_factor=0.001):
        self.spread = spread
        self.inventory_limit = inventory_limit
        self.latency = latency
        self.slippage_factor = slippage_factor
        self.inventory = 0
        self.cash = 100000
        self.order_book = None

    def set_order_book(self, order_book):
        """Sets the order book for the market-making bot."""
        self.order_book = order_book

    def quote(self, price):
        """Generate dynamic bid and ask quotes, adjusted for market volatility."""
        bid = price * (1 - self.spread / 2)
        ask = price * (1 + self.spread / 2)
        return bid, ask

    def apply_slippage(self, price, quantity):
        """Apply slippage to larger orders."""
        slippage = 1 + self.slippage_factor * (quantity / self.inventory_limit)
        return price * slippage

    def handle_order(self, side, price, quantity):
        """Simulate handling an order with latency and slippage."""
        time.sleep(self.latency)  # Simulate network latency
        if side == 'buy':
            executed_quantity, executed_price = self.order_book.match_order('sell', price, quantity)
            if executed_price:
                adjusted_price = self.apply_slippage(executed_price, executed_quantity)
                self.inventory += executed_quantity
                self.cash -= adjusted_price * executed_quantity
                print(f"Executed BUY order for {executed_quantity} @ {adjusted_price:.2f}")
        elif side == 'sell':
            executed_quantity, executed_price = self.order_book.match_order('buy', price, quantity)
            if executed_price:
                adjusted_price = self.apply_slippage(executed_price, executed_quantity)
                self.inventory -= executed_quantity
                self.cash += adjusted_price * executed_quantity
                print(f"Executed SELL order for {executed_quantity} @ {adjusted_price:.2f}")

    def market_make(self, duration=60, interval=0.1):
        """Main loop for market-making, dynamically adjusts spread based on market volatility."""
        for _ in range(int(duration / interval)):
            self.order_book.update_order_book()
            price = self.order_book.price
            bid, ask = self.quote(price)
            print(f"Bid: {bid:.2f}, Ask: {ask:.2f}")

            # Simulate buy/sell orders and match them
            self.handle_order('sell', ask, random.randint(5, 20))  # Random sell at ask
            self.handle_order('buy', bid, random.randint(5, 20))  # Random buy at bid

            time.sleep(interval)
