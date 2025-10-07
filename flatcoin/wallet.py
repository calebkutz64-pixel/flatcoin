import os
import json
import ecdsa

from typing import Dict, List, Set, TextIO

from flatcoin.coinstate import CoinState
from flatcoin.reading import computer, human
from flatcoin.transaction import Input, Output, OutputReference, Transaction


class Wallet:
    
    def __init__(self, keypair: Dict[bytes, bytes] | None = None):
        self.keypair = keypair
        self.spent_transaction_outputs: Set[OutputReference] = set()
        
    def generate_keys(self) -> None:
        signing_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        private_key = signing_key.to_string()
        public_key = signing_key.verifying_key.to_string() # type: ignore
        self.keypair = dict()
        self.keypair[public_key] = private_key
        
    def dump(self, f: TextIO) -> None:
        assert self.keypair
        json.dump({
           human(k): human(v) for (k, v) in self.keypair.items()
        }, f, indent=4)
        
    @classmethod
    def empty(cls) -> "Wallet":
        return cls({})
    
    @classmethod
    def load(cls, f: TextIO) -> "Wallet":
        data = json.load(f)
        
        return cls(
            keypair={computer(k): computer(v) for (k, v) in data.items()}
        )
        
    def get_balance(self, coinstate: CoinState) -> int:
        if not self.keypair: 
            return 0
        
        total = 0
        owned_keys = self.keypair.keys()
        
        for out in coinstate.unspent_transaction_outs.values():
            if out.public_key in owned_keys:
                total += out.value
                
        return total
        
        
def save_wallet(wallet: Wallet) -> None:
    with open("wallet.json.new", "w") as f:
        wallet.dump(f)
        
    os.replace("wallet.json.new", "wallet.json")
    
    
def create_spend_transaction(
    wallet: Wallet,
    unspent_transaction_outs: Dict[OutputReference, Output],
    recipient_public_key: bytes,
    amount: int,
    fee: int 
) -> Transaction:
    if not wallet.keypair:
        raise ValueError("Wallet has no keys")
    
    public_key, private_key = next(iter(wallet.keypair.items()))
    signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    
    total = 0
    chosen_unspent_transaction_outs: List[tuple[OutputReference, Output]] = []
    for reference, output in unspent_transaction_outs.items():
        if output.public_key == public_key:
            chosen_unspent_transaction_outs.append((reference, output))
            total += output.value
            if total >= amount + fee:
                break
            
    if total < amount + fee:
        raise ValueError("Insufficient funds") # TODO: create an exception
    
    outputs: List[Output] = [Output(amount, recipient_public_key)]
    change = total - (amount + fee)
    if change > 0:
        outputs.append(Output(change, public_key))
        
    inputs = [Input(reference, signature=None) for (reference, _) in chosen_unspent_transaction_outs]
    
    transaction = Transaction(inputs, outputs, None)
    transaction_hash = transaction.hash()
    for inp in transaction.inputs:
        signature = signing_key.sign_deterministic(transaction_hash)
        inp.signature = signature
        
    transaction.cached_hash = transaction.hash()
    return transaction
    
    
def create_coinbase_transaction(miner_public_key: bytes, reward: int, block_height: int) -> Transaction:
    coinbase_reference = OutputReference(b"\x00" * 32, block_height)
    coinbase_input = Input(output_reference=coinbase_reference, signature=b"\x00" * 64)
    coinbase_output = Output(value=reward, public_key=miner_public_key)
    transaction = Transaction(inputs=[coinbase_input], outputs=[coinbase_output], hash=None)
    transaction.cached_hash = transaction.hash()
    return transaction