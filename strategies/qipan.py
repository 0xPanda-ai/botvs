import os

if os.getenv('PLATFORM'):
    # 如果是本地环境,就加载本地的配置,如果是botvs环境就加载botvs的环境
    from func import _N, _C, Sleep, Log, getExchange
    from robot_conf.qipan import ENTRY_TYPE, BASE_PRICE, SPREADS, BLANCE, NUMBER_GRIDS, STOCKS, BASE_CURREN, \
        QUOTE_CURRENCY, EXCHANGE_NAME, SECRECT_KEY, ACCESS_KEY

    exchange = getExchange(EXCHANGE_NAME, QUOTE_CURRENCY, BASE_CURREN, ACCESS_KEY, SECRECT_KEY)

init_ststus = {}


class Robot():
    def __init__(self, exchange, check_try_time, spreads, base_price, entry_type, number_grids=5, balance=0, stocks=0):
        self.exchange = exchange
        self.exchange.SetPrecision(4, 4)
        self.checkTryTime = check_try_time
        self.spreads = spreads
        self.basePrice = float(base_price)

        self.orderList = []
        self.balance = balance
        self.stocks = stocks
        self.numberGrids = number_grids
        self.entry_type = entry_type

        self.ORDER_STATE_PENDING = 0
        self.ORDER_STATE_CLOSED = 1
        self.ORDER_STATE_CANCELED = 2

        self.ORDER_TYPE_BUY = 0

        self.ORDER_TYPE_SELL = 1
        self.FLOAT_LENGTH = 4

        self.exchange.exchange_name = exchange.GetName()

    def getFee(self):
        """手续费"""
        return {'sell': 0 / 100, 'buy': 0 / 100}

    def orderIsNotExists(self):
        """判断是否有服务器存在的订单,本地却没有的订单,如果存在这种情况就返回 这个订单号"""
        pending_order_list = _C(self.exchange.GetOrders)
        current_order_id_list = [order_info['order_id'] for order_info in self.orderList]
        for order in pending_order_list:
            if order['Id'] not in current_order_id_list:
                return order['Id']
        return False

    def getAccountInfo(self):
        """获取交易所的账号的信息"""
        account_info = _C(self.exchange.GetAccount)
        total_balance = account_info["Balance"] + account_info["FrozenBalance"]
        total_stocks = account_info["Stocks"] + account_info["FrozenStocks"]
        account_info.update({'total_balance': total_balance, 'total_stocks': total_stocks})
        self.printAccountInfo(account_info)
        return account_info

    def generateOrders(self):
        """初始化订单"""
        if self.basePrice == 0:
            ticker = _C(self.exchange.GetTicker);
            base_price = ticker['Last']
        else:
            base_price = self.basePrice

        Log('入手币价:', base_price)
        if self.entry_type:
            Log('法币入场')
            each_balance = _N(self.balance / self.numberGrids, self.FLOAT_LENGTH)
            for i in range(1, self.numberGrids + 1):
                price = _N(base_price * (1 - self.spreads * i), self.FLOAT_LENGTH)
                buy_quantit = _N(each_balance / price, self.FLOAT_LENGTH)
                order_id = self.transaction(self.exchange.Buy, price, buy_quantit, self.ORDER_TYPE_BUY)
                buy_info = {'price': price, 'quantity': buy_quantit, 'type': self.ORDER_TYPE_BUY,
                            'order_id': order_id}
                self.orderList.append(buy_info)
                Sleep(self.checkTryTime)

        else:
            Log('持币入场')
            sellQuantity = _N(self.stocks / self.numberGrids, self.FLOAT_LENGTH)
            for i in range(1, self.numberGrids + 1):
                price = _N(base_price * (1 + self.spreads * i), self.FLOAT_LENGTH)

                order_id = self.transaction(self.exchange.Sell, price, sellQuantity, self.ORDER_TYPE_SELL)
                sell_info = {'price': price, 'quantity': sellQuantity, 'type': self.ORDER_TYPE_SELL,
                             'order_id': order_id}
                self.orderList.append(sell_info)
                Sleep(self.checkTryTime)

        return self.orderList

    def transaction(self, action, price, quantity, order_type):
        """
        下单
        :param action: 
        :param price: 
        :param quantity:
        :param type: 
        :return: 
        """
        while True:
            account_info = self.getAccountInfo()
            self.printAccountInfo(account_info)
            if order_type == self.ORDER_TYPE_SELL:
                if float(account_info['Stocks']) >= quantity:
                    break

            if order_type == self.ORDER_TYPE_BUY:
                if float(account_info['Balance']) >= quantity * price:
                    break

            Log(order_type, '钱或者币数量不够')
            Sleep(self.checkTryTime)

        while True:
            order_id = action(price, quantity)
            if order_id:
                return order_id

            order_id = self.orderIsNotExists()
            if order_id:
                return order_id

            Sleep(self.checkTryTime)

    def run(self):
        """运行搬砖"""
        order_list = self.generateOrders()
        account_info = self.getAccountInfo()
        Log('---------初始化订单成功---------')

        while True:
            order_list = self.checkOrders(order_list)
            Sleep(self.checkTryTime)

    def checkOrders(self, order_list):
        for order in order_list:
            order_info = _C(self.exchange.GetOrder, order['order_id'])
            if order_info['Status'] == self.ORDER_STATE_CLOSED:
                Sleep(self.checkTryTime)
                fee = self.getFee()
                account_info = self.getAccountInfo()
                if order['type'] == self.ORDER_TYPE_BUY:
                    price = _N(order['price'] * (1 + self.spreads), self.FLOAT_LENGTH)
                    quantity = _N(order['quantity'] * (1 - fee.get('buy')), self.FLOAT_LENGTH)
                    order_id = self.transaction(self.exchange.Sell, price, quantity, self.ORDER_TYPE_SELL)
                    new_order = {'price': price, 'quantity': quantity, 'order_id': order_id,
                                 'type': self.ORDER_TYPE_SELL}

                    Log('订单号%s 以%s价格买入%s个币,交易成功,现在以%s价格卖出币' % (
                        order['order_id'], order['price'], order['quantity'], price), '#ff0000@')
                else:

                    price = _N(order['price'] * (1 - self.spreads), self.FLOAT_LENGTH)
                    quantity = _N(order['quantity'] * (1 + fee.get('buy')), self.FLOAT_LENGTH)

                    order_id = self.transaction(self.exchange.Buy, price, quantity, self.ORDER_TYPE_BUY)
                    new_order = {'price': price, 'quantity': quantity, 'order_id': order_id,
                                 'type': self.ORDER_TYPE_BUY}

                    Log('订单号%s 以%s价格卖出%s个币,交易成功,现在以%s价格买入币' % (
                        order['order_id'], order['price'], order['quantity'], price), '#ff0000@')

                order_list.append(new_order)
                order_list.remove(order)
                Log(order_list)
                Log('---------------------------')

        return order_list

    def printAccountInfo(self, account_info):
        """打印交易所账号信息"""
        msg = '定价币总数:%s,基础币总数:%s,剩余定价货币%s,被冻结的定价货币%s,剩余基础货币:%s,被冻结的基础货币%s' % (
            account_info['total_balance'], account_info['total_stocks'], account_info['Balance'],
            account_info['FrozenBalance'], account_info['Stocks'], account_info['FrozenStocks'])

        Log(msg, '#4D4DFF')

    def cancelPendingOrders(self):
        """取消所有未完成挂单"""

        orders = _C(self.exchange.GetOrders)
        for order in orders:
            while True:
                order_status = self.exchange.CancelOrder(order.Id)
                Log(order_status)
                order_info = _C(self.exchange.GetOrder, order.Id)
                if order_info['Status'] == self.ORDER_STATE_CLOSED:
                    break

                if (order_info['Status'] == self.ORDER_STATE_CANCELED):
                    if order_info['Type'] == self.ORDER_TYPE_SELL:
                        order_type = '卖单'
                    else:
                        order_type = '买单'

                    Log('取消了%s,订单号:%s,下单金额%s,下单数量%s,成交量%s,' % (
                        order_type, order_info['Id'], order_info['Price'], order_info['Amount'],
                        order_info['DealAmount']), '#FF0000')
                    break

                Sleep(self.checkTryTime)

        self.orderList = []


def main():
    global init_ststus
    check_try_time = 100  # 重试时间间隔
    robot = Robot(exchange=exchange, check_try_time=check_try_time, spreads=SPREADS, base_price=BASE_PRICE,
                  entry_type=ENTRY_TYPE, balance=BLANCE, stocks=STOCKS, number_grids=NUMBER_GRIDS)
    init_ststus = robot.getAccountInfo()
    Log('开始', "#00FF00")
    robot.run()
