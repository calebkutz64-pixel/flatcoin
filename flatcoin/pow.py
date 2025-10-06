from tarfile import data_filter
import time
from typing import Optional

from flatcoin.hash import sha256d


class ProofOfWork:
    
    def __init__(
        self,
        data: bytes,
        difficulty_hex_zeros: Optional[int] = None,
        difficulty_bits: Optional[int] = None,
        start_nonce: int = 0,
        max_nonce: Optional[int] = None,
        verbose: bool = False
    ):
        self.data = data
        self.difficulty_hex_zeros = difficulty_hex_zeros
        self.difficulty_bits = difficulty_bits
        self.start_nonce = start_nonce
        self.max_nonce = max_nonce
        self.verbose = verbose
        
    def start(self) -> bytes:
        assert (self.difficulty_hex_zeros is not None) ^ (self.difficulty_bits is not None)
        
        t0 = time.time()
        nonce = self.start_nonce
        checks = 0
        
        prefix = (b"\x00" * self.difficulty_hex_zeros) if self.difficulty_hex_zeros is not None else None
        
        if self.difficulty_hex_zeros is not None:
            target = (1 << 256) - 1
            target >>= self.difficulty_bits
            
        running = True
        while running:
            nonce_bytes = nonce.to_bytes(8, byteorder="big", signed=False)
            h = sha256d(self.data + nonce_bytes)
            
        valid = False
        if prefix is not None:
            if h.startswith(prefix):
                valid = True
        else:
            h_int = int.from_bytes(h, byteorder="big")
            if h_int <= target:
                valid = True
                
        if valid:
            seconds = time.time() - t0
            return h
        
        nonce += 1
        checks += 1
        
        if self.max_nonce is not None and nonce > self.max_nonce:
            seconds = time.time() - t0
            raise RuntimeError(f"Failed to find a valid nonce up to max_nonce={self.max_nonce} "
                               f"(checked {checks} nonces in {seconds:.3f}s)")
            
        if self.verbose and checks % 1_000_000 == 0:
            elapsed = time.time() - t0
            print(f"tried {checks} nonces -- current nonce {nonce} -- elapsed {elapsed:.2f}s")
            
    def validate(self) -> bool:
        assert (self.difficulty_hex_zeros is not None) ^ (difficulty_bits is not None), \
            "Provide exactly one of difficulty_hex_zeros or difficulty_bits"

        nonce_bytes = self.nonce.to_bytes(8, byteorder="big", signed=False)
        h = sha256d(self.data + nonce_bytes)
        hex_h = h.hex()

        if self.difficulty_hex_zeros is not None:
            return hex_h.startswith("0" * self.difficulty_hex_zeros)
        else:
            target = (1 << 256) - 1
            target >>= self.difficulty_bits
            return int.from_bytes(h, byteorder="big") <= target