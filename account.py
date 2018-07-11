from blockchain import recordBlockchainTransaction

class Account():

    def __init__(self, name, initialBalance=0.0):
        self.name = name
        self.balance = initialBalance

    def withdraw(self, amount):
        self.balance -= amount
        recordBlockchainTransaction(self.name,"debit",amount)
        return self.balance

    def deposit(self, amount):
        self.balance += amount
        recordBlockchainTransaction(self.name,"credit",amount)
        return self.balance

