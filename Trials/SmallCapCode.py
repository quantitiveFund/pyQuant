# -*- coding: utf-8 -*-
"""
Created on Sun Apr  8 19:18:07 2018

@author: FY
"""

import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt  
df = ts.get_stock_basics()
#date.today()-timedelta(days=2
## 将月末停牌股票去除
# 万科在2015年12月18日停牌，2016年7月4日复牌。在12月31日那一天是不能买入这个股票的。
# 即最后一天不交易的股票，不能买入。
#去掉涨停无法买入
none_harden = []
code_all=df.index
try:
    for code in code_all:
        data = ts.get_k_data(code).close[-2:]
        if data.iloc[-1] / data.iloc[-2] <= 1.099:
            none_harden.append(code)
            #print(none_harden)          
except:
    print(code)
a=[]       
b=[]
for i in range(len(code_all)):
    today= ts.get_realtime_quotes(str(code_all[i]))
    price=today['price'][0]
    total=df['totals'][i]
    market_value=float(price)*total
    a.append(code_all[i])
    b.append(market_value)
data_2=pd.DataFrame(b,a,columns=['market_value'])
maktp=data_2.sort_values(by='market_value')     #排序市值
data_3 = [] 
for i in range(len(data_2)):
    if maktp.market_value[i] > 0:
        data_3.append(maktp.index[i])  
        #data_2.drop(i)      #删除某行
        #del data_2[i]
buy=data_3[0:10]     #买入市值最低的10只股票
money = 1000000
for a in buy:
    k_data=ts.get_k_data(a)
    account=money/k_data.close[0]
    money=account*k_data.close[120]
    account=0
    print(money)
    y = k_data.close / k_data.close.shift(1)
    plt.plot(y[:120])
    money=1000000
