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
import time


def loadfromMysql(code, start_date, end_date=time.strftime('%Y-%m-%d',time.localtime(time.time())), paralist = ['Date','Close']):
    #连接MySQL数据库
    while True:    
        pw = input('Please enter the password: ')
        try:
            conn = mysql.connector.connect(host='localhost', port=3306, user='root', password = pw, database='quant')  
            cur = conn.cursor()
            break
        except:
            re_try = input('The password might be wrong, or the datebase is not available, do you want to retry (y/n)? ')
            if re_try == 'n' or re_try == 'no':
                break

    ## 注意： where 从句里面输入的因子数值必须要加上单引号 where Date > '%s'"， 否则该where从句没有作用！！
    sql = "select %s from stock_%s where Date > '%s' and Date < '%s'" % \
    (','.join(paralist), code, start_date, end_date)
    try:
        cur.execute(sql)
        res = cur.fetchall()
        dat = pd.DataFrame(res, columns = paralist)
        dat = dat.set_index('Date')
        conn.close()
        return dat
    except:
        print('Error: unable to fetch data. You might enter a wrong code')

def KDJ(dat, nday):
    dat['K'][nday-1] = dat['D'][nday-1] = 50
    periodhigh=dat['Close'].rolling(window = nday).max().astype('float')
    periodlow=dat['Close'].rolling(window = nday).min().astype('float')
    
    for i in range(nday,len(dat)):   #range（start， end， scan) 若只有一个数字则从0开始，第9日开始i8
        dat['RSV'][i]=100*(dat['Close'][i]-periodlow[i])/(periodhigh[i]-periodlow[i]) #某些股票刚上市会出现一字板涨停，high，low，close一样，rsv为0
        dat['K'][i]=(2/3)*dat['K'][i-1]+(1/3)*dat['RSV'][i]
        dat['D'][i]=(2/3)*dat['D'][i-1]+(1/3)*dat['K'][i]
        dat['J'][i]=3*dat['K'][i]-2*dat['D'][i]
    return dat
###KDJ交易策略：
#1、K or D在80以上为超卖区：K or D在20以下为超卖区
#2、J>100为超买区，J<0为超卖区
#3、k线由下而上穿过D线时，即为“黄金交叉” ——买入信号（股票价格上涨动量大）
   #k线由上而下穿过D线时，“死亡交叉”——卖出信号（下跌趋势）    11031103        
        
data=loadfromMysql('002500', start_date= '2015-01-01', end_date= '2018-01-01', paralist = ['Date','Open','Close','High','Low','Volume'])   

    #给函数赋一个变量名 

dat = pd.DataFrame(data['Close'],dtype=np.float)
dat['K'] = dat['J'] = dat['D']= dat['RSV'] = None
data = KDJ(dat, 8)
   


    
    
    
    
    
    
    
    
    
    
    
    
    