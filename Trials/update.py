# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 12:14:40 2018

@author: 余智伦
"""
import pandas as pd
import tushare as ts
from datetime import *
df=ts.get_stock_basics()
now=datetime.now().strftime('%Y-%m-%d')#'2018-03-29'字符串#
for i in range(len(df)):
    code=df.index[i]
    data=pd.read_csv(code+'.csv')
    date=data.ix[len(data)-1].date#'2018/3/27'字符串#
    strdate=pd.to_datetime(date).strftime('%Y-%m-%d')#'2018-03-27'字符串#
    if strdate!=now:
        print('需要更新数据')
        date_new=str(pd.to_datetime(date))#上次数据末尾(时间戳：不包含当天)#
        temp=ts.get_k_data(code,start=date_new)
        data_new=pd.concat([data,temp])
        data_new.to_csv(code+'.csv',index=False)
    else:
        print('不需要更新')
    
    
    
