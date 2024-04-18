import sys

if sys.version_info >= (3, 10):
    import collections.abc
    sys.modules['collections.Mapping'] = collections.abc.Mapping
    sys.modules['collections.MutableMapping'] = collections.abc.MutableMapping
    sys.modules['collections.Sequence'] = collections.abc.Sequence
    sys.modules['collections.Iterable'] = collections.abc.Iterable
    sys.modules['collections.Hashable'] = collections.abc.Hashable


from bitcoinlib.wallets import Wallet as BitcoinWallet
from eth_keys import keys
import os
from eth_utils import to_checksum_address as eth_to_checksum_address
from tronapi import Tron

private_key = os.urandom(32)
def generate_bitcoin_address():
    wallet = BitcoinWallet.create(private_key)
    key = wallet.new_key(private_key)
    return key.address


def generate_ethereum_address():
    # 生成32字节的随机数作为私钥
    private_key_bytes = os.urandom(32)
    private_key = keys.PrivateKey(private_key_bytes)

    # 从私钥获取公钥
    public_key = private_key.public_key

    # 计算地址
    address = public_key.to_checksum_address()

    return address, private_key


def generate_tron_address():
    tron = Tron()
    account = tron.create_account
    return account.address, account.private_key


if __name__ == "__main__":
    btc_address = generate_bitcoin_address()
    eth_address = generate_ethereum_address()
    tron_address, tron_private_key = generate_tron_address()

    print(f"Bitcoin Address: {btc_address}")
    print(f"Ethereum Address: {eth_address}")
    print(f"Tron Address: {tron_address}")
    print(f"Tron Private Key (WARNING: Keep this safe!): {tron_private_key}")
