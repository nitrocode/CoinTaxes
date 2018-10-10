from dateutil import parser as date_parser
from coinbase.wallet.client import Client
from exchanges import Exchange


class Coinbase(Exchange):
    client = None

    def __init__(self, config):
        """
        Initialize the client

        :param config: dictionary containing keys `key` and `secret`
        """
        try:
            self.client = Client(config['key'], config['secret'])
            print('Connected to Coinbase.')
        except:
            print('Could not connect to Coinbase.')

    def get_price(self, order_time, product='BTC-USD'):
        """Gets price for a specific day.

        Unfortunately, it does not allow date and time answers.

        :return:
        """
        return self.client.get_spot_price(date=order_time, currency_pair=product)

    def parse_order(self, order, buysell):
        """

        :param order:
        :param buysell:
        :return:
        """
        order_time = date_parser.parse(order['payout_at'])
        product = order['amount']['currency']
        exchange_currency = order['total']['currency']
        currency_pair = '-'.join([order['amount']['currency'], order['total']['currency']])
        cost = float(order['total']['amount'])
        amount = float(order['amount']['amount'])
        cost_per_coin = cost / amount

        return {
            'order_time': order_time,
            'product': product,
            'currency': exchange_currency,
            'currency_pair': currency_pair,
            'buysell': buysell,
            'cost': cost,
            'amount': amount,
            'cost_per_coin': cost_per_coin,
        }

    # get the buys and sells for an account
    def get_account_transactions(self, account):
        """

        :param account:
        :return:
        """
        buys = []
        sells = []
        buys_complex = self.client.get_buys(account['id'])
        sells_complex = self.client.get_sells(account['id'])
        for order in buys_complex['data']:
            buys.append(self.parse_order(order, 'buy'))
        for order in sells_complex['data']:
            sells.append(self.parse_order(order, 'sell'))
        return buys, sells

    def get_buys_sells(self):
        """

        :return:
        """
        # Get the Coinbase accounts
        accounts = self.client.get_accounts()
        buys = []
        sells = []
        for account in accounts['data']:
            # Only use the USD and BTC accounts since they will contain all transaction ids
            if account['currency'] != 'USD':
                buys_dummy, sells_dummy = self.get_account_transactions(account)
                buys += buys_dummy
                sells += sells_dummy
        return buys, sells
