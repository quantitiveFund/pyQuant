# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 21:38:07 2018

@author: FY
"""

#KDJ指标
#求未成熟随机指标RSV
import mysql.connector 
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
def loadfrommysql(code):
    conn = mysql.connector.connect(host="*",port=3306,user="root", password="***",database="quant",charset="utf8")
    cur = conn.cursor()
    #data = pd.read_sql("select * from stock_%s where Date > '%s' and Date < '%s'", conn) 
    data=pd.read_sql('select * from stock_'+code,conn,index_col=['Date'])
    return data
data=loadfrommysql('002500')       #给函数赋一个变量名 
data.index=pd.to_datetime(data.index)   #时间列是年月日加时间则不需要变，若只有年月日则为了画图要变
close=data['Close']
close=pd.DataFrame(close,dtype=np.float)
RSV=pd.Series(0.0,index=data.index)#[8:len(close)])
K=pd.Series(0.0,index=data.index)#[8:len(close)])
D=pd.Series(0.0,index=data.index)
J=pd.Series(0.0,index=data.index)
K[7]=50
D[7]=50
def KDJ(day):
    for i in range(day,len(close)):   #range（start， end， scan) 若只有一个数字则从0开始，第9日开始i8
        periodhigh=float(data.High[i-8:i+1].max())
        periodlow=float(data.Low[i-8:i+1].min())
        RSV[i]=100*(close.iloc[i]-periodlow)/(periodhigh-periodlow) #某些股票刚上市会出现一字板涨停，high，low，close一样，rsv为0
        K[i]=(2/3)*K[i-1]+(1/3)*RSV[i]
        D[i]=(2/3)*D[i-1]+(1/3)*K[i]
        J[i]=3*K[i]-2*D[i]
    plt.plot(RSV)        
    plt.plot(K)
    plt.plot(D)
    plt.plot(J)
KDJ(8)
###KDJ交易策略：
#1、K or D在80以上为超卖区：K or D在20以下为超卖区
#2、J>100为超买区，J<0为超卖区
#3、k线由下而上穿过D线时，即为“黄金交叉” ——买入信号（股票价格上涨动量大）
   #k线由上而下穿过D线时，“死亡交叉”——卖出信号（下跌趋势）       


    
    
    
    
    
    
    
    
    
    
    
    
    