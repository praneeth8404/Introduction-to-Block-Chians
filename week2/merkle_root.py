import hashlib


def sha256d(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def bytelist(hexlist: list[str]) -> list[bytes]:
    bytelist = []
    for h in hexlist:
        bytelist.append(bytes.fromhex(h))
    return bytelist

def build_merkle_root(txlist :list[str]) -> str:

    if not txlist:
        return "0" * 64

    tx_bytes = bytelist(txlist)

    for i in range(len(tx_bytes)):
        tx_bytes[i] = sha256d(tx_bytes[i])

    current_level = tx_bytes[:]
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            if i + 1 < len(current_level):
                right = current_level[i + 1]
            else:
                right = left

            next_level.append(sha256d(left + right))
        current_level = next_level

    return current_level[0].hex()


def main():
    txlist=["11", "22", "33", "44", "55"]
    root=build_merkle_root(txlist)
    print(f"Merkle root: {root}")

if __name__ == "__main__":    main()