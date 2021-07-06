import datetime
from dateutil import parser as date_parser
import cbpro as gdax
from exchanges import Exchange


class Gdax(Exchange):
    client = None

    def __init__(self, config):
        self.config = config
        """

        :param config:
        """
        self.client = self.get_cached_client('gdax')

    def get_client(self):
        """
        Get real connected client

        :param config:
        :return:
        """
        client = None
        try:
            print('Connected to GDAX.')
            client = gdax.AuthenticatedClient(
                self.config['key'], self.config['secret'], self.config['passphrase']
            )
        except:
            print('Could not connect to GDAX.')
        return client

    def get_order_ids(self, history, ignore_products=[]):
        """
        Get all of the order ids by looping through transaction history.

        :param history:
        :param ignore_products:
        :return:
        """
        order_ids = {}
        for transaction in history:
            if 'order_id' in transaction['details'] and 'product_id' in transaction['details']:
                if transaction['details']['order_id'] not in order_ids and \
                        transaction['details']['product_id'] not in ignore_products:
                    order_ids[transaction['details']['order_id']] = 1
            elif 'source' in transaction['details'] and transaction['details']['source'] == 'fork':
                # this was a forked coin deposit
                print(transaction['amount'] + transaction['details']['ticker'] + " obtained from a fork.")
            elif 'transfer_id' not in transaction['details']:
                print("No order_id or transfer_id in details for the following order (WEIRD!)")
                print(transaction)
        return list(order_ids.keys())

    def parse_order(self, order):
        """
        Normalizes the order.

        :param order: Passed in from client.get_order(order_id)
        :return:
        """
        if order['status'] == 'done':
            fees = float(order['fill_fees'])
            # currency pair
            pair = order['product_id'].split('-')
            product = pair[0]
            exchange_currency = pair[1]
            amount = float(order['filled_size'])
            cost = float(order['executed_value'])
            if order['side'] == 'sell':
                cost -= fees
            else:
                cost += fees
            cost_per_coin = cost / amount
        else:
            print('Order status is not done! (WEIRD)')
            print(order)

        return {
            'order_time': date_parser.parse(order['done_at']),
            'product': product,
            'currency': exchange_currency,
            'currency_pair': order['product_id'],
            'buysell': order['side'],
            'cost': cost,
            'amount': amount,
            'cost_per_coin': cost_per_coin,
        }

    # get the buys and sells for an account
    def get_account_transactions(self, account, ignore_products=[]):
        """

        :param account:
        :param ignore_products:
        :return:
        """
        # Get the account history
        history = self.client.get_account_history(account['id'])
        # Get all order ids from the account
        order_ids = self.get_order_ids(history, ignore_products=ignore_products)

        # Get the information from each order_id
        sells = []
        buys = []
        for order_id in order_ids:
            order = self.parse_order(self.client.get_order(order_id))

            if len(order['product']) < 3:
                print('WEIRD ORDER. NO PRODUCT!!!')

            # put order in a buy or sell list
            if order['buysell'] == 'sell':
                sells.append(order)
            elif order['buysell'] == 'buy':
                buys.append(order)
            else:
                print('order is not buy or sell! WEIRD')
                print(order)

        return buys, sells

    def get_price(self, order_time, product='BTC-USD'):
        """
        Get the price of a specific pair from an hour before the order took place.

        :param order_time:
        :param product: currency pair
        :return:
        """
        history = self.client.get_product_historic_rates(
            product_id=product,
            start=order_time - datetime.timedelta(hours=1),
            end=order_time
        )
        price = history[0][4]
        return price

    def get_buys_sells(self):
        """
        Get the buys and sells for all orders.

        :return:
        """
        # Get the GDAX accounts
        accounts = self.client.get_accounts()
        for account in accounts:
            # Only use the USD and BTC accounts since they will contain all transaction ids
            if account['currency'] == 'USD':
                [buys_usd, sells_usd] = self.get_account_transactions(account)
            elif account['currency'] == 'BTC':
                [buys_btc, sells_btc] = self.get_account_transactions(account, ignore_products=['BTC-USD'])
            # elif account['currency'] == 'ETH':
            #     [buys_btc, sells_btc] = get_account_transactions(client, account, ignore_products=['ETH-USD'])
        return buys_usd + buys_btc, sells_usd + sells_btc
