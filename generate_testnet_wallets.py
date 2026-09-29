#!/usr/bin/env python3
"""Generate disposable TRON testnet wallets for Nile and Shasta.

The same TRON account/address can be used on both testnets; only the RPC
endpoint changes. Never use the generated private keys for real funds.
"""

from __future__ import annotations

import argparse
import json
import secrets
from pathlib import Path

from tronpy.keys import PrivateKey


NETWORKS = {
    "nile": {
        "name": "TRON Nile Testnet",
        "rpc_url": "https://nile.trongrid.io",
        "faucet_url": "https://nileex.io/join/getJoinPage",
    },
    "shasta": {
        "name": "TRON Shasta Testnet",
        "rpc_url": "https://api.shasta.trongrid.io",
        "faucet_url": "https://www.trongrid.io/shasta",
    },
}


def new_wallet(index: int) -> dict:
    # secrets.token_bytes is backed by the OS CSPRNG. PrivateKey validates the
    # value is in the secp256k1 range before deriving the account addresses.
    private_key = PrivateKey(secrets.token_bytes(32))
    return {
        "id": f"wallet-{index:03d}",
        "private_key": private_key.hex(),
        "address": private_key.public_key.to_base58check_address(),
        "address_hex": private_key.public_key.to_hex_address(),
        "networks": {name: {"name": data["name"], "rpc_url": data["rpc_url"]}
                     for name, data in NETWORKS.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--count", type=int, default=100)
    parser.add_argument("-o", "--output", type=Path, default=Path("testnet-wallets.json"))
    args = parser.parse_args()
    if args.count < 1:
        parser.error("count must be positive")

    document = {
        "format": "tron-testnet-wallets/v1",
        "warning": "TESTNET ONLY. Treat private_key values as secrets even though these accounts are disposable.",
        "networks": NETWORKS,
        "wallets": [new_wallet(i) for i in range(1, args.count + 1)],
    }
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {args.count} wallets in {args.output}")


if __name__ == "__main__":
    main()
