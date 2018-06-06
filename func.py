import time, importlib
from decimal import Decimal, ROUND_DOWN


def Log(**kwargs):
    print(kwargs)


def Sleep(time):
    time.sleep(time)


def _C(func):
    pass


def _N(num, precision):
    num = float(Decimal(str(num)).quantize(Decimal('0.' + '0' * precision), rounding=ROUND_DOWN))
    return num


def getExchange(class_name, quote_currency, base_currency):
    global exchange
    module = importlib.import_module('lib.' + class_name)
    # exchange = module.Exchange('e052bd66-424f0c16-ea398791-f3841', 'e1368ec2-ca459353-2b97a1b2-7c965', quote_currency,base_currency)
    exchange = module.Exchange('7f80ef59-ba8d4dc0-51957f5a-40785', 'f7041765-c81c6671-cf19b32c-3f48d', quote_currency,
                               base_currency)
    return exchange
