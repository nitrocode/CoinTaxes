from dateutil import parser as date_parser
import os
from fdfgen import forge_fdf


FORKED_LIST = ['BCH', 'BCC', 'BGD']


def get_forked_time(product):
    """
    TODO: find a better way to do this

    :param product:
    :return:
    """
    if product == 'BCH':
        forked_time = '8/17/2018'
    elif product == 'BGD':
        forked_time = '10/24/2017'
    else:
        print('Unknown fork product: ' + product)
    return forked_time


def get_cost_basis(sells_sorted, buys_sorted, basis_type='highest', tax_year=2017):
    """
    TODO: clean up and break up code

    :param sells_sorted:
    :param buys_sorted:
    :param basis_type:
    :param tax_year:
    :return:
    """
    start_year = date_parser.parse(f'{tax_year}/1/1 00:00:00Z')
    end_year = date_parser.parse(f'{tax_year + 1}/1/1 00:00:00Z')
    full_orders = []
    # Loop through the sell orders and find the best cost basis
    # for sell_index in range(len(sells_sorted)):
    for sell_index, sell_order in enumerate(sells_sorted):
        sell_time = sell_order['order_time']
        product = sell_order['product'].upper()
        # Loop through the buy index to get the cost basis
        # Create a cost basis and subtract sell volume
        # Continue looping until sell volume goes away
        count = 0
        while sell_order['amount'] > 0 and count < 1 and (start_year < sell_time < end_year):
            count = 0
            max_cost_index = -1
            max_cost = 0
            max_cost_volume = -1
            for buy_index, buy_order in enumerate(buys_sorted):
                # See if the buy is the correct product and earlier than the sell time and there are coins left
                if (buy_order['product'] == product) and (sell_time >= buy_order['order_time']) and \
                        (buy_order['amount'] > 0):
                    cost = buy_order['cost_per_coin']
                    # See if the max cost is higher
                    if cost >= max_cost:
                        max_cost_index = buy_index
                        max_cost = cost
                        max_cost_volume = buy_order['amount']
            # If no cost basis was found, see if the coin was forked
            if max_cost_volume < 0 and product in FORKED_LIST:
                print("Found a forked coin")
                print(sell_order)
                # Set forked coin cost basis (0)
                max_cost_volume = sell_order['amount']
            # See if the max cost volume is still negative
            if max_cost_volume < 0:
                print(f"WARNING! COULD NOT FIND A COST BASIS FOR sell_index={sell_index}!")
                print(sell_order)
                count = 1
            else:
                cost_basis_volume = min(max_cost_volume, sell_order['amount'])
                # reduce the buy and sell volumes
                # Make sure the max_cost_index is not -1 (forked coin airdrop)
                if max_cost_index >= 0:
                    bought_time = buys_sorted[max_cost_index]['order_time'].strftime('%m/%d/%Y')
                    buys_sorted[max_cost_index]['amount'] = round(
                        buys_sorted[max_cost_index]['amount'] - cost_basis_volume, 8)
                    cost_basis_per_coin = cost
                else:
                    # This is a forked coin, get the forked date
                    bought_time = get_forked_time(product)
                    cost_basis_per_coin = 0
                sell_order['amount'] = round(sell_order['amount'] - cost_basis_volume, 8)

                # Full order [description, date acquired, date sold, proceeds, cost basis, gain/loss]
                full_orders.append([
                    f'{cost_basis_volume:.8f} {product}',
                    bought_time,
                    sell_order['order_time'].strftime('%m/%d/%Y'),
                    cost_basis_volume * sell_order['cost_per_coin'],
                    cost_basis_volume * cost_basis_per_coin,
                    cost_basis_volume * (sell_order['cost_per_coin'] - cost_basis_per_coin)
                ])
    return full_orders


def add_field(row, col, value):
    """Using a row and column add a fdf field value"""
    return f'topmostSubform[0].Page1[0].Table_Line1[0].Row{row}[0].f1_{col}[0]', value


def add_last_field(col, value):
    """Using a column add a fdf field value at the bottom"""
    if value < 0:
        return f'topmostSubform[0].Page1[0].f1_{col}[0]', f'({abs(value):.2f})'
    else:
        return f'topmostSubform[0].Page1[0].f1_{col}[0]', f'{value:.2f}'

def run_pdftk(main_pdf, file_name, fields, count):
    """Runs pdftk command"""
    file_path = os.path.join('output', file_name)
    irs_form = os.path.join('forms', main_pdf)

    fdf = forge_fdf("", fields, [], [], [])

    base_name = f'{file_path}_{count}'
    fdf_path = f'{base_name}.fdf'
    pdf_path = f'{base_name}.pdf'

    with open(fdf_path, "wb") as fdf_file:
        fdf_file.write(fdf)

    pdftk_cmd = f'pdftk {irs_form} fill_form {fdf_path} output {pdf_path}'
    os.system(pdftk_cmd)
    print(pdftk_cmd)


def make_pdf(fifo_result, file_name, name_of_person, social_security_number, year):
    """
    TODO: break up code

    :param fifo_result: gigantic multidimensional array containing
    
    [
        [
            'description of property',
            'date acquired',
            'date sold',
            'sales price',
            'cost or other basis',
            'gain or loss'
        ]
    ] 
    
    :param file_name:
    :param name_of_person:
    :param social_security_number:
    :return:
    """
    max_rows = 14
    max_cols = 8
    file_count = 0
    fields = [
        ('topmostSubform[0].Page1[0].f1_1[0]', name_of_person),
        ('topmostSubform[0].Page1[0].f1_2[0]', social_security_number)
    ]
    # unsure how this is computed...
    field_nums = [3 + row * max_cols for row in range(max_rows)]

    # initialize
    last_row = [0, 0, 0, 0]
    # row number for the current pdf. resets on new pdf.
    row = 0
    # loop through all FIFO sales
    for idx, sale in enumerate(fifo_result):
        row += 1
        # append to the form
        # field_num = field_nums[idx - 1]
        # print(f"idx={row}!" )
        field_num = field_nums[row-1]
        for i in range(5):
            if type(sale[i]) == float:
                sale_tmp = f'{sale[i]:.2f}'
            else:
                sale_tmp = sale[i]
            fields.append(add_field(row, field_num + i, sale_tmp))

        if (sale[3] - sale[4]) < 0:
            fields.append(add_field(row, field_num + 7, f'({sale[4] - sale[3]:.2f})'))
        else:
            fields.append(add_field(row, field_num + 7, f'{sale[3] - sale[4]:.2f}'))

        last_row[0] += sale[3]
        last_row[1] += sale[4]
        last_row[3] += sale[3] - sale[4]

        # create a new pdf if its the last row on the form or the sale is the last
        if row == max_rows or idx == len(fifo_result) - 1:
            fields.append(add_last_field(115, last_row[0]))
            fields.append(add_last_field(116, last_row[1]))
            if last_row[3] < 0:
                fields.append(add_last_field(118, last_row[3]))
            else:
                fields.append(add_last_field(118, last_row[3]))
            fields.append(("topmostSubform[0].Page1[0].c1_1[2]", 3))

            # save the file and reset the idx
            run_pdftk(f'f8949_{year}.pdf', file_name, fields, file_count)
            file_count += 1

            # reset fields
            fields = []
            last_row = [0, 0, 0, 0]
            row = 0
