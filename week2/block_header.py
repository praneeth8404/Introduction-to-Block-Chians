import struct

def block_header(version: int,prev_hash:str,merkle_root:str,timestamp:int,bits:int,nonce:int):
    if len(prev_hash) != 64 or len(merkle_root) != 64:
        raise ValueError("prev_hash and merkle_root must be 64 hex chars each")
    

    header=struct.pack(">I",version)+bytes.fromhex(prev_hash)+bytes.fromhex(merkle_root)+struct.pack(">III",timestamp,bits,nonce)
    
    if len(header) != 80:
        raise ValueError(f"Invalid header length: {len(header)} (expected 80)")
    return header
    

def main():
    version=1
    prev_hash="0"*64
    merkle_root="0"*64
    timestamp=1
    bits=0x1e0ffff0
    nonce=0
    header=block_header(version,prev_hash,merkle_root,timestamp,bits,nonce)
    print(f"Block header: {header.hex()}")


if __name__ == "__main__":
    main()
