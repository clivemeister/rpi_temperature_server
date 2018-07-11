""" Simple module that stores a flag when a bitcoin transfer has recently been
    performed and returns a flag if that is the case, so we can mark up the 
    display of transaction hashes in blockchain.html
"""

newBlockchainTransaction = False;

def isRecentBlockchainTransaction():
    global newBlockchainTransaction
    if (newBlockchainTransaction):
        print("newBlockchainTransaction is true")
        answer = True
        newBlockchainTransaction = False
    else:
        answer = False
    return answer

def recordBlockchainTransaction(accountName, type, amount):
    global newBlockchainTransaction
    newBlockchainTransaction = True
    return
