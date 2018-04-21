# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 13:43:30 2018

@author: CS
"""

import pandas as pd
from WindPy import w
from sqlalchemy import create_engine
import time
import os
import pymysql
pymysql.install_as_MySQLdb()

class WindStock():
    
    def getCurrentTime(self):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    
    def AllStockHistoryData(self,symbols,start_date,end_date,step=0):
        print(self.getCurrentTime(),": start to download stock data:")
        for symbol in symbols:
            w.start()
            try:
                stock = w.wsd(symbol,"trade_code,open_price,high_price,\
                              low_price,close_price,volumn,\
                              pre_close",start_date,end_date)
                index_data = pd.DataFrame()
                index_data['trade_code'] = stock.Times
                stock.Data[0] = symbol
                index_data['stock_code'] = stock.Data[0]
                index_data['open_price'] = stock.Data[1]
                index_data['high_price'] = stock.Data[2]
                index_data['low_price'] = stock.Data[3]
                index_data['close_price'] = stock.Data[4]
                index_data['volumn'] = stock.Data[5]
                index_data['pre_close'] = stock.Data[6]
                index_data['data_source'] = 'Wind'
                index_data['created_date'] = time.strftime('%Y-%m-%d %H:%M:%S'\
                          ,time.localtime(time.time()))
                index_data['updated_date'] = time.strftime('%Y-%m-%d %H:%M:%S'\
                          ,time.localtime(time.time()))
                index_data = index_data[index_data['open_price' > 0]]
                try:
                    index_data.to_sql('stock_daily_data',\
                                      engine,if_exists='append')
                except Exception as e:
                    error_log = pd.DataFrame()
                    error_log['trade_date'] = stock.Times
                    error_log['stock_code'] = stock.Data[0]
                    error_log['strat_date'] = start_date
                    error_log['end_date'] = end_date
                    error_log['status'] = None
                    error_log['table'] = 'stock_daily_data'
                    error_log['args'] = 'Symbol' + symbol + 'From'\
                    + start_date + 'To' + end_date
                    error_log['error_info'] = e
                    error_log['created_date'] = time.strftime(\
                             '%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                    error_log.to_sql('stock_error_log',\
                                     engine,if_exists='append')
                    print(self.getCurrentTime(),":SQL Exception: %s" %(e))
                    continue
                w.start()
            except Exception as e:
                error_log = pd.DataFrame()
                error_log['trade_date'] = stock.Times
                error_log['stock_code'] = stock.Data[0]
                error_log['strat_date'] = start_date
                error_log['end_date'] = end_date
                error_log['status'] = None
                error_log['table'] = 'stock_daily_data'
                error_log['args'] = 'Symbol' + symbol + 'From'\
                + start_date + 'To' + end_date
                error_log['error_info'] = e
                error_log['created_date'] = time.strftime(\
                             '%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                error_log.to_sql('stock_error_log',\
                                 engine,if_exists='append')
                print (self.getCurrentTime(),":index_data %s : Exception :%s" \
                       % (symbol,e) )
                time.sleep(sleep_time)
                w.start()
                continue
            print(self.getCurrentTime(),": Downloading [",symbol,"] From "\
                  +start_date+" to "+end_date)
        print(self.getCurrentTime(),": Symbols have been downloaded.")
        
        
    def getAllStockCodesFromCsv(self):
        file_path=os.path.join(os.getcwd(),'Symbols.csv')
        stock_code = pd.read_csv(filepath_or_buffer=file_path,encoding='utf-8')
        Code=stock_code.code
        return Code
    
    
    def getAllStockCodesFromWind(self,end_date=\
                           time.strftime('%Y%m%d',\
                                         time.localtime(time.time()))):
        w.start()
        stockCodes=w.wset("sectorconstituent","date="+end_date+\
                          ";sectorid=a001010100000000;field=wind_code")
        return stockCodes.Data[0]
    
    
def main():
    global engine,sleep_time,symbols
    sleep_time=5
    windStock=WindStock()
    engine = create_engine('mysql://root:lemonseth5571.@127.0.0.1/winf?charset=utf-8')
    start_date='ipo'
    end_date='20180324'
    symbols=windStock.getAllStockCodesFromWind(end_date)
    windStock.AllStockHistoryData(symbols,start_date,end_date)
    
if __name__ == "__main__":
    main()
    
             
