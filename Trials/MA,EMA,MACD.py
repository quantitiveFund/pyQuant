# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 21:01:54 2018

@author: FY
"""
#SMA 价格线与10日简单移动平均线
import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
def code(code):
    df=ts.get_hist_data(str(code))    #获取所有k线数据
    close=df['close']
    ma_10=df['ma10']
    money=1000000
    position=0
    for i in range(len(close)):
        if close.iloc[i] < ma_10.iloc[i]:    
            while money>0:
                buy=money/close.iloc[i]  #未考虑整百股买卖和是否能除尽问题
                position=buy
                money=0
        else:
            while money == 0:
                money=buy*close.iloc[i]
                position=0
    print(money)
code('000002')
code('002500')

#EMA   指数加权移动平均
import mysql.connector 
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
conn = mysql.connector.connect(host="10.23.0.2",port=3306,user="root", password="11031103",database="quant",charset="utf8")
cur = conn.cursor()
#data=a.loc[:,['Date','Close']]     #取两列
a = pd.read_sql("select * from stock_000002 where Date > '2016' and Date < '2018'", conn) 
#data=a.loc[:,['Date','Close']]     #取两列
data=a['Close']
data=pd.DataFrame(data,dtype=np.float)
def EWMA(day):
    c=2/(1+day)
    #EMA_1=np.mean(data.Close[0:day])    #计算第day天的平均 
    EMA_1=data.Close[0]
    #EMA_2=c*data.iloc[1]+(1-c)*EMA_1#计算day+1天以上的加权均值 以c的权重计算
    EMA=pd.Series(0.0,index=a['Date'])
    EMA[0]=EMA_1
    #EMA[1]=EMA_2
    for i in range(1,len(data)):
        expo=np.array(sorted(range(i+1),reverse=True)) #对range（i+1）倒序排列数组 range（2）为0，1
        w=0.8**expo        #不同的权重
        m=np.mat(w)
        EMA[i]=c*m*data[0:i+1].values+EMA_1*((1-c)**(i))  #矩阵相乘(.values将其改为数值直接用），得到EMA规律值，data[0,i+1] 为0到i
    plt.plot(EMA)
    return EMA

    
#MACD  异同移动平均线    统一第0用close，后续加权
EWMA(12)
EWMA(26)
DIF=EWMA(12)-EWMA(26)   #快速线DIF=EMA(12)-EMA(26)
#DEA   DEA=EMA(DIF,9)
data=pd.DataFrame(DIF.values,index=DIF.index,columns=['Close'])
DEA=EWMA(9)
MACD=DIF-DEA
plt.bar(left=MACD.index,height=MACD,label='MACD',color='r')





    
    
    
    
    
    
    
    


            


