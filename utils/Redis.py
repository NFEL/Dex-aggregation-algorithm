from .Schema import Pair, Token
import redis as _redis
import json

c = _redis.Redis(db=4)

PAIR_PREFIX = "pair:"
TOKEN_PREFIX = "token:"



def get_pair_obj(key):
    data = json.loads(c.get(key))
    return Pair(
        key,
        data['token0'],
        data['token1'],
        data['reserve0'],
        data['reserve1'],
        data['dex_address'])


def get_token_obj(key):
    data = json.loads(c.get(key))
    return Token(
        data['name'],
        data['symbol'],
        key,
        data['decimals'])

async def get_obj_async(key, is_token=False, is_pair=False):
    return get_obj(key, is_token, is_pair)

## key can either have prefix or no which results in Token() or Pair()
def get_obj(key, is_token=False, is_pair=False):
    if isinstance(key, str):
        if is_token:
            return get_token_obj(TOKEN_PREFIX + key)

        if is_pair :
            return get_pair_obj(PAIR_PREFIX + key)

        if PAIR_PREFIX in key:
            return get_pair_obj(key)

        if TOKEN_PREFIX in key:
            return get_token_obj(key)
    else:
        assert(isinstance(key,Pair) or isinstance(key,Token),"Bad Key Type")

def update(key, value, add_pair=False, pair_prefix=False, ):
    if add_pair and isinstance(value, str):
        if TOKEN_PREFIX not in key:
            key = TOKEN_PREFIX + key
        obj = get_obj(key)
        obj.pairs.append(value)
        return c.set(key, obj.json())
    elif pair_prefix:
        if isinstance(value, Pair):
            return c.set(PAIR_PREFIX + key, value.json())
        else:
            raise ValueError("BAD OBJECT :)")

    else:
        raise Exception('Need flag tag')


async def all_tokens():
    return c.keys(TOKEN_PREFIX + "*")


async def all_pairs():
    return c.keys(PAIR_PREFIX + "*")


async def sync_pairs():
    for token in all_tokens():
        for pair in all_pairs():
            if get_obj(pair).token0 == token:
                update(token, pair, add_pair=True)
