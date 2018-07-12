from blockchain import recordBlockchainTransaction

class Account():

    def __init__(self, name, initialBalance=0.0):
        """Create account with the given name and starting balance
        """
        self.name = name
        self.balance = initialBalance

    def withdraw(self, amount):
        """Reduce balance for this account by given amount
           Notify the blockchain object as we do this
        """   
        self.balance -= amount
        recordBlockchainTransaction(self.name,"debit",amount)
        return self.balance

    def deposit(self, amount):
        self.balance += amount
        recordBlockchainTransaction(self.name,"credit",amount)
        return self.balance

