import re


def is_valid_bitcoin_address(address: str) -> bool:
    # 简化的比特币地址验证规则
    return re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', address) is not None

def is_valid_ethereum_address(address: str) -> bool:
    # 简化的以太坊地址验证规则
    return re.match(r'^0x[a-fA-F0-9]{40}$', address) is not None

def is_valid_tron_address(address: str) -> bool:
    # 简化的TRON地址验证规则
    return re.match(r'^T[a-zA-Z0-9]{33}$', address) is not None

if __name__ == '__main__':
    print(is_valid_bitcoin_address('1FoerXbdBKr9bVFP3cFpyNFhJZ8rXZdDLx'))