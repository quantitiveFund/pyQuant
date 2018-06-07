# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 19:52:46 2018

@author: Pikari
"""

'''
alpha回测测试，回测流程：确定股票池->确定回测日期->计算alpha->导入股票池数据->
建立账户->依据alpha选定股票->买入卖出股票->更新账户资产->生成收益率曲线
'''

import Event
import NewNeoAlpha
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
conn = create_engine('mysql+mysqldb://root:password@localhost:3306/database?charset=utf8')    

'----确定股票池----'
tables = pd.read_sql('show tables', conn)
stock_pool = ['stock_000004', 'stock_000005', 'stock_000006', 'stock_000007', 'stock_000008', 'stock_000009', 'stock_000010', 'stock_000011', 'stock_000012', 'stock_000014', 'stock_000016', 'stock_000017', 'stock_000018', 'stock_000019', 'stock_000020', 'stock_000021', 'stock_000022', 'stock_000023', 'stock_000025', 'stock_000026', 'stock_000027', 'stock_000028', 'stock_000029', 'stock_000030', 'stock_000031', 'stock_000032', 'stock_000033', 'stock_000034', 'stock_000035', 'stock_000036', 'stock_000037', 'stock_000038', 'stock_000039', 'stock_000040', 'stock_000042', 'stock_000043', 'stock_000045', 'stock_000046', 'stock_000048', 'stock_000049', 'stock_000050', 'stock_000055', 'stock_000056', 'stock_000058', 'stock_000059']
symbol_list = stock_pool

'----确定回测日期----'
start_date = '2016-01-01'
end_date = '2017-01-01'

'----计算alpha----'
open = NewNeoAlpha.get_panel_data(stock_pool, 'Open', start_date, end_date)
high = NewNeoAlpha.get_panel_data(stock_pool, 'High', start_date, end_date)
low = NewNeoAlpha.get_panel_data(stock_pool, 'Low', start_date, end_date)
close = NewNeoAlpha.get_panel_data(stock_pool, 'Close', start_date, end_date)
returns = NewNeoAlpha.get_panel_data(stock_pool, 'ChgRate', start_date, end_date)
volume = NewNeoAlpha.get_panel_data(stock_pool, 'Volume', start_date, end_date)
vwap = (open + high + low + close) / 4
alpha = NewNeoAlpha.Alpha(open, high, low, close, returns, volume, vwap)
alpha_101 = alpha.alpha_101()

'----导入股票池数据----'
data = Event.DatabaseHandler(Event.Event(), start_date, end_date, symbol_list)

'----建立账户----'
port = Event.NaviePortfolio(data, Event.Event(), start_date)
hold = [] #持仓股票

'----回测----'
i = 0
port.bars.update_data() #必须更新一次股票数据，不更新会导致未来数据的使用
while port.bars.contiune == True: #update_data()方法迭代完成后，continue=False
    port.bars.update_data() #交易前更新数据，决定下一交易日的买卖
    
    if i % 20 == 0: #20天调仓一次
        
        '----依据alpha选定股票----'
        stock_rank = list(alpha_101.iloc[i, ].replace([-np.inf, np.inf], 0).rank().sort_values().dropna().index[-10:-1])
        #alpha排序，去除alpha值为nan的股票，买入排名前n只的股票
        buy_list = list(set(stock_rank).difference(set(hold))) #买入未持仓股票
        sell_list = list(set(hold).difference(set(stock_rank))) #卖出已持仓股票
        keep_list = list(set(hold).intersection(stock_rank)) #不调仓股票
        
        '----买入卖出股票----'
        if hold is not []:
            for stock in sell_list:
                fill = Event.FillEvent(datetime.datetime.utcnow(), stock, data.symbol_lastest_data[stock][0][2] * 1000, 1000, 'SELL', 5)
                port.update_fill(fill)
                hold.remove(stock)
        
        if buy_list is not []:
            for stock in buy_list:
                fill = Event.FillEvent(datetime.datetime.utcnow(), stock, data.symbol_lastest_data[stock][0][2] * 1000, 1000, 'BUY', 5)
                port.update_fill(fill)
                hold.append(stock)
    
    '----更新账户资产----'
    port.update_timeindex(Event.Event()) #
    i += 1

'----生成收益率曲线----'
value = []
for i in range(len(alpha_101)):
    for symbol in symbol_list:
        day_value = port.all_holdings[i]['total'] - port.all_holdings[i]['commission']
    value.append(day_value)
        
value = pd.Series(value)
index_shanghai = pd.read_sql('select close from index_000001 where date between "%s" and "%s"' % (start_date, end_date), conn).close

returns_alpha = value / value[0] - 1
returns_basic = index_shanghai / index_shanghai[0] - 1
plt.plot(pd.to_datetime(port.bars.symbol_data[symbol].index), returns_alpha)
plt.plot(pd.to_datetime(port.bars.symbol_data[symbol].index), returns_basic)
