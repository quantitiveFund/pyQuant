# -*- coding: utf-8 -*-
"""
Created on Thu May  3 10:33:32 2018

@author: FY
"""

###RSI相对强弱指标
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
data=pd.read_csv("002510.csv")
aaa=data[['date','close']]    #取两列数据
df=pd.DataFrame(aaa,columns = ["date", "close", "up", "down"]) #创建一个带两列数据的dataframe  )
data.index=pd.to_datetime(data.date)
for i in range(1,len(aaa)):                 #获得收盘价每日涨跌值
    diff=aaa['close'][i]-aaa['close'][i-1]
    if diff>=0:
        df['up'][i]=diff     #在dataframe指定位置中插入值
    else:
        df['down'][i]=diff*(-1)
#计算n日的rsi
RSI=pd.Series(0.0,index=data.index)
for j in range(6,len(aaa)):            #获得涨跌幅度简单移动平均
    smup=np.mean(df['up'][(j-6):j])#用简单平均来计算
    smdown=np.mean(df['down'][(j-6):j])
    RSI[j]=100*smup/(smup+smdown)
plt.plot(RSI,color='r',label='RSI')
