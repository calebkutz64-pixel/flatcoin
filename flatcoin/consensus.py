from flatcoin.block import Block, BlockHeader
from flatcoin.params import MAX_BLOCK_SIZE, MAX_FUTURE_BLOCK_TIME
from flatcoin.transaction import Transaction

def validate_coinbase_transaction(transaction: Transaction) -> bool:
    if not len(transaction.inputs) == 1:
        return False

    return True
    
    
def validate_transaction(transaction: Transaction) -> bool:
    if len(transaction.inputs) == 0:
        return False

    if len(transaction.outputs) == 0:
        return False

    if len(transaction.serialize()) > MAX_BLOCK_SIZE:
        return False

    return True

def validate_block_header(block_header: BlockHeader, current_timestamp: int) -> bool:
    if block_header.summary.timestamp > current_timestamp + MAX_FUTURE_BLOCK_TIME:
        return False

    return True
    
def validate_block(block: Block, current_timestamp: int) -> bool:
    valid_header = validate_block_header(block.header, current_timestamp)

    if not valid_header:
        return False
    
    if len(block.transactions) == 0:
        return False

    if len(block.serialize()) > MAX_BLOCK_SIZE:
        return False

    coinbase_transaction = block.transactions[0]
    
    valid_coinbase_transaction = validate_coinbase_transaction(coinbase_transaction)

    if not valid_coinbase_transaction:
        return False

    for transaction in block.transactions[1:]:
        valid_transaction = validate_transaction(transaction)

        if not valid_transaction:
            return False

    return True