import random
import numpy as np
from marketmakerbotwithlatency import MarketMakerBotWithLatency
import time

class MarketMakerWithQLearning(MarketMakerBotWithLatency):
    def __init__(self, spread=0.02, inventory_limit=100, latency=0.1, slippage_factor=0.001):
        super().__init__(spread, inventory_limit, latency, slippage_factor)
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.exploration_rate = 1.0  # Initial exploration rate
        self.exploration_decay = 0.995
        self.min_exploration_rate = 0.01

    def get_state(self, price, volatility):
        """Returns a simplified state based on price and volatility."""
        return (round(price, 2), round(volatility, 2))

    def choose_action(self, state):
        """Choose an action (spread adjustment) based on the Q-table."""
        if random.random() < self.exploration_rate:
            return random.choice([-0.001, 0.001])  # Random spread adjustment
        if state not in self.q_table:
            self.q_table[state] = [0, 0]  # Initialize state in Q-table
        return np.argmax(self.q_table[state]) - 0.001  # Choose best action

    def update_q_table(self, state, action, reward, next_state):
        """Updates Q-table based on the action taken and the reward received."""
        if state not in self.q_table:
            self.q_table[state] = [0, 0]
        if next_state not in self.q_table:
            self.q_table[next_state] = [0, 0]
        action_idx = 0 if action == -0.001 else 1
        q_value = self.q_table[state][action_idx]
        next_max_q_value = max(self.q_table[next_state])
        new_q_value = q_value + self.learning_rate * (reward + self.discount_factor * next_max_q_value - q_value)
        self.q_table[state][action_idx] = new_q_value

    def market_make(self, duration=60, interval=0.1):
        """Main loop for market-making with Q-learning-based spread adjustments."""
        for _ in range(int(duration / interval)):
            self.order_book.update_order_book()
            price = self.order_book.price
            volatility = np.std([bid[0] for bid in self.order_book.bids])
            state = self.get_state(price, volatility)
            action = self.choose_action(state)

            # Adjust spread based on action
            self.spread += action
            self.spread = max(0.001, self.spread)  # Ensure spread doesn't go negative
            bid, ask = self.quote(price)
            print(f"Bid: {bid:.2f}, Ask: {ask:.2f}")

            # Simulate buy/sell orders and match them
            self.handle_order('sell', ask, random.randint(5, 20))
            self.handle_order('buy', bid, random.randint(5, 20))

            # Reward: profit from market-making
            reward = (self.cash + self.inventory * price) - 100000
            next_state = self.get_state(price, volatility)
            self.update_q_table(state, action, reward, next_state)

            # Decay exploration rate
            self.exploration_rate = max(self.min_exploration_rate, self.exploration_rate * self.exploration_decay)

            time.sleep(interval)
