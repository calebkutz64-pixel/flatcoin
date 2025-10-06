import os
from flatcoin.wallet import Wallet, save_wallet


def open_or_init_wallet() -> Wallet:
    if os.path.isfile("wallet.json"):
        wallet = Wallet.load(open("wallet.json", "r"))
    else:
        wallet = Wallet.empty()
        wallet.generate_keys()
        save_wallet(wallet)
        print("Created new wallet")
        
    return wallet