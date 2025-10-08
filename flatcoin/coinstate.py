import immutables

from flatcoin.block import Block
from flatcoin.reading import human
from flatcoin.transaction import Output, OutputReference, Transaction


class CoinState:
    
    def __init__(
        self,
        unspent_transaction_outs: immutables.Map[OutputReference, Output]
    ):
        self.unspent_transaction_outs = unspent_transaction_outs
    
    @classmethod
    def empty(cls) -> "CoinState":
        return cls(unspent_transaction_outs=immutables.Map())
    
    def apply_transaction(self, transaction: Transaction) -> "CoinState":
        with self.unspent_transaction_outs.mutate() as temp:
            
            is_coinbase = (
                len(transaction.inputs) == 1
                and  transaction.inputs[0].output_reference.tx_hash == b"\x00" * 32
            )
            
            if not is_coinbase:
                for inp in transaction.inputs:
                    reference = inp.output_reference
                    if reference not in self.unspent_transaction_outs:
                        raise ValueError(f"Input {human(reference.tx_hash)}:{reference.index} not found or already spent")
                    del temp[reference]
                    
            transaction_hash = transaction.hash()
            for index, output in enumerate(transaction.outputs):
                output_reference = OutputReference(transaction_hash, index)
                temp[output_reference] = output
                
            return CoinState(temp.finish())
        
    def apply_block(self, block: Block) -> "CoinState":
        state = self
        for transaction in block.transactions:
            state = state.apply_transaction(transaction)
        return state