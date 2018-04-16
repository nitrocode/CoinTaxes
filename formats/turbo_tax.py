# This deals with all Turbo Tax related things
import datetime
import os


def make_txf(full_orders, output_dir='output', year=2017):
    file_name = os.path.join(output_dir, '_'.join(['TurboTax', 'Crypto', str(year)])) + '.txf'
    with open(file_name, "w") as text_file:
        # Write the header
        text_file.write("V042\n")
        text_file.write("ACyrptoTaxes\n")
        text_file.write("D " + datetime.datetime.now().strftime('%m/%d/%Y') + "\n")
        text_file.write("^\n")
        for order in full_orders:
            text_file.write("TD\n")
            text_file.write("N712\n")
            text_file.write("C1\n")
            text_file.write("L1\n")
            # text_file.write("P" + order['order_time'] + "\n")
            # text_file.write("D" + order['product_id'] + "\n")
            # text_file.write("D" + order['buysell'] + "\n")
            # text_file.write("$%.2f\n" % order['amount'])
            text_file.write("$" + order[0] + "\n")
            text_file.write("D" + order[1] + "\n")
            text_file.write("D" + order[2] + "\n")
            text_file.write("$%.2f\n" % order[4])
            text_file.write("$%.2f\n" % order[3])
            text_file.write("^\n")
