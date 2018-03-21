# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 20:04:28 2018

@author: fy(step1)
"""
###import tushare as ts
###import pandas as pd
###df=ts.get_hist_data('002522',start='2017-01-01',end='2018-03-20')
###data=df[['open','close','high','volume']]  #获取前几列数据



import tushare as ts
import pandas as pd
df=ts.get_stock_basics()
#data_1=df.index                #第一列为index
for i in range(len(df)):        #range为整数列表  用于for遍历
    code=df.index[i]
    date=df['timeToMarket'][i]      #a['列索引'][数字]第几列的几行
    data=ts.get_k_data(code,start=str(date))   #用str将数值转化为字符串(全要用字符串)#get_k_data为新增的接口，可读取所有数据不断
    filename=str(code)+'.csv'
    data.to_csv(filename)
