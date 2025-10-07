from flatcoin.block import Block
from flatcoin.chain import Chain


def main():
    c = Chain.without_genesis()
    
    c.scan_for_genesis()
    
    c.add_block_no_validation()