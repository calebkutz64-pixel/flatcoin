from flatcoin.coinstate import CoinState
from flatcoin.reading import computer
import time
from flatcoin.block import Block, BlockHeader, BlockSummary
from flatcoin.transaction import Transaction, Input, Output, OutputReference
from flatcoin.hash import sha256d


just_believe_in_me = (
    b"You buy a piece of paradise\n"
    b"You buy a piece of me\n"
    b"I'll get you everything you wanted\n"
    b"I'll get you everything you need\n"
    b"Don't need to believe in hereafter\n"
    b"Just believe in me"
)


genesis_block_data = computer(
    '00000000000000000000000000000000000000000000000000000000000000000000616c35621abdf928185b74d57985cea7ff2d66ef318c58'
    'ec7ea8dd01ed089028604e7f3101000000000000000000000000000000000000000000000000000000000000000000003aea13176dbcbf6210'
    '55bdb3d6a138be4b73229d8584cb380e1dd1bbe1cedd42820000000000000000000000000000000000000000000000000000000000000000e3'
    '8ee41a6b0f6584fe8b95bd8c8d7b4d6db961fa5c2a6fafe72ea1533dd2838b0100010000000000000000000000000000000000000000000000'
    '000000000000000000000000000100000000ab596f75206275792061207069656365206f662070617261646973650a596f7520627579206120'
    '7069656365206f66206d650a49276c6c2067657420796f752065766572797468696e6720796f752077616e7465640a49276c6c206765742079'
    '6f752065766572797468696e6720796f75206e6565640a446f6e2774206e65656420746f2062656c6965766520696e20686572656166746572'
    '0a4a7573742062656c6965766520696e206d6501000000003b9aca0002aac3faad6ddc26ec4674328741498fe74bdb0d8e49a22473a02370e5'
    '3d69b0079819d5ac3f0cd36f25578eb042ad2a7b59f84a0b5f622e41ac982f478e8cb259'
)


def create_genesis_block(coinbase_value: int, public_key: bytes) -> Block:
    fake_prev_hash = b"\x00" * 32
    coinbase_input = Input(OutputReference(fake_prev_hash, 0xffffffff), b"\x00" * 64)
    coinbase_output = Output(coinbase_value, public_key)
    coinbase_tx = Transaction([coinbase_input], [coinbase_output], None)

    timestamp = int(time.time())
    height = 0
    previous_block_hash = b"\x00" * 32
    nonce = 0
    target = 0xffff

    header_summary = BlockSummary(
        timestamp=timestamp,
        height=height,
        block_hash=b"\x00" * 32,  
        nonce=nonce,
        target=target,
        previous_block_hash=previous_block_hash,
    )

    header = BlockHeader(summary=header_summary)
    genesis_block = Block(header, [coinbase_tx])
    
    block_hash = sha256d(genesis_block.serialize())
    genesis_block.header.summary.block_hash = block_hash
    
    return genesis_block
