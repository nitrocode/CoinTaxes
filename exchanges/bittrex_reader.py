# This will read in bittrex transactions
# Note that you must supply the fullOrders.csv file
# This only works with BTC transactions!!!!
import csv

import dateutil.parser


class Bittrex(object):
    client = None
    order_file = None

    def __init__(self, config):
        """

        :param config:
        """
        self.order_file = config['file']

    def parse_order(self, order):
        """

        :param order:
        :return:
        """
        # product = order['product_id'][order['product_id'].index('-') + 1:]
        # exchange_currency = order['product_id'][0:order['product_id'].index('-')]
        pair = order['product_id'].split('-')
        product = pair[0]
        exchange_currency = pair[1]
        amount = float(order['cost'])
        fees = float(order[5])
        if 'SELL' in order['buysell']:
            buysell = 'sell'
            cost = float(order[6]) - fees
        elif 'BUY' in order['buysell']:
            buysell = 'buy'
            cost = float(order[6]) + fees
        else:
            print('UNKNOWN BUY/SELL ORDER!!')
            print(order)
            return {}
        cost_per_coin = cost / amount
        order_time = dateutil.parser.parse(order[8] + " UTC")
        return {
            'order_time': order_time,
            'product': product,
            'currency': exchange_currency,
            'currency_pair': order['product_id'],
            'buysell': buysell,
            'cost': cost,
            'amount': amount,
            'cost_per_coin': cost_per_coin,
        }

    def get_buys_sells(self):
        """

        :return:
        """
        # Get the buys and sells for all orders
        buys = []
        sells = []
        print('Loading Bittrex orders from ' + self.order_file)
        # First make sure there are no NULL bytes in the file
        with open(self.order_file, 'rb') as csvfile:
            reader = csv.reader((line.replace('\0', '') for line in csvfile))
            first_row = True
            for row in reader:
                # ignore the header line
                if first_row:
                    first_row = False
                elif len(row) > 0:
                    order = self.parse_order(row)
                    if order['buysell'] == 'buy':
                        buys.append(order)
                    elif order['buysell'] == 'sell':
                        sells.append(order)
                    else:
                        print("WEIRD! Order is neither buy nor sell!")
                        print(order)
        print('Done parsing Bittrex orders!')
        return buys, sells
