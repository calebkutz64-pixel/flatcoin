from flatcoin.block import Block, BlockHeader
from flatcoin.params import MAX_BLOCK_SIZE, MAX_FUTURE_BLOCK_TIME
from flatcoin.transaction import Transaction



class ProofOfWorkValidationError(Exception):
    pass



class BlockHeaderValidationError(Exception):
    pass



class BlockValidationError(Exception):
    pass


class TransactionValidationError(Exception):
    pass


def validate_coinbase_transaction(transaction: Transaction) -> None:
    if not len(transaction.inputs) == 1:
        raise TransactionValidationError("Coinbase transaction should have 1 input")
    
    
def validate_transaction(transaction: Transaction) -> None:
    if len(transaction.inputs) == 0:
        raise TransactionValidationError("No inputs")

    if len(transaction.outputs) == 0:
        raise TransactionValidationError("No outputs")
    
    if len(transaction.serialize()) > MAX_BLOCK_SIZE:
        raise TransactionValidationError("transaction > MAX_BLOCK_SIZE")


def validate_proof_of_work(hash: bytes, target: bytes) -> None:
    if hash >= target:
        raise ProofOfWorkValidationError("hash >= target")
    

def validate_block_header(block_header: BlockHeader, current_timestamp: int) -> None:
    validate_proof_of_work(block_header.hash(), block_header.summary.target)
    
    if block_header.summary.timestamp > current_timestamp + MAX_FUTURE_BLOCK_TIME:
        raise BlockHeaderValidationError("Block timestamp in the future")
    
    
def validate_block(block: Block, current_timestamp: int) -> None:
    validate_block_header(block.header, current_timestamp)
    
    if len(block.transactions) == 0:
        raise BlockValidationError("No transactions in block")
    
    if len(block.serialize()) > MAX_BLOCK_SIZE:
        raise BlockValidationError("block > MAX_BLOCK_SIZE")
    
    coinbase_transaction = block.transactions[0]
    
    validate_coinbase_transaction(coinbase_transaction)
    
    for transaction in block.transactions[1:]:
        validate_transaction(transaction)