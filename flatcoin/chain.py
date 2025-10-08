from time import time
from typing import Optional
from flatcoin.block import Block
from flatcoin.coinstate import CoinState
from flatcoin.consensus import validate_block
from flatcoin.database import BlockStore, DefaultBlockStore
from flatcoin.genesis import create_genesis_block
from flatcoin.utils import open_or_init_wallet, save_block_to_file
from flatcoin.wallet import create_coinbase_transaction


CHAIN_CACHE_DIRECTORY = "chain-state"
CHAIN_BLOCKS_DIRECTORY = f"{CHAIN_CACHE_DIRECTORY}/blocks"


class Chain:
    
    def __init__(
        self,
        disk: BlockStore,
        coinstate: CoinState,
        genesis: Optional[Block],
        height: int,
    ):
        self.disk = disk
        self.coinstate = coinstate
        self.genesis = genesis
        self.height = height
        
    @classmethod
    def with_genesis(cls) -> "Chain":
        disk = DefaultBlockStore.instance
        coinstate = CoinState.empty()
        
        wallet = open_or_init_wallet()
        public_key = next(iter(wallet.keypair))
        
        coinbase_transaction = create_coinbase_transaction(
            miner_public_key=public_key,
            reward=50_000_000,
            block_height=0,
        )
        
        genesis = create_genesis_block(coinbase_transaction.outputs[0].value, public_key)
        coinstate = coinstate.apply_block(genesis)
        
        disk.insert(genesis.hash(), genesis.serialize())
        save_block_to_file(CHAIN_BLOCKS_DIRECTORY, genesis)
        
        return cls(
            disk=disk,
            coinstate=coinstate,
            genesis=genesis,
            height=1
        )
        
    def add_block_with_validation(self, block: Block) -> None:
        validate_block(block, int(time()))
        
        if block.transactions:
            self.coinstate = self.coinstate.apply_block(block)
        
        self.disk.insert(block.hash(), block.serialize())
        save_block_to_file(CHAIN_BLOCKS_DIRECTORY, block)
        
        self.height += 1
        
    def __repr__(self) -> str:
        return "Chain w/ %s blocks" % self.height