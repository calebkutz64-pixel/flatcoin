import struct
from typing import BinaryIO, List, Optional

from flatcoin.hash import sha256d
from flatcoin.serialization import Serializable, safe_read, stream_deserialize_list, stream_deserialize_vlq, stream_serialize_list, stream_serialize_vlq
from flatcoin.transaction import Transaction


class BlockSummary(Serializable):
    
    # TODO: add target and merkle_root_hash
    
    def __init__(
        self,
        timestamp: int,
        height: int,
        block_hash: bytes,
        nonce: int,
        target: int,
        previous_block_hash: bytes,
    ):
        self.timestamp = timestamp
        self.height = height
        self.block_hash = block_hash
        self.nonce = nonce
        self.target = target
        self.previous_block_hash = previous_block_hash
        
    def hash(self) -> bytes:
        return sha256d(self.serialize())
        
    def stream_serialize(self, f: BinaryIO) -> None:
        f.write(struct.pack(b">I", self.timestamp))
        stream_serialize_vlq(f, self.height)
        f.write(self.block_hash)
        f.write(struct.pack(b">I", self.nonce))
        f.write(struct.pack(b">I", self.target))
        f.write(self.previous_block_hash)
        
    @classmethod
    def stream_deserialize(cls, f: BinaryIO) -> "BlockSummary":
        (timestamp,) = struct.unpack(b">I", safe_read(f, 4))
        height = stream_deserialize_vlq(f)
        block_hash = safe_read(f, 32)
        (nonce,) = struct.unpack(b">I", safe_read(f, 4))
        (target,) = struct.unpack(b">I", safe_read(f, 4))
        previous_block_hash = safe_read(f, 32)
        return cls(timestamp, height, block_hash, nonce, target, previous_block_hash) 
    
    
class BlockHeader(Serializable):
    
    # TODO: implement & add ProofOfWorkEvidence
    
    def __init__(self, summary: BlockSummary):
        self.summary = summary
        self.version = 0
    
    def hash(self) -> bytes:
        return sha256d(self.serialize())
    
    def stream_serialize(self, f: BinaryIO) -> None:
        self.summary.stream_serialize(f)
        f.write(struct.pack(b"B", self.version))
        
    @classmethod
    def stream_deserialize(cls, f: BinaryIO) -> "BlockHeader":
        summary = BlockSummary.stream_deserialize(f)
        
        return cls(summary)
        
        
class Block(Serializable):
    
    def __init__(self, header: BlockHeader, transactions: List[Transaction], hash: Optional[bytes] = None):
        self.header = header
        self.transactions = transactions
        self.cached_hash = hash
        
    def hash(self) -> bytes:
        return self.cached_hash or self.header.hash()
    
    def stream_serialize(self, f: BinaryIO) -> None:
        self.header.stream_serialize(f)
        stream_serialize_list(f, self.transactions)
        
    @classmethod 
    def stream_deserialize(cls, f: BinaryIO) -> "Block":
        start_position = f.tell()
        header = BlockHeader.stream_deserialize(f)
        end_position = f.tell()
        f.seek(start_position)
        hash = sha256d(f.read(end_position - start_position))
        transactions = stream_deserialize_list(f, Transaction)
        return cls(header, transactions, hash)