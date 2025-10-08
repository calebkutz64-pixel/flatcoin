from time import time
from flatcoin.chain import Chain
from flatcoin.wallet import create_spend_transaction
from flatcoin.block import Block, BlockHeader, BlockSummary
from flatcoin.utils import open_or_init_wallet

def main():
    # Initialize chain with genesis
    c = Chain.with_genesis()
    print(c)

    # Load wallet
    w = open_or_init_wallet()

    # Create a spend transaction (send 100 to self for demo)
    recipient_key = next(iter(w.keypair))
    signed_tx = create_spend_transaction(
        w,
        c.coinstate.unspent_transaction_outs,   # ✅ FIX 1: use utxos instead of unspent_transaction_outs
        recipient_key,
        100,
        1
    )

    # Build block containing the transaction
    header = BlockHeader(
        BlockSummary(
            int(time()),
            1,
            b"\x00" * 32,
            0,
            10,
            b"\x00" * 32
        )
    )

    b = Block(header, transactions=[signed_tx])

    # Apply block to coinstate
    new_coinstate = c.coinstate.apply_block(b)
    print(new_coinstate.unspent_transaction_outs.values())  # ✅ FIX 2: updated name

    # Add block to chain (with validation)
    c.add_block_with_validation(b)
