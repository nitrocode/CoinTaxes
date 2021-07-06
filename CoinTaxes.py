#!/usr/bin/env python
import argparse

import os
import yaml
import copy

import exchanges
from formats import fill_8949, turbo_tax, spreadsheet


def get_exchange(name, config):
    """Gets the exchange object based on the name and instantiates it

    Source: https://stackoverflow.com/a/1176180/2965993

    :param name: exchange name
    :param config: exchange configuration
    :return:
    """
    return getattr(exchanges, name.title())(config)


def fix_orders(exchange, buys, sells):
    """

    :param exchange:
    :param buys:
    :param sells:
    :return:
    """
    buys_fixed = []
    sells_fixed = []
    for orders in [buys, sells]:
        for order in orders:
            # See if the exchange currency is BTC
            # if order[6] == 'BTC':
            if order['currency'] == 'BTC':
                # This is a coin-coin transaction
                # We need to get the btc value in $$ and create another trade (a sell order)
                price_usd = exchange.get_price(order['order_time'], product='BTC-USD')
                cost_btc = order['cost']
                cost_usd = cost_btc * price_usd
                cost_per_coin_usd = cost_usd / order['amount']
                # get the coin name
                product = order['product']
                # Fix any coin discrepancies (right now call all bitcoin cash BCH, sometimes it is called BCC)
                if product == 'BCC':
                    product = 'BCH'
                if order['buysell'] == 'buy':
                    # buys_fixed.append([
                    #     order['order_time'], product, 'buy', cost_usd, order['amount'], cost_per_coin_usd, 'USD'
                    # ])
                    # sells_fixed.append([
                    #     order['order_time'], 'BTC', 'sell', cost_usd, order['cost'], price_usd, 'USD'
                    # ])
                    buys_fixed.append({
                        'order_time': order['order_time'],
                        'product': product,
                        'currency': 'USD',
                        'currency_pair': product + '-USD', # TODO: review
                        'buysell': 'buy',
                        'cost': cost_usd,
                        'amount': order['amount'],
                        'cost_per_coin': cost_per_coin_usd,
                    })
                    sells_fixed.append({
                        'order_time': order['order_time'],
                        'product': 'BTC',
                        'currency': 'USD',
                        'currency_pair': 'BTC-USD', # TODO: review
                        'buysell': 'sell',
                        'cost': cost_usd,
                        'amount': order['cost'],
                        'cost_per_coin': price_usd,
                    })
                elif order['buysell'] == 'sell':
                    # sells_fixed.append([
                    #     order['order_time'], product, 'sell', cost_usd, order['amount'], cost_per_coin_usd, 'USD'
                    # ])
                    # buys_fixed.append([
                    #     order['order_time'], 'BTC', 'buy', cost_usd, order['cost'], price_usd, 'USD'
                    # ])
                    sells_fixed.append({
                        'order_time': order['order_time'],
                        'product': product,
                        'currency': 'USD',
                        'currency_pair': product + '-USD', # TODO: review
                        'buysell': 'sell',
                        'cost': cost_usd,
                        'amount': order['cost'],
                        'cost_per_coin': price_usd,
                    })
                    # was order['order_time'], product, 'sell', cost_usd, order['amount'], cost_per_coin_usd, 'USD'
                    buys_fixed.append({
                        'order_time': order['order_time'],
                        'product': 'BTC',
                        'currency': 'USD',
                        'currency_pair': 'BTC-USD', # TODO: review
                        'buysell': 'buy',
                        'cost': cost_usd,
                        'amount': order['cost'],
                        'cost_per_coin': price_usd,
                    })
                else:
                    print("WEIRD! Unknown order buy sell type!")
                    print(order)
            else:
                # This order was already paid/received with USD
                if order['buysell'] == 'buy':
                    buys_fixed.append(order)
                elif order['buysell'] == 'sell':
                    sells_fixed.append(order)
                else:
                    print("WEIRD! Unknown order buy/sell type!")
                    print(order)
    return buys_fixed, sells_fixed


def main():
    """Main function to collect information and create the forms."""

    parser = argparse.ArgumentParser(description='CoinTaxes', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input', default='config.yml',
                        help='Configuration file to read.')
    parser.add_argument('--output', default='output',
                        help='Directory to output autogenerated files.')
    args = parser.parse_args()

    # create output directory
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # read yaml config file
    with open(args.input, 'r') as f:
        config = yaml.load(f.read())

    # also shares the name in the configs
    # exchanges_supported = ['gdax', 'coinbase', 'bittrex', 'gemini', 'poloniex']
    exchanges_supported = ['gdax', 'coinbase']

    buys = []
    sells = []

    # go through all supported exchanges
    for exchange_name in exchanges_supported:
        # instantiate the exchange and aggregate the buys and sells
        if exchange_name in config:
            exchange = get_exchange(exchange_name, config[exchange_name])
            if exchange_name == 'bittrex':
                exchange_buys, exchange_sells = exchange.get_buys_sells(order_file=config['bittrex']['file'])
            else:
                exchange_buys, exchange_sells = exchange.get_buys_sells()
            exchange_buys, exchange_sells = fix_orders(exchange, exchange_buys, exchange_sells)
            buys += exchange_buys
            sells += exchange_sells

    # sort the buys and sells by date
    buys_sorted = sorted(buys, key=lambda buy_order: buy_order['order_time'])
    sells_sorted = sorted(sells, key=lambda buy_order: buy_order['order_time'])

    # Get the full order information to be used on form 8949
    full_orders = fill_8949.get_cost_basis(
        copy.deepcopy(sells_sorted), # pass a copy to preserve the original
        copy.deepcopy(buys_sorted),  # pass a copy to preserve the original
        basis_type='highest',
        tax_year=config['year']
    )

    # Save the files in a pickle
    # pickle.dump([buys_sorted, sells_sorted, full_orders], open("save.p", "wb"))

    # Make the Turbo Tax import file
    if 'txf' in config and config['txf']:
        turbo_tax.make_txf(full_orders, year=config['year'])

    # Make the 8949 forms
    if 'fill_8949' in config and config['fill_8949']:
        fill_8949.make_pdf(full_orders, "test", config['name'], config['social'], config['year'])

    if 'spreadsheet' in config and config['spreadsheet']:
        spreadsheet.make_spreadsheet(full_orders, buys_sorted, sells_sorted, year=config['year'])

if __name__ == '__main__':
    main()
