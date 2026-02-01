import json


class AlphaTracker:
    def __init__(self, initial_balance=10000.0):
        self.balance = initial_balance
        self.position = 0.0  # Amount of BTC held
        self.entry_price = 0.0
        self.total_fees = 0.0
        self.trade_count = 0
        self.fee_rate = 0.0001  # 0.01% Binance-level fee

    def update(self, signal, current_price):
        """
        Lethal Logic: Simulated Execution
        signal > 0.3: BUY
        signal < -0.3: SELL
        """
        # BUY LOGIC
        if signal > 0.3 and self.position == 0:
            slippage = current_price * 0.00005  # 0.005% slippage
            exec_price = current_price + slippage
            self.position = self.balance / exec_price
            self.entry_price = exec_price
            fee = self.balance * self.fee_rate
            self.balance -= fee
            self.total_fees += fee
            self.trade_count += 1
            return f"BUY @ {exec_price:.2f}"

        # SELL LOGIC
        elif signal < -0.3 and self.position > 0:
            slippage = current_price * 0.00005
            exec_price = current_price - slippage
            self.balance = self.position * exec_price
            fee = self.balance * self.fee_rate
            self.balance -= fee
            self.total_fees += fee
            self.position = 0
            self.trade_count += 1
            return f"SELL @ {exec_price:.2f}"

        return "HOLD"

    def get_equity(self, current_price):
        if self.position > 0:
            return self.position * current_price
        return self.balance
