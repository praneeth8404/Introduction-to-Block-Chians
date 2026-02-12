import struct

def block_header(version: int,prev_hash:bytes,merkle_root:bytes,timestamp:int,bits:int,nonce:int):
    
    header=struct.pack(">I",version)+prev_hash+merkle_root+struct.pack(">III",timestamp,bits,nonce)
    
    if len(header) != 80:
        raise ValueError(f"Invalid header length: {len(header)} (expected 80)")
    return header
    

def main():
    version=1
    prev_hash=b"\x00" * 32
    merkle_root=b"\x00" * 32
    timestamp=1
    bits=0x1e0ffff0
    nonce=0
    header=block_header(version,prev_hash,merkle_root,timestamp,bits,nonce)
    print(f"Block header: {header.hex()}")


if __name__ == "__main__":
    main()
