import hashlib
import json
import time
from typing import List
from merkle_root import build_merkle_root, sha256d
from block_header import block_header

TX_VSIZE = 250
BLOCK_SIZE_LIMIT = 1_048_576

def generate_tranasctions(count: int) -> List[str]:
    transactions = []
    for i in range(1,count+1):
        transactions.append(hashlib.sha256(str(i).encode()).hexdigest())
    return transactions

def make_coinbase_transaction(height:int) -> str:
    return f"coinbase_height_{height}".encode().hex()

def select_transactions(transactions: List[str],height:int) -> List[str]:
    capacity= BLOCK_SIZE_LIMIT // TX_VSIZE
    coin_base= make_coinbase_transaction(height) 
    return [coin_base] + transactions[:capacity-1]

def target_from_bits(bits: int) -> int:
    exponent = bits >> 24
    coefficient = bits & 0xFFFFFF
    target = coefficient * pow(256, exponent - 3)
    return target

def block_to_dict(height: int, header: bytes, version: int, prev_hash: bytes,
                  merkle_root: bytes, timestamp: int, bits: int, nonce: int,selected_transactions: List[str]) -> dict:
    block_hash_hex = sha256d(header).hex()
    return {
        "height": height,
        "hash": block_hash_hex,
        "header": {
            "version": version,
            "prev_hash": prev_hash.hex(),
            "merkle_root": merkle_root.hex(),
            "timestamp": timestamp,
            "bits": f"{bits:08x}",   # "1e0ffff0"
            "nonce": nonce
        },
        "transactions": selected_transactions
    }




def main():
    transactions = generate_tranasctions(20000)
    height=1
    prev_block_header=None
    bits=0x1e00ffff
    target = target_from_bits(bits)
    blocks = [] 
    start = time.perf_counter()
    while transactions:
        selected_transactions = select_transactions(transactions,height)
        consumed = len(selected_transactions) - 1
        del transactions[:consumed]
        root=build_merkle_root(selected_transactions)
        timestamp=int(time.time())
        prev_header = (b"\x00" * 32) if prev_block_header is None else sha256d(prev_block_header)
        found_header = None
        found_nonce = None
        for nonce in range(0, 2**32):
            header = block_header(1,prev_header,bytes.fromhex(root),timestamp,bits,nonce)
            hash_int=int.from_bytes(sha256d(header),"big")
            if hash_int < target:
                found_header=header
                found_nonce=nonce
                break

        if found_header is None:
            raise RuntimeError("No valid nonce found in 2^32 range")
        
    
        
        print(f"Block {height} found with nonce {found_nonce} and hash {sha256d(found_header).hex()} and transaction count is {len(selected_transactions)}")
        block_obj=block_to_dict(height,found_header,1,prev_header,bytes.fromhex(root),timestamp,bits,found_nonce,selected_transactions)

        blocks.append(block_obj)
        
        height+=1
        prev_block_header=found_header
    end = time.perf_counter()
    duration = end - start
    print(f"Total time taken: {duration:.2f} seconds")
    with open("blockchain.json", "w", encoding="utf-8") as f:
        json.dump(blocks, f, indent=2)    

if __name__ == "__main__":    main()