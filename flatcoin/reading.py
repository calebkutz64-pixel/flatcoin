from binascii import hexlify, unhexlify


def human(b: bytes) -> str:
    return hexlify(b).decode("utf-8")


def computer(s: str) -> bytes:
    return unhexlify(s.encode("utf-8"))