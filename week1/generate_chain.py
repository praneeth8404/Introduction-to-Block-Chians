import time
import random
import hashlib
import argparse
import csv

def hash(data: str)-> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def parent_string(parent_hash: str, timestamp:int, nonce:int)-> str:
    return hash(parent_hash+str(timestamp)+str(nonce))

def new_block(block_height:int, parent_hash:str, k:int, prev_ts: int = None)-> dict:
    timestamp = int(time.time())
    # nonce = random.randint(0, 2**32 - 1)
    if prev_ts is not None and timestamp <= prev_ts:
        timestamp = prev_ts + 1

    expected_head="0"*k

    for nonce in range(0, 2**32):
        hs = parent_string(parent_hash, timestamp, nonce)
        if hs.startswith(expected_head):
            hash=hs
            break
         
    return{
        "block_height": block_height,
        "parent_hash": parent_hash,
        "timestamp": timestamp,
        "nonce": nonce,
        "hash": hs,
    }

def generate_chain(n:int, k:int)-> list[dict]:
    if n<10:
        print("Assignment requires at least 10 blocks. Use --n 10 or more.")
        exit(1)
    
    chain = []
    genesis_hash="0"*64
    block0=new_block(0,genesis_hash,k,prev_ts=0)
    chain.append(block0)

    for i in range(1,n):
        prev_hash=chain[i-1]["hash"]
        prev_ts=chain[i-1]["timestamp"]
        block=new_block(i,prev_hash,k,prev_ts)
        chain.append(block)
    
    return chain

def create_csv(chain:list[dict], file:str='blockchain.csv')-> None:
    with open(file,'w',newline='') as l:
        
        writer=csv.writer(l)
        writer.writerow(["block_height","parent_hash","timestamp","nonce"])
        for b in chain:
            writer.writerow([b["block_height"],b["parent_hash"],b["timestamp"],b["nonce"]])



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=10, help="Number of blocks (must be >= 10). Default: 10")
    parser.add_argument("--k", type=int)
    args = parser.parse_args()


    start = time.perf_counter()

    chain = generate_chain(args.n, args.k)
    create_csv(chain)
    end = time.perf_counter()

    duration = end - start

    print(f"Duration (seconds): {duration:.3f}")

if __name__ == "__main__":
    main()