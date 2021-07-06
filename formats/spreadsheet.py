import os
import datetime
import pyexcel as p
from pyexcel._compact import OrderedDict

def make_spreadsheet(full_orders, buys_sorted, sells_sorted, output_dir='output', year=2017):
  out_file = os.path.join(output_dir, '_'.join(['Transactions', 'Crypto', str(year)])) + '.ods'
  book = OrderedDict()

  # "Transactions" sheet
  trans_sheet = []
  book['Transactions'] = trans_sheet
  trans_sheet.append([ 'Order Time UTC', 'product', 'currency', 'currency_pair', 'buysell', 'cost', 'amount', 'cost_per_coin' ])
# 'order_time', 'product', 'currency', 'currency_pair', 'buysell', 'cost', 'amount', 'cost_per_coin'
  buys_sells_sorted = sorted(buys_sorted+sells_sorted, key=lambda order: order['order_time'])
  for order in buys_sells_sorted:
    trans_sheet.append([
      order['order_time'].isoformat(),
      order['product'],
      order['currency'],
      order['currency_pair'],
      order['buysell'],
      order['cost'],
      order['amount'],
      order['cost_per_coin']
    ])
    
  # "8949" sheet
  form_8949_sheet = []
  book['8949'] = form_8949_sheet
  form_8949_sheet.append([ 'Description', 'Date bought', 'Date sold', 'Proceeds', 'Cost basis', 'Gain/Loss' ])

  # Full order is [description, date acquired, date sold, proceeds, cost basis, gain/loss] (populated in fill_8949.py)
  DESC, DATE_ACQ, DATE_SOLD, PROCEEDS, COST_BASIS, GAIN_LOSS = range(5+1)
  form_8949_sales_by_month = { month_num: { 'first_idx': -1, 'last_idx': -1, 'proceeds': 0, 'gain_loss': 0 } for month_num in range(1,12+1) }
  total_8949_proceeds  = 0
  total_8949_gain_loss = 0

  for idx, full_order in enumerate(full_orders):
    form_8949_sheet.append(full_order)
    # caclulate start/end indices of sales by month
    sale_dt = datetime.datetime.strptime(full_order[DATE_SOLD], '%m/%d/%Y')
    month_sales = form_8949_sales_by_month[sale_dt.month]
    if month_sales['first_idx'] == -1:
      month_sales['first_idx'] = idx
      
    month_sales['last_idx']     = idx
    month_sales['proceeds']     += full_order[PROCEEDS]
    total_8949_proceeds         += full_order[PROCEEDS]
    month_sales['gain_loss']    += full_order[GAIN_LOSS]
    total_8949_gain_loss        += full_order[GAIN_LOSS]

  # "Calculated" sheet
  calc_sheet = []
  book['Calculated'] = calc_sheet
  calc_sheet.append([ 'Total 8949 gain/loss:', "=SUM($'8949'.F2:F%d)" % (len(form_8949_sheet)), total_8949_gain_loss ])
  calc_sheet.append([ 'Total 8949 proceeds:', "=SUM($'8949'.D2:D%d)" % (len(form_8949_sheet)), total_8949_proceeds ])
  for month_num in range(1, 12+1):
    month_sales     = form_8949_sales_by_month[month_num]
    month_first_idx = month_sales['first_idx']
    month_last_idx  = month_sales['last_idx']
    if month_first_idx != -1:
      calc_sheet.append([ 'Total 8949 proceeds in month #%d:' % (month_num), "=SUM($'8949'.D%d:D%d)" % (month_first_idx+2, month_last_idx+2), month_sales['proceeds'] ])
  # calc_sheet.append([ 'Total trans amounts:', "=SUM($'Transactions'.F2:F%d)" % (len(buys_sells_sorted)) ])

  p.save_book_as(bookdict=book, dest_file_name=out_file)
  print("Saved spreadsheet as %s" %(out_file) )

