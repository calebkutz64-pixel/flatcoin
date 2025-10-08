import struct
from typing import BinaryIO, Optional, List

from flatcoin.hash import sha256d
from flatcoin.serialization import Serializable, safe_read, stream_deserialize_list, stream_serialize_list


class OutputReference(Serializable):
    
    def __init__(self, tx_hash: bytes, index: int):
        if not len(tx_hash) == 32:
            raise ValueError("OutputReference hash must be 32 bytes")
        
        self.tx_hash = tx_hash
        self.index = index
        
    def stream_serialize(self, f: BinaryIO) -> None:
        f.write(self.tx_hash)
        f.write(struct.pack(b">I", self.index))
        
    @classmethod
    def stream_deserialize(cls, f: BinaryIO) -> "OutputReference":
        hash = safe_read(f, 32)
        (index,) = struct.unpack(b">I", safe_read(f, 4))
        return cls(hash, index)


class Input(Serializable):
    
    def __init__(self, output_reference: OutputReference, signature: Optional[bytes]):
        self.output_reference = output_reference
        self.signature = signature
        
    def stream_serialize(self, f: BinaryIO) -> None:
        self.output_reference.stream_serialize(f)
        # assert self.signature
        #

    @classmethod
    def stream_deserialize(cls, f: BinaryIO) -> "Input":
        output_reference = OutputReference.stream_deserialize(f)
        signature = safe_read(f, 64)
        return cls(output_reference, signature)
    

class Output(Serializable):
    
    def __init__(self, value: int, public_key: bytes):
        self.value = value
        self.public_key = public_key
        
    def stream_serialize(self, f: BinaryIO) -> None:
        f.write(struct.pack(b">Q", self.value))
        f.write(self.public_key)
        
    @classmethod
    def stream_deserialize(cls, f: BinaryIO) -> "Output":
        (value,) = struct.unpack(b">Q", safe_read(f, 8))
        public_key = safe_read(f, 32) 
        return cls(value, public_key)



class Transaction(Serializable):
    
    def __init__(self, inputs: List[Input], outputs: List[Output], hash: Optional[bytes]):
        self.inputs = inputs
        self.outputs = outputs
        self.cached_hash = hash
        
    def stream_serialize(self, f: BinaryIO) -> None:
        stream_serialize_list(f, self.inputs)
        stream_serialize_list(f, self.outputs)
    
    @classmethod
    def stream_deserialize(cls, f: BinaryIO) -> "Transaction":
        start_position = f.tell()
        
        if safe_read(f, 1) != b"\x00":
            raise ValueError("Current version only supports version 0 transactions")
        
        inputs = stream_deserialize_list(f, Input)
        outputs = stream_deserialize_list(f, Output)
        
        end_position = f.tell()
        f.seek(start_position)
        cached_hash = sha256d(f.read(end_position - start_position))
        
        return cls(inputs, outputs, cached_hash)
    
    def hash(self) -> bytes:
        return self.cached_hash or sha256d(self.serialize())