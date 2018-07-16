from blockchain import isRecentBlockchainTransaction, recordBlockchainTransaction

def test_the_basics():
    assert isRecentBlockchainTransaction()==False
    recordBlockchainTransaction("fridge","debit",0.50)
    assert isRecentBlockchainTransaction()==True
    assert isRecentBlockchainTransaction()==False
