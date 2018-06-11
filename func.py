import time, importlib
from decimal import Decimal, ROUND_DOWN
from app.extensions import db
from services import text_log_serv


def Log(*args):
    contents = ''
    for arg in args:
        contents = contents + str(arg) + '|'

    data = {
        'contents': contents
    }
    text_log_serv.save(**data)
    db.session.commit()


def Sleep(sleep_time):
    time.sleep(sleep_time / 1000)


def _C(func, *args, **kwargs):
    while True:
        result = func(*args, **kwargs)
        if result:
            return result


def _N(num, precision):
    num = float(Decimal(str(num)).quantize(Decimal('0.' + '0' * precision), rounding=ROUND_DOWN))
    return num


def getExchange(class_name, quote_currency, base_currency, access_key, secrect_key):
    module = importlib.import_module('lib.' + class_name)
    exchange = module.Exchange(access_key, secrect_key, quote_currency, base_currency)
    return exchange
