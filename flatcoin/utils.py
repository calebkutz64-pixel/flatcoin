import os
from flatcoin.block import Block
from flatcoin.reading import human
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


def create_chain_directory() -> None:
    if not os.path.isdir("chain-state"):
        os.mkdir("chain-state")
        os.mkdir("chain-state/blocks")


def block_filename(block: Block) -> str:
    return "%08d-%s" % (block.header.summary.height, human(block.hash()))


def save_block_to_file(chain_directory: str, block: Block) -> None:
    with open(chain_directory+f"/{block_filename(block)}", "wb") as f:
        f.write(block.serialize())
        
        
def block_file_count(chain_directory: str) -> int:
    file_count = 0
    for entry in os.scandir(chain_directory+"/blocks"):
        if entry.is_file():
            file_count += 1
    return file_count