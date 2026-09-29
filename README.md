# TRON 测试网钱包

仓库中的 `testnet-wallets.json` 包含 100 个独立的 TRON 测试钱包，供项目的测试环境使用。每个钱包明确配置了两个测试网：

- **Nile Testnet**：`https://nile.trongrid.io`
- **Shasta Testnet**：`https://api.shasta.trongrid.io`

TRON 地址与网络无关，因此同一钱包地址可以分别在 Nile 和 Shasta 使用；余额和交易记录在两个网络之间不会共享。`private_key` 仅用于测试签名，不能用于主网或生产资金。

## 重新生成

需要 Python 3 和 `tronpy`：

```bash
python3 -m pip install tronpy
python3 generate_testnet_wallets.py --count 100 --output testnet-wallets.json
```

脚本使用操作系统的安全随机数源，每次运行都会生成一批全新的账户。生成的 JSON 文件包含 Base58 地址、Hex 地址、私钥和两个测试网的 RPC 配置。请勿将该文件提交到公共仓库或日志系统。
