#!/usr/bin/env python3
"""为 testnet-wallets.json 中的钱包准备 TRON 测试币领取清单。

Nile 和 Shasta 当前使用网页水龙头。本脚本会校验钱包、通过公开 RPC
查询余额，并生成领取清单；不会发送私钥。
"""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from tronpy.keys import PrivateKey


FAUCETS = {
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


def get_balance(address: str, rpc_url: str) -> int | None:
    body = json.dumps({"value": address}).encode()
    request = Request(
        f"{rpc_url}/wallet/getaccount",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            return int(json.load(response).get("balance", 0))
    except Exception as exc:  # RPC 暂时不可用时不阻止继续准备领取清单。
        print(f"warning: balance lookup failed for {address}: {exc}", file=sys.stderr)
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", choices=FAUCETS, action="append", default=None,
                        help="要准备的网络，默认同时处理两个网络")
    parser.add_argument("--wallet-file", type=Path, default=Path("testnet-wallets.json"))
    parser.add_argument("--manifest", type=Path, default=Path("faucet-claims.json"))
    parser.add_argument("--open-browser", action="store_true",
                        help="打开每个官方水龙头页面")
    args = parser.parse_args()
    networks = args.network or list(FAUCETS)
    document = json.loads(args.wallet_file.read_text(encoding="utf-8"))
    claims = []
    for wallet in document["wallets"]:
        # 重新推导地址，拒绝损坏或被修改过的钱包 JSON 文件。
        key = PrivateKey(bytes.fromhex(wallet["private_key"]))
        address = key.public_key.to_base58check_address()
        if address != wallet["address"]:
            raise SystemExit(f"address mismatch: {wallet['id']}")
        for network in networks:
            config = FAUCETS[network]
            balance = get_balance(address, config["rpc_url"])
            claims.append({
                "wallet_id": wallet["id"],
                "network": network,
                "network_name": config["name"],
                "address": address,
                "balance_sun": balance,
                "faucet_url": config["faucet_url"],
            })

    args.manifest.write_text(json.dumps({"claims": claims}, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(claims)} claims in {args.manifest}")
    for network in networks:
        config = FAUCETS[network]
        addresses = [c["address"] for c in claims if c["network"] == network]
        url = config["faucet_url"] + "?" + urlencode({"address": addresses[0]})
        print(f"{config['name']}: {config['faucet_url']} ({len(addresses)} addresses)")
        if args.open_browser:
            webbrowser.open(url)


if __name__ == "__main__":
    main()
