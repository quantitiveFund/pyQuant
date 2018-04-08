# -*- coding: utf-8 -*-
"""
Created on Sun Apr  1 19:29:12 2018

@author: Pikari
"""

from WindPy import w
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
w.start()

code_list = w.wset("SectorConstituent","sectorId=a001010100000000;field=wind_code").Data[0]

#获取股票收盘价
def get_stock_price(code, start, end):
    stock_price = w.wsd(code, 'close', start, end)
    time_series = pd.DataFrame(stock_price.Data, index=stock_price.Fields, columns=stock_price.Times).T.CLOSE
    return time_series

#获取平稳股票
def get_stable_stock(code, start, end, lag, pvalue):
    time_series = get_stock_price(code, start, end)
    result = sm.tsa.stattools.adfuller(time_series.diff(lag).dropna())
    if result[1] < pvalue:
        return code

#获取协整股票
def get_coint_stock(code1, code2, start, end, pvalue):
    time_series1 = get_stock_price(code1, start, end)
    time_series2 = get_stock_price(code2, start, end)
    result = sm.tsa.stattools.coint(time_series1, time_series2)
    if result[1] < pvalue:
        return [code1, code2]

#获取协整残差
def get_resid(code1, code2, start, end):
    time_series1 = get_stock_price(code1, start, end)
    time_series2 = get_stock_price(code2, start, end)
    resid = sm.OLS(time_series1, sm.add_constant(list(time_series2))).fit().resid
    return resid

#回测，还不完整
def test(stock_portfolios, money, start, end, buy_pvalue, sell_pvalue):
    position = 0
    stock1_price = get_stock_price(stock_portfolios[0], start, end)
    stock_resid = get_resid(stock_portfolios[0], stock_portfolios[1], start, end)
    #stock2_price = get_stock_price(stock_portfolios[1], start, end)
    mean = np.mean(stock_resid)
    var = np.var(stock_resid)
    
    for i in range(len(stock_resid)):
        res = abs(stock_resid[i])
        
        if res > abs(norm.ppf(buy_pvalue, mean, var)):
            while money > 0:
                position = money / stock1_price[i]
                money = 0
                
        elif res < abs(norm.ppf(buy_pvalue, mean, var)):
            while position > 0:
                money = position * stock1_price[i]
                position = 0
                
    return [stock_portfolios, money, position, stock1_price[-1]]

stable_stock_list = []
coint_stock_list = []
final_result = []
start = '2016-01-01'
end = '2017-01-01'
lag = 1
pvalue = 0.05
money = 1000000
buy_pvalue = 0.05
sell_pvalue = 0.5

for code in code_list:
    temp_stock = get_stable_stock(code, start, end, lag, pvalue)
    if temp_stock != None:
        stable_stock_list.append(temp_stock)
    
for code1 in stable_stock_list:
    for code2 in stable_stock_list:
        temp_stock_portfolios = get_coint_stock(code1, code2, start, end, pvalue)
        if temp_stock_portfolios != None:
            coint_stock_list.append(temp_stock_portfolios)
            
for code_portfolios in coint_stock_list:
    final_result.append(test(code_portfolios, money, start, end, buy_pvalue, sell_pvalue))

print(final_result)
