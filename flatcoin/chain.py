from typing import List, Optional
from flatcoin.block import Block
from flatcoin.coinstate import CoinState
from flatcoin.consensus import validate_block
from flatcoin.database import BlockStore, DefaultBlockStore
from flatcoin.genesis import create_genesis_block, genesis_block_data

from time import time

from flatcoin.utils import save_block_to_file
from flatcoin.wallet import Wallet, create_coinbase_transaction


CHAIN_CACHE_DIRECTORY = "chain-state"
CHAIN_BLOCKS_DIRECTORY = f"{CHAIN_CACHE_DIRECTORY}/blocks"


class Chain:
    
    def __init__(
        self,
        disk: BlockStore,
        coinstate: CoinState,
        genesis: Optional[Block]
    ):
        self.disk = disk
        self.coinstate = coinstate
        self.genesis = genesis
        
    @classmethod 
    def without_genesis(cls) -> "Chain":
        disk = DefaultBlockStore.instance
        coinstate = CoinState.empty()
        
        chain = cls(
            disk=disk,
            coinstate=coinstate,
            genesis=None
        )
        
        # TODO do this through the Miner class
        w = Wallet.empty()
        w.generate_keys()
        
        create_genesis_block(create_coinbase_transaction(w.keypair.keys(), ))
        
    def add_block_with_validation(self, block: Block) -> None:
        validate_block(block, int(time())) 
        
        if not len(block.transactions) == 0:
            self.coinstate.apply_block(block)
        
        self.disk.insert(block.hash(), block.serialize())
        save_block_to_file(CHAIN_BLOCKS_DIRECTORY, block)
        