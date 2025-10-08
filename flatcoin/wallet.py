import os
import json
import ecdsa

from typing import Dict, List, Set, TextIO

from flatcoin.coinstate import CoinState
from flatcoin.hash import sha256d
from flatcoin.reading import computer, human
from flatcoin.transaction import Input, Output, OutputReference, Transaction
import ecdsa


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
        
    def __getitem__(self, public_key: bytes) -> bytes:
        return self.keypair[public_key]
    
    def __contains__(self, public_key: bytes) -> bool:
        return public_key in self.keypair
        
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
    
    public_key, _ = next(iter(wallet.keypair.items()))
    
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
    
    signed_transaction = sign_transaction(wallet, unspent_transaction_outs, transaction)
    
    return signed_transaction
    
    
def create_coinbase_transaction(miner_public_key: bytes, reward: int, block_height: int) -> Transaction:
    coinbase_reference = OutputReference(b"\x00" * 32, block_height)
    coinbase_input = Input(output_reference=coinbase_reference, signature=b"\x00" * 64)
    coinbase_output = Output(value=reward, public_key=miner_public_key)
    transaction = Transaction(inputs=[coinbase_input], outputs=[coinbase_output], hash=None)
    transaction.cached_hash = transaction.hash()
    return transaction


def sign_transaction(
    wallet: Wallet,
    unspent_transaction_outs: Dict[OutputReference, Output],
    transaction: Transaction
) -> Transaction:
    message = transaction.serialize()
    
    signed_inputs = []
    for input in transaction.inputs:
        if input.output_reference not in unspent_transaction_outs:
            raise Exception("Attempting to sign invalid transaction")
        
        output = unspent_transaction_outs[input.output_reference]
        
        if output.public_key not in wallet:
            raise Exception("Wallet has no known Private Key")
        
        private_key = wallet[output.public_key]
        
        signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        
        signature = signing_key.sign(message)
        
        signed_inputs.append(Input(
            output_reference=input.output_reference,
            signature=signature.hex()
        ))
        
    signed_tx = Transaction(inputs=signed_inputs, outputs=transaction.outputs, hash=None)
    signed_tx.cached_hash = signed_tx.hash()
    return signed_tx
        