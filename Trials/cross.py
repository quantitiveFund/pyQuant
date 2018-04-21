# -*- coding: utf-8 -*-
"""
Spyder Editor author: YZL

This is a temporary script file.
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def MA(code,n):#股票代码和天数#
    data=pd.read_csv(code+'.csv')
    price=data.close
    x=price
    for i in range(1,n):#0为原始数据#
       x=x+price.shift(i)#依次挤出最前一天#
    x=x/n
    return x

def xx(code,n1,n2):#n2>n1#
    a=0#操作次数#
    b=0#盈利次数#
    c=0#确保先买入才能卖出#
    yiled=0#累计收益率#
    x1=MA(code,n1)
    x2=MA(code,n2)
    x=x1-x2#MA(n1)与MA(n2)差值#
    for i in range((n2-1),len(data)):#n2时才有两根均线#
        if x[i]>0 and x[i-1]<0 :#金叉买入#
            print('在'+data.ix[i].date+'买入')
            buy=price[i]
            c=1#可以卖出股票#
        elif x[i]<0 and x[i-1]>0 and c==1:#死叉卖出#
            print('在'+data.ix[i].date+'卖出')
            sell=price[i]
            a=a+1#一轮完成#
            y=(buy-sell)/buy#单次收益#
            yiled=yiled+y
            print('当次收益='+'%.2f%%'%(y*100)+'\n累计收益率='+'%.2f%%'%(yiled*100))
            if y>0:
                b=b+1#盈利次数#
    print('操作次数='+str(a)+'\n盈利次数='+str(b)+'\n胜率='+'%.2f%%'%(b/a*100))
        
        

       
