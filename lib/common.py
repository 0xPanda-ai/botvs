import requests, socket, socks, abc, json


class Common:
    def __init__(self, access_key, secret_key, quote_currency, base_currency):
       # socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1086)
       # socket.socket = socks.socksocket
        self.ACCESS_KEY = access_key
        self.SECRET_KEY = secret_key
        self.quote_currency = quote_currency
        self.base_currency = base_currency
        self.symbol = self.get_symbol(quote_currency, base_currency)

    @staticmethod
    def http_get_request(url, params, **kwargs):

        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        }

        if kwargs.get('headers'):
            headers.update(kwargs.pop('headers'))

        response = requests.get(url, params=params, headers=headers, **kwargs)
        try:

            if response.status_code == 200:
                return response.json()
            else:
                return None
        except BaseException as e:
            return None

    @staticmethod
    def http_post_request(url, params, **kwargs):
        headers = {
            "Accept": "application/json",
            'Content-Type': 'application/json'
        }
        if kwargs.get('headers'):
            headers.update(kwargs.pop('headers'))
        postdata = json.dumps(params)
        response = requests.post(url, postdata, headers=headers, timeout=10)
        try:

            if response.status_code == 200:
                return response.json()
            else:
                return
        except BaseException as e:
            print("httpPost failed, detail is:%s,%s" % (response.text, e))
            return

    @abc.abstractmethod
    def get_symbol(self, quote_currency, base_currency):
        pass
