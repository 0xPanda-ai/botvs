# -*- coding: utf-8 -*-

from .common import Common
from constants import *
from func import _N, _C

import base64
import datetime
import hashlib
import hmac
import urllib
import urllib.parse
import urllib.request


class Service(Common):
    # e052bd66-424f0c16-ea398791-f3841
    # e1368ec2-ca459353-2b97a1b2-7c965


    # 7f80ef59-ba8d4dc0-51957f5a-40785
    # f7041765-c81c6671-cf19b32c-3f48d

    MARKET_URL = "https://api.huobi.br.com"
    TRADE_URL = "https://api.huobi.br.com"

    def __init__(self, access_key, secrect_key, quote_currency, base_currency):
        Common.__init__(self, access_key, secrect_key, quote_currency, base_currency)
        account = _C(self.get_accounts)

        self.account_id = account['data'][0]['id']

    def get_kline(self, period, size=150):
        """
         获取KLine
        :param period: 可选值：{1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
        :param size: 可选值： [1,2000]
        :return:
        """
        params = {'symbol': self.symbol,
                  'period': period,
                  'size': size}

        url = self.MARKET_URL + '/market/history/kline'
        origin_datas = self.http_get_request(url, params)
        return origin_datas

    def get_depth(self, option='step0'):
        """
        获取市场深度
        :param option: 可选值：{ percent10, step0, step1, step2, step3, step4, step5 }
        :return:
        """
        params = {'symbol': self.symbol,
                  'type': option}

        url = self.MARKET_URL + '/market/depth'
        origin_datas = self.http_get_request(url, params)
        return origin_datas

    def get_trade(self):
        """
        获取简介的行情数据
        :return:
        """
        params = {'symbol': self.symbol}

        url = self.MARKET_URL + '/market/trade'
        return self.http_get_request(url, params)

    def get_ticker(self):
        """
        获取聚合行情
        :return:
        """
        params = {'symbol': self.symbol}

        url = self.MARKET_URL + '/market/detail/merged'
        return self.http_get_request(url, params)

    def get_history_trade(self, size):
        """
         批量获取最近的交易记录
        :param size: 要查询的条数 1-2000
        :return: 
        """
        params = {
            'symbol': self.symbol,
            'size': size,
        }

        url = self.MARKET_URL + '/market/history/trade'
        origin_datas = self.http_get_request(url, params)
        return origin_datas

    # 获取 Market Detail 24小时成交量数据
    def get_detail(self):
        """
        :return:
        """
        params = {'symbol': self.symbol}

        url = self.MARKET_URL + '/market/detail'
        return self.http_get_request(url, params)

    def get_symbols(self, long_polling=None):
        """
        查询交易所支持的交易对
        :param long_polling: 
        :return: 
        """
        params = {}
        if long_polling:
            params['long-polling'] = long_polling
        path = '/v1/common/symbols'
        return self.api_key_get(params, path)

    def is_suport(self):
        datas = _C(self.get_symbols)
        for data in datas.get('data'):
            if data.get('base-currency') == self.base_currency and data.get('quote-currency') == self.quote_currency:
                self.price_precision = data.get('price-precision')
                self.amount_precision = data.get('amount-precision')
                return True

        return False

    def get_accounts(self):
        """
        查询用户的账号id
        :return: 
        """
        path = "/v1/account/accounts"
        params = {}
        return self.api_key_get(params, path)

    # 获取当前账户资产
    def get_balance(self, acct_id=None):
        """
        :param acct_id
        :return:
        """
        if not acct_id:
            accounts = self.get_accounts()
            acct_id = accounts['data'][0]['id'];

        url = "/v1/account/accounts/{0}/balance".format(acct_id)
        params = {"account-id": acct_id}
        return self.api_key_get(params, url)

    def send_order(self, _type, amount, price=0, source='api'):
        """
        创建并执行订单
        :param amount: 
        :param source: 如果使用借贷资产交易，请在下单接口,请求参数source中填写'margin-api'
        :param _type: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param price: 
        :return: 
        """

        params = {"account-id": self.account_id,
                  "amount": amount,
                  "symbol": self.symbol,
                  "type": _type,
                  "source": source}
        if price:
            params["price"] = price

        url = '/v1/order/orders/place'
        return self.api_key_post(params, url)

    def cancel_order(self, order_id):
        """
        取消订单
        :param order_id: 
        :return: 
        """
        params = {}
        url = "/v1/order/orders/{0}/submitcancel".format(order_id)
        return self.api_key_post(params, url)

    def order_info(self, order_id):
        """
        查询某个订单详情
        :param order_id: 
        :return: 
        """
        params = {}
        url = "/v1/order/orders/{0}".format(order_id)
        return self.api_key_get(params, url)

    def order_matchresults(self, order_id):
        """
        查询某个订单的成交明细
        :param order_id: 
        :return: 
        """
        params = {}
        url = "/v1/order/orders/{0}/matchresults".format(order_id)
        return self.api_key_get(params, url)

    def orders_list(self, states, types=None, start_date=None, end_date=None, _from=None, direct=None, size=None):
        """
        查询当前委托、历史委托
        :param states: 可选值 {pre-submitted 准备提交, submitted 已提交, partial-filled 部分成交, partial-canceled 部分成交撤销, filled 完全成交, canceled 已撤销}
        :param types: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param start_date: 
        :param end_date: 
        :param _from: 
        :param direct: 可选值{prev 向前，next 向后}
        :param size: 
        :return: 
        """
        params = {'symbol': self.symbol,
                  'states': states}

        if types:
            params[types] = types
        if start_date:
            params['start-date'] = start_date
        if end_date:
            params['end-date'] = end_date
        if _from:
            params['from'] = _from
        if direct:
            params['direct'] = direct
        if size:
            params['size'] = size
        url = '/v1/order/orders'
        return self.api_key_get(params, url)

    def orders_matchresults(self, types=None, start_date=None, end_date=None, _from=None, direct=None,
                            size=None):
        """
        查询当前成交、历史成交
        :param types: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param start_date: 
        :param end_date: 
        :param _from: 
        :param direct: 可选值{prev 向前，next 向后}
        :param size: 
        :return: 
        """
        params = {'symbol': self.symbol}

        if types:
            params[types] = types
        if start_date:
            params['start-date'] = start_date
        if end_date:
            params['end-date'] = end_date
        if _from:
            params['from'] = _from
        if direct:
            params['direct'] = direct
        if size:
            params['size'] = size
        url = '/v1/order/matchresults'
        return self.api_key_get(params, url)

    def api_key_get(self, params, request_path):
        method = 'GET'
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        params.update({'AccessKeyId': self.ACCESS_KEY,
                       'SignatureMethod': 'HmacSHA256',
                       'SignatureVersion': '2',
                       'Timestamp': timestamp})

        host_url = self.TRADE_URL
        host_name = urllib.parse.urlparse(host_url).hostname
        host_name = host_name.lower()
        params['Signature'] = self.createSign(params, method, host_name, request_path, self.SECRET_KEY)

        url = host_url + request_path
        return self.http_get_request(url, params)

    def api_key_post(self, params, request_path):
        method = 'POST'
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        params_to_sign = {'AccessKeyId': self.ACCESS_KEY,
                          'SignatureMethod': 'HmacSHA256',
                          'SignatureVersion': '2',
                          'Timestamp': timestamp}

        host_url = self.TRADE_URL
        host_name = urllib.parse.urlparse(host_url).hostname
        host_name = host_name.lower()
        params_to_sign['Signature'] = self.createSign(params_to_sign, method, host_name, request_path, self.SECRET_KEY)
        url = host_url + request_path + '?' + urllib.parse.urlencode(params_to_sign)
        return self.http_post_request(url, params)

    @staticmethod
    def createSign(pParams, method, host_url, request_path, secret_key):
        sorted_params = sorted(pParams.items(), key=lambda d: d[0], reverse=False)
        encode_params = urllib.parse.urlencode(sorted_params)
        payload = [method, host_url, request_path, encode_params]
        payload = '\n'.join(payload)
        payload = payload.encode(encoding='UTF8')
        secret_key = secret_key.encode(encoding='UTF8')

        digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest)
        signature = signature.decode()
        return signature

    def get_symbol(self, quote_currency, base_currency):
        symbol = base_currency + quote_currency
        is_suport = self.is_suport()
        if not is_suport:
            raise BaseException('交易对不支持')
        return symbol


