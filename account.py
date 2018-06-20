class Account():
    def __init__(self, initialBalance=0.0):
        self.balance = initialBalance

    def withdraw(self, amount):
        self.balance -= amount
        return self.balance

    def deposit(self, amount):
        self.balance += amount
        return self.balance

