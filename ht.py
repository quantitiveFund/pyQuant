# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False#前两句实现显示中文#
def HTZD(code):
    data=pd.read_csv(code+'.csv',index_col='date')
    data.index=pd.to_datetime(data.index)
    y=(data.close-data.close.shift(1))/data.close.shift(1)
    y1=y[y>=0]
    y2=y[y<0]
    plt.bar(y1.index,y1,color='r')#上涨为红柱#
    plt.bar(y2.index,y2,color='g')#下跌为绿柱#
    plt.title(code+'每日涨跌幅')

def HTLJ(code):
    data=pd.read_csv(code+'.csv',index_col='date')
    data.index=pd.to_datetime(data.index)
    y=(data.close-data.close.shift(1))/data.close.shift(1)
    yiled=y.copy()#不改变y#
    yiled[1]=1+y[1]
    for i in range(2,len(y)):
        yiled[i]=yiled[i-1]*(1+y[i])
    yiled=yiled-1
    plt.plot(yiled)
    plt.title(code+'累计收益率')
