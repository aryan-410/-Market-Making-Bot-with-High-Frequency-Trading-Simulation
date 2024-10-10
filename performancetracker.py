import matplotlib.pyplot as plt

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