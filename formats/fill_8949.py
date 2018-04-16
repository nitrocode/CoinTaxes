import dateutil.parser
import os
from fdfgen import forge_fdf

FORKED_LIST = ['BCH', 'BCC', 'BGD']


def get_forked_time(product):
    """

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

    :param sells_sorted:
    :param buys_sorted:
    :param basis_type:
    :param tax_year:
    :return:
    """
    start_year = dateutil.parser.parse('%d/1/1 00:00:00Z' % tax_year)
    end_year = dateutil.parser.parse('%d/1/1 00:00:00Z' % (tax_year + 1))
    full_orders = []
    # Loop through the sell orders and find the best cost basis
    # for sell_index in range(len(sells_sorted)):
    for sell_order in sells_sorted:
        # sell_order = sells_sorted[sell_index]
        sell_time = sell_order['order_time']
        product = sell_order['product']
        # Loop through the buy index to get the cost basis
        # Create a cost basis and subtract sell volume
        # Continue looping until sell volume goes away
        count = 0
        while sell_order['amount'] > 0 and count < 1 and (start_year < sell_time < end_year):
            count = 0
            max_cost_index = -1
            max_cost = 0
            max_cost_volume = -1
            for buy_index in range(len(buys_sorted)):
                buy_order = buys_sorted[buy_index]
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
                max_cost = 0
                max_cost_volume = sell_order['amount']
            # See if the max cost volume is still negative
            if max_cost_volume < 0:
                print("WARNING! COULD NOT FIND A COST BASIS FOR sell_index=%d!" % sell_index)
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
                full_orders.append(['%1.8f ' % cost_basis_volume + product,
                                    bought_time,
                                    sell_order['order_time'].strftime('%m/%d/%Y'),
                                    cost_basis_volume * sell_order['cost_per_coin'],
                                    cost_basis_volume * cost_basis_per_coin,
                                    cost_basis_volume * (sell_order['cost_per_coin'] - cost_basis_per_coin)])
    return full_orders


def makePDF(fifoResult, fname, person, social):
    """

    :param fifoResult:
    :param fname:
    :param person:
    :param social:
    :return:
    """
    # Write to the PDF

    fpath = os.path.join('output', fname)
    irs_form = os.path.join('forms', 'f8949.pdf')

    counter = 0
    fileCounter = 0
    fields = [('topmostSubform[0].Page1[0].f1_1[0]', person),
              ('topmostSubform[0].Page1[0].f1_2[0]', social)]
    fnums = [3 + i * 8 for i in range(14)]
    lastRow1 = 0
    lastRow2 = 0
    lastRow3 = 0
    lastRow4 = 0
    # loop through all FIFO sales
    for sale in fifoResult:
        counter += 1
        # append to the form
        row = counter
        fnum = fnums[row - 1]
        fields.append(('topmostSubform[0].Page1[0].Table_Line1[0].Row%d[0].f1_%d[0]' % (row, fnum), sale[0]))
        fields.append(('topmostSubform[0].Page1[0].Table_Line1[0].Row%d[0].f1_%d[0]' % (row, fnum + 1), sale[1]))
        fields.append(('topmostSubform[0].Page1[0].Table_Line1[0].Row%d[0].f1_%d[0]' % (row, fnum + 2), sale[2]))
        fields.append(
            ('topmostSubform[0].Page1[0].Table_Line1[0].Row%d[0].f1_%d[0]' % (row, fnum + 3), "%1.2f" % sale[3]))
        fields.append(
            ('topmostSubform[0].Page1[0].Table_Line1[0].Row%d[0].f1_%d[0]' % (row, fnum + 4), "%1.2f" % sale[4]))
        if (sale[3] - sale[4]) < 0:
            fields.append(('topmostSubform[0].Page1[0].Table_Line1[0].Row%d[0].f1_%d[0]' % (row, fnum + 7),
                           "(%1.2f)" % (sale[4] - sale[3])))
        else:
            fields.append(('topmostSubform[0].Page1[0].Table_Line1[0].Row%d[0].f1_%d[0]' % (row, fnum + 7),
                           "%1.2f" % (sale[3] - sale[4])))

        lastRow1 += float("%1.2f" % sale[3])
        lastRow2 += float("%1.2f" % sale[4])
        lastRow3 += 0
        lastRow4 += float("%1.2f" % (sale[3] - sale[4]))

        # create a new pdf
        if row == 14 or sale == fifoResult[-1]:
            fields.append(("topmostSubform[0].Page1[0].f1_115[0]", "%1.2f" % lastRow1))
            fields.append(("topmostSubform[0].Page1[0].f1_116[0]", "%1.2f" % lastRow2))
            if lastRow4 < 0:
                fields.append(("topmostSubform[0].Page1[0].f1_118[0]", "(%1.2f)" % abs(lastRow4)))
            else:
                fields.append(("topmostSubform[0].Page1[0].f1_118[0]", "%1.2f" % lastRow4))
            fields.append(("topmostSubform[0].Page1[0].c1_1[2]", 3))
            # save the file and reset the counter
            fdf = forge_fdf("", fields, [], [], [])
            with open(fpath + "_%03d.fdf" % fileCounter, "w") as fdf_file:
                fdf_file.write(fdf)

            # call PDFTK to make the PDF
            os.system("pdftk " + irs_form + " fill_form " + fpath + "_%03d.fdf" % fileCounter + " output " +
                      fpath + "_%03d.pdf" % fileCounter)

            counter = 0
            fileCounter += 1
            fields = []
            lastRow1 = 0
            lastRow2 = 0
            lastRow3 = 0
            lastRow4 = 0

# # Make the pdfs
# if not os.path.exists("FDFs"):
#     os.makedirs("FDFs")
# if not os.path.exists("PDFs"):
#     os.makedirs("PDFs")
#
# bFIFO = FIFO(btcBoughtSorted, btcSold, "bitcoin")
# eFIFO = FIFO(ethBoughtSorted, ethSold, "ethereum")
# lFIFO = FIFO(ltcBoughtSorted, ltcSold, "litecoin")
#
# print('Filling out the 8949 forms...')
# makePDF(bFIFO, "bitcoin", myname, ss)
# makePDF(eFIFO, "ethereum", myname, ss)
# makePDF(lFIFO, "litecoin", myname, ss)
# # delete the FDFs directory
# os.system("rmdir FDFs")
# print('Done!')
