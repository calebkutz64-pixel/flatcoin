import os
import sqlite3

from flatcoin.block import Block


class BlockStore:
    
    def __init__(self, path: str):
        
        self.is_memory: bool = path == ":memory:"
        self.is_new: bool = self.is_memory or not os.path.isfile(path)
        
        if self.is_new and not self.is_memory:
            print(f"Creating blockstore at {path}")
        elif not self.is_memory:
            print(f"Loading blockstore from {path}")
        
        self.connection: sqlite3.Connection = sqlite3.connect(path)
        
        if self.is_new:
            self._ensure_schema()
        
    def _ensure_schema(self) -> None:
        self.connection.execute("""

            CREATE TABLE IF NOT EXISTS chain (
                hash BLOB,
                block_bytes BLOB
            )
            
        """)
        
    def insert(self, hash: bytes, block_bytes: bytes) -> None:
        self.connection.execute("""
            
            INSERT INTO chain (hash, block_bytes) VALUES (?, ?)
                                    
        """, (hash, block_bytes))
        self.connection.commit()
        
    # TODO: make sure to check if the block bytes equals b"\x00"
    # if so, this means it could not find the block with the given hash
    def get(self, hash: bytes) -> Block:
        cursor = self.connection.execute(
            "SELECT block_bytes FROM chain WHERE hash = ?", 
            (hash,)
        )
        row = cursor.fetchone()
        return Block.deserialize(row[0] if row is not None else b"\x00")
    
    def remove(self, hash: bytes) -> None:
        self.connection.execute("""

            DELETE FROM chain WHERE hash = ?
            
        """, (hash,))
        self.connection.commit()