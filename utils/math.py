from .Schema import Pair
from utils.Redis import get_obj

def get_price_token1(reserve0, reserve1):
    assert(reserve1 > 0)
    return reserve0 / reserve1

def get_price_token0(pair_obj):
    assert(isinstance(pair_obj,Pair))
    return pair_obj.reserve1 / pair_obj.reserve0

def get_price_token0(reserve0, reserve1):
    assert(reserve0 > 0)
    return reserve1 / reserve0

def amount_out_with_fee(reserve0, reserve1, amount, fee=0.002) -> float:
    amount *= (1 - fee)
    return reserve1 - (reserve1 * reserve0 / (amount + reserve0))

def amount_out_with_fee_multipair_with_redis(pairs, amount_in, fee=0.002) -> float:
    amount_out = amount_in
    for pair in pairs:
        pair_obj = get_obj(pair, is_pair=True)
        amount_out = amount_out_with_fee(
            pair_obj.reserve0, pair_obj.reserve1, amount_out, fee)
    return amount_out

def amount_out_no_fee(reserve0, reserve1, amount) -> float:
    return reserve1 - (reserve1 * reserve0 / (amount + reserve0))
