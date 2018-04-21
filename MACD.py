# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
def EMA(code,n): 
    data=pd.read_csv(code+'.csv', index_col='date',usecols=[0,2])
    data.index=pd.to_datetime(data.index)#转化为timestamp时间轴画图#
    data['ema']=data.close#新增ema列##ema和close同为data的列，所以不会改变元素#
    for i in range(1,len(data)):#[0]为初始ema#
        data.ema[i]=(n-1)/(n+1)*data.ema[i-1]+2/(n+1)*data.close[i]
    return data.ema

def MACD(code,n1,n2,m):#n2>n1#
    short=EMA(code,n1)
    long=EMA(code,n2)
    dif=short-long
    dea=dif.copy()#防止改变内在元素#
    for i in range(1,len(dea)):    
        dea[i]=(m-1)/(m+1)*dea[i-1]+2/(m+1)*dif[i]
    bar=(dif-dea)*2
    dif.name='dif'
    dea.name='dea'
    bar.name='bar'
    plt.plot(dif.index,dif,label='dif')
    plt.plot(dea.index,dea,label='dea')
    plt.bar(bar.index,bar,label='bar')
    plt.legend(loc='best') 
    return dif,dea,bar

def MACDCS(code,n1,n2,m,capital_0):
    data=pd.read_csv(code+'.csv',index_col='date',usecols=[0,2])
    dif,dea,bar=MACD(code,n1,n2,m)
    x=dif-dea
    a=0
    b=0
    shares=0
    capital=capital_0
    yiled=1
    day=[]#用于储存日期#
    y_t=[]#用于储存累计收益#
    for i in range(len(dea)):
        if x[i]>0 and x[i-1]<0:
            print(data.index[i]+'买入')
            buy=data.close[i]
            shares=capital/buy
        elif x[i]<0 and x[i-1]>0 and shares>0:
            print(data.index[i]+'卖出')
            day=np.append(day,data.index[i])#添加date#
            sell=data.close[i]
            capital=sell*shares
            a=a+1
            y=(sell-buy)/buy
            yiled=yiled*(1+y)#累计收益率#
            y_t=np.append(y_t,yiled)
            print('该次收益率'+'%.2f%%'%(y*100)+'\n累计收益率'+'%.2f%%'%((yiled-1)*100))
            if y>0:
                b=b+1
    print('\n操作次数'+str(a),'\n盈率次数'+str(b),'\n胜率'+'%.2f%%'%(b/a*100)+'\n累计收益率'+'%.2f%%'%((yiled-1)*100)+'\n期末资金'+str(capital))
    return day,y_t
        
    

        
