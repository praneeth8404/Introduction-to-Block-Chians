import csv
import hashlib
import argparse
from typing import List, Dict

def hash(data: str)-> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def parent_string(parent_hash: str, timestamp:int, nonce:int)-> str:
    return hash(parent_hash+str(timestamp)+str(nonce))

def read_csv(path: str) -> List[Dict]:
    chain = []
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        expected_fields = ["block_height", "parent_hash", "timestamp", "nonce"]
        if reader.fieldnames != expected_fields:
            raise ValueError(f"CSV header must be exactly: {','.join(expected_fields)}")

        for row in reader:
            chain.append({
                "block_height": int(row["block_height"]),
                "parent_hash": row["parent_hash"].strip(),
                "timestamp": int(row["timestamp"]),
                "nonce": int(row["nonce"]),
            })
    return chain


def validate(chain: List[Dict]) -> List[str]:
    errors = []

    if not chain:
        return ["Chain is empty."]

    # Helper to validate 64-char lowercase hex
    def is_hex(s: str) -> bool:
        if len(s) != 64:
            return False
        for ch in s:
            if ch not in "0123456789abcdef":
                return False
        return True
    

    # Check Genesis
    if chain[0]["block_height"] != 0:
       errors.append(f"Genesis block_height must be 0, found {chain[0]['block_height']}.")

    if chain[0]["parent_hash"] != "0" * 64:
       errors.append("Genesis parent_hash must be 64 zeros.")

    if not is_hex(chain[0]["parent_hash"]):
       errors.append("Genesis parent_hash is not a 64-char lowercase hex string.")

    # Per-block checks
    for i in range(len(chain)):
        b = chain[i]

        # parent_hash format check
        if not is_hex(b["parent_hash"]):
           errors.append(f"Block {i}: parent_hash is not 64-char lowercase hex.")

        # block_height sequence check
        if b["block_height"] != i:
           errors.append(
                f"Block at row {i}: block_height must be {i}, found {b['block_height']}."
            )

        # timestamps strictly increasing
        if i > 0:
            prev = chain[i - 1]
            if b["timestamp"] <= prev["timestamp"]:
               errors.append(
                    f"Block {i}: timestamp must be strictly greater than Block {i-1} "
                    f"({b['timestamp']} <= {prev['timestamp']})."
                )

            # hash linkage check
            prev_hash = parent_string(prev["parent_hash"], prev["timestamp"], prev["nonce"])
            if b["parent_hash"] != prev_hash:
               errors.append(
                    f"Block {i}: parent_hash does not match SHA-256(header of Block {i-1})."
                )

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate blockchain.csv with hash + logical checks.")
    parser.add_argument("--file", type=str, default="blockchain.csv", help="Path to blockchain.csv")
    args = parser.parse_args()

    try:
        chain = read_csv(args.file)
        errors = validate(chain)
    except Exception as e:
        print(f"VALIDATION FAILED (exception): {e}")
        return

    if errors:
        print("VALIDATION FAILED")
        for err in errors:
            print(f"- {err}")
    else:
        print("VALIDATION PASSED")
        print(f"Blocks checked: {len(chain)}")


if __name__ == "__main__":
    main()
