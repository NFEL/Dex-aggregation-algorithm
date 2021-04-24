import redis
import json
import math
import pickle
import web3
from .Schema import Pair, Token, RequestPath
from .Redis import get_obj,update
from .math import *


c = redis.Redis(db=4)


async def find(request: RequestPath):


    def expand_via_redis(from_token, to_token, amountIn, route_length=2, _path=[], path=[], tr_fee=0):
        if route_length == 0:
            return
        token0 = get_obj(from_token, is_token=True)

        for pair in token0.pairs:
            path_so_far = _path + [pair]
            pair_obj = get_obj(pair, is_pair=True)

            amount_out = amount_out_with_fee(pair_obj.reserve0,
                                             pair_obj.reserve1,
                                             amountIn)
            if pair_obj.token1 == to_token:
                path.append({
                    'path': path_so_far,
                    'amount_out': amount_out}
                )
                continue
            expand_via_redis(pair_obj.token1, to_token,
                             amount_out, route_length-1, path_so_far)

        return path

    values = {
        "usdt": "0.00277691",
        "dai": "0.00278376",
        "ada": "0.00326817",
        "bake": "0.00282223"
    }

    start = get_obj(request.fromToken)
    end = get_obj(request.toToken)
    amount = 1 * math.pow(10, 18)
    fee = "0.00270000"

    transaction_in_a_path = math.ceil(
        math.log(amount * float(await end.get_ETH_value()) / float(fee), 8))

    v = expand_via_redis(start, end, amount, transaction_in_a_path, tr_fee=fee)

    def buy_from_this(path, amount_in, amount_out):
        for pair in path:
            pair_obj = pickle.loads(c.get(f'pair:{pair}'))
            amount_out_tmp = amount_out_with_fee(
                pair_obj.reserve0, pair_obj.reserve1, amount_in)
            pair_obj.reserve0 -= amount_in
            pair_obj.reserve1 -= amount_out_tmp
            amount_in = amount_out_tmp
            update(pair_obj.name, pair_obj, pair_prefix=True)

        # if amount_out_tmp != amount_out:
        #     raise ValueError(f"sth bad Happened :) {amount_out - amount_out_tmp}")

    part = 100
    buy_from = {}
    for path in v:
        path = path['path']
        buy_from[tuple(path)] = 0

    for i in range(1, part, 1):
        highest_bid = 0
        candidate = None
        for path in v:
            path = path['path']
            bid = amount_out_with_fee_multipair_with_redis(path, amount/part)
            if highest_bid < bid:
                candidate = path
                highest_bid = bid
        buy_from_this(candidate, amount/part, highest_bid)
        buy_from[tuple(candidate)] += 1

    print(buy_from)

    return buy_from


'''
##Pair reserve request

request -> {
    address : DEX_pool Address
}
response -> {
    reserve0 = token0
    reserve1 = token1
}

logic :
    token0 -> token1 : reserve1 (price impact)
    token1 -> token0 : reserve0 (price impact)
'''


{('DAI-BUSD-pan',): 0, ('DAI-BUSD-burger',)
  : 0, ('DAI-USDT-pan', 'USDT-BUSD-pan'): 99}
[{'path': ['DAI-BUSD-pan'], 'amount_out': 1.999266482259126e+19},
 {'path': ['DAI-BUSD-burger'], 'amount_out': 1000.0},
 {'path': ['DAI-USDT-pan', 'USDT-BUSD-pan'], 'amount_out': 1.9945719425591673e+19}]
