# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 21:51:49 2018

@author: 余智伦
"""
import matplotlib.pyplot as plt
import pandas as pd
import mysql.connector as mc
import numpy as np
def loadfrommysql(code):
    con=mc.connect(host='10.23.0.2',port=3306,user='root',password='11031103',database='quant',charset='utf8') #该数据库是手动建立的，请填上相应的密码
    data=pd.read_sql('select * from stock_'+code,con,index_col=['Date'])
    data=pd.DataFrame(data,dtype=float)#数值由str转化为float#
    data.index=pd.to_datetime(data.index)#转化为timestamp画图#
    con.close()
    return data

'''
确定的时间段（“ N “）
在此期间出现最高价后的天数（“ HH “）； 使用公式 [（N - HH）/ N]×100% ] 计算得到阿隆Up；
[例：若取时间段为25天，如果今天为最高价（HH = 0），则阿隆Up =（25-0）/ 25×100%= 100%；
如果10天前为最高价（HH = 10），则阿隆Up =（25-10）/ 25×100%= 60% ]
在此期间出现最低价后的天数（“ LL “）； 使用公式 [（N - LL）/ N]×100% ] 计算得到阿隆Down;
利用阿隆向上和阿隆向下，利用公式 [ 阿隆Up - 阿隆Down ] 计算得到Aroon Osc'''

def aroon(code,n=25):
    data=loadfrommysql(code)
    data['up']=np.nan#初始化赋值nan#
    data['down']=np.nan
    for i in range(n,len(data)):#每个区间需要n+1个数#
        today=data.index[i]#该区间的当日#
        high_day=data.Close[i-n:i+1].idxmax()#区间内最高价的索引日期#
        low_day=data.Close[i-n:i+1].idxmin()
        HH=data.Close[high_day:today].count()-1#间隔periods#
        LL=data.Close[low_day:today].count()-1
        data.up[i]=(n-HH)/n*100
        data.down[i]=(n-LL)/n*100
    aroon_osc=data.up-data.down
    plt.plot(data.up,color='r',label='up')
    plt.plot(data.down,color='g',label='down')
    plt.plot(aroon_osc,color='b',label='osc')
    plt.title('Aroon')
    plt.legend(loc='best')
    return data.up,data.down,aroon_osc
        
