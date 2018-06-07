# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 18:26:56 2018

@author: Pikari
"""

import pandas as pd
from sqlalchemy import create_engine
conn = create_engine('mysql+mysqldb://root:password@localhost:3306/database?charset=utf8')    

def get_trade_date(stock):
    start_date = pd.read_sql('select min(Date) from %s' % (stock), conn).iat[0, 0]
    end_date = pd.read_sql('select max(Date) from %s' % (stock), conn).iat[0, 0]
    trade_date = pd.read_sql('select date from index_000001 where date between "%s" and "%s"' % (start_date, end_date), conn, index_col='date')
    return trade_date

def get_stock_data(stock):
    stock_data = pd.read_sql('select * from %s' % (stock), conn, index_col='Date')
    trade_date = get_trade_date(stock)
    return pd.concat([trade_date, stock_data], axis=1)

def complete_stock_data(stock):
    data = get_stock_data(stock)
    data.Close.fillna(method='pad', inplace=True)
    data.fillna({'ChgAmount' : 0, 
              'ChgRate' : 0, 
              'Volume' : 0, 
              'VolTrans' : 0, 
              'Swing' : 0, 
              'Turnover' : 0}, inplace=True)
    data.fillna(method='backfill', axis=1, inplace=True)
    return data

if __name__ == '__main__':
    tables = pd.read_sql('show tables', conn)
    stock_list = list(tables.iloc[200:1000, 0])
    
    for stock in stock_list:
        stock_data = complete_stock_data(stock)
        stock_data.reset_index(inplace=True)
        stock_data.rename(columns={'index' : 'Date'}, inplace=True)
        stock_data.to_sql(stock, conn, if_exists='replace', index=False)