class Exchange(Service):
    order_status = {
        'filled': ORDER_STATE_CLOSED,
        'canceled': ORDER_STATE_CANCELED,
        'pre-submitted': ORDER_STATE_PENDING,
        'submitting': ORDER_STATE_PENDING,
        'submitted': ORDER_STATE_PENDING,
        'partial-filled': ORDER_STATE_PENDING,
        'partial-canceled': ORDER_STATE_PENDING,
    }

    order_type = {
        'buy-limit': ORDER_TYPE_BUY,
        'sell-limit': ORDER_TYPE_SELL,
    }

    @staticmethod
    def check_response_status(data):

        if not data or data.get('status') == 'error':
            return None
        return True

    def GetRecords(self, period='1min', size=10):
        origin_datas = self.get_kline(period, size)
        if not self.check_response_status():
            return None
        data_list = []
        for origin_data in origin_datas.get('data'):
            data = {
                "Open": origin_data.get('open'),
                "Close": origin_data.get('close'),
                "High": origin_data.get('high'),
                "Low": origin_data.get('low'),
                "Volume": origin_data.get('open'),
                "Time": origin_data.get('id'),
            }
            data_list.append(data)
        return data_list

    def GetDepth(self):
        origin_datas = self.get_depth()
        if not self.check_response_status(origin_datas):
            return None

        bids_list = []

        for origin_bid in origin_datas['tick'].get('bids'):
            bid = {
                'Price': origin_bid[0],
                'Amount': origin_bid[1],
            }
            bids_list.append(bid)

        asks_list = []
        for origin_ask in origin_datas['tick'].get('asks'):
            ask = {
                'Price': origin_ask[0],
                'Amount': origin_ask[1],
            }
            asks_list.append(ask)

        data = {
            'Asks': asks_list,
            'Bids': bids_list,
        }
        return data

    def GetTicker(self):
        origin_datas = self.get_ticker()

        if not self.check_response_status(origin_datas):
            return None

        ticker = origin_datas.get('tick')
        data = {"High": ticker.get('high'),
                "Low": ticker.get('low'),
                "Sell": ticker.get('ask')[0],
                "Buy": ticker.get('bid')[0],
                "Last": ticker.get('close'),
                "Volume:": ticker.get('amount'),
                "info": ticker
                }

        return data

    def GetTrades(self, size=10):
        origin_datas = self.get_history_trade(size=size)
        if not self.check_response_status(origin_datas):
            return None

        data_list = []
        for origin_data in origin_datas.get('data'):
            sub_data = origin_data.get('data')[0]
            direction = 1 if sub_data.get('direction') == 'sell' else 0
            data = {
                "id": sub_data.get('id'),
                "time": sub_data.get('ts'),
                "Price": sub_data.get('price'),
                "Amount": sub_data.get('amount'),
                "Type": direction,
            }
            data_list.append(data)

        return data_list

    def GetAccount(self):
        origin_data = self.get_balance(self.account_id)
        if not self.check_response_status(origin_data):
            return None

        currencys = origin_data.get('data').get('list')

        for data in currencys:
            if data.get('currency') == self.base_currency and data.get('type') == 'trade':
                stocks = data.get('balance')
            if data.get('currency') == self.base_currency and data.get('type') == 'frozen':
                frozen_stocks = data.get('balance')
            if data.get('currency') == self.quote_currency and data.get('type') == 'trade':
                balance = data.get('balance')
            if data.get('currency') == self.quote_currency and data.get('type') == 'frozen':
                frozen_balance = data.get('balance')

        info = {
            "Balance": balance or None,
            "FrozenBalance": frozen_balance or None,
            "Stocks": stocks or None,
            "FrozenStocks": frozen_stocks or None
        }

        return info

    @staticmethod
    def GetName():
        return '火币'

    def GetCurrency(self):
        return self.symbol

    def GetQuoteCurrency(self):
        return self.quote_currency

    def transaction(self, _type, amount, price):
        """
        现货限价交易
        :param amount: 
        :param price: 
        :return: 
        """

        price = _N(price, self.price_precision)
        amount = _N(amount, self.amount_precision)
        data = self.send_order(_type=_type, amount=amount, price=price)
        if not self.check_response_status(data):
            return None
        if data.get('status') == 'ok':
            return data.get("data")
        return None

    def Buy(self, price, amount):
        return self.transaction(_type='buy-limit', amount=amount, price=price)

    def Sell(self, price, amount):
        return self.transaction(_type='sell-limit', amount=amount, price=price)

    def CancelOrder(self, order_id):
        data = self.cancel_order(order_id)
        if data.get('status') == 'ok':
            return True
        return None

    def GetOrder(self, order_id):
        origin_info = self.order_info(order_id)
        if not self.check_response_status(origin_info):
            return None

        data = origin_info.get('data')

        info = {
            'Info': origin_info,
            'Id': data.get('id'),
            'Price': data.get('price'),
            'Amount': data.get('amount'),
            'DealAmount': data.get('field-amount'),
            'AvgPrice': 0,
            'Status': self.order_status.get(data.get('state')),
            'Type': self.order_type.get(data.get('type'))
        }

        return info

    def GetOrders(self):
        states = 'pre-submitted,submitting,submitted,partial-filled,partial-canceled'
        origin_data = self.orders_list(states=states, );
        if not self.check_response_status(origin_data):
            return None

        order_list = []
        for data in origin_data.get('data'):
            info = {
                'Id': data.get('id'),
                'Price': data.get('price'),
                'Amount': data.get('amount'),
                'DealAmount': data.get('field-amount'),
                'AvgPrice': 0,
                'Status': self.order_status.get(data.get('state')),
                'Type': self.order_type.get(data.get('type'))
            }
            order_list.append(info)

        return order_list

    def SetPrecision(self, price_precision, amount_precision):
        self.price_precision = min(self.price_precision, price_precision)
        self.amount_precision = min(self.price_precision, amount_precision)
