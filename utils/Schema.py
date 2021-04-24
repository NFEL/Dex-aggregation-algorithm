from utils.Redis import get_obj, update, all_pairs, get_obj_async
from utils.math import get_price_token0
from pydantic import BaseModel
import json as _json
import typing


"""
Redis : 
    token:<token-address> -> b'{name:str,symbol:str,pairs:list,address:str}'
    pair:<pair_address> -> b'{dex_address:str,token0:str,token1:str,reserve0:str,reserve1:str}'
"""


class RequestPath(BaseModel):
    fromToken: str
    toToken: str
    amount: typing.Optional[int]
    fee: typing.Optional[float]
    


class Token:
    _tokens = []
    ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WETH_ADDRESS_56 = "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c"
    WETH_ADDRESS_97 = "0xae13d989dac2f0debff460ac112a837c89baa7cd"

    def __init__(self, name, symbol, address, pairs=[]) -> None:
        self.name = name
        self.pairs = pairs
        self.symbol = symbol
        self.address = address
        Token._tokens.append(self)

    def json(self):
        data = {
            "address": self.address,
            "symbol": self.symbol,
            "pairs": self.pairs,
            "name": self.name,
        }
        return _json.dumps(data)

    @classmethod
    def is_ETH(cls, address):
        return address == cls.ETH_ADDRESS

    @classmethod
    def is_WETH(cls, address):
        return address == cls.WETH_ADDRESS_97 or address == cls.WETH_ADDRESS_56

    async def get_ETH_value(self):
        possible_pairs = []
        for pair in await all_pairs():
            pair_obj = await get_obj_async(pair)
            if self.address == pair_obj.token0 and self.is_WETH(pair_obj.token1):
                possible_pairs.append(pair_obj)
        value = 0
        for pair in possible_pairs:
            value += get_price_token0(pair)

        return value / len(possible_pairs)

    def __str__(self) -> str:
        return self.name


class Pair:

    def __init__(self, address, token0, token1, reserve0, reserve1, dex) -> None:
        self.address = address
        self.token0 = token0
        self.token1 = token1
        self.reserve0 = reserve0
        self.reserve1 = reserve1
        self.dex = dex

    def json(self):
        data = {}
        data['address'] = self.address
        data['token0'] = self.token0
        data['token1'] = self.token1
        data['reserve0'] = self.reserve0
        data['reserve1'] = self.reserve1
        data['dex_address'] = self.dex
        return _json.dumps(data)

    def __str__(self) -> str:
        return f'{self.address} - {self.reserve0}  - {self.reserve1}'
