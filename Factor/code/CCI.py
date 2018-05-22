# -*- coding: utf-8 -*-
"""
Created on Mon May 21 19:02:34 2018

@author: FY
"""
import mysql.connector
import time
import pandas as pd
import matplotlib.pyplot as plt
def loadfromMysql(code, start_date, end_date=time.strftime('%Y-%m-%d',time.localtime(time.time())), paralist = ['Date','Close']):  #time中localtime为格式化时间戳为本地的时间，time()函数可以获取当前的时间，strftime('%Y-%m-%d',为转化为年-月-日
    #连接MySQL数据库
    while True: 
        hostname = '10.23.0.2'
        pw = input('Please enter the password: ')
        try:
            conn = mysql.connector.connect(host = hostname, port=3306, user='root', password = pw, database='quant')  
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
        cur.execute(sql)   #建表
        res = cur.fetchall()
        dat = pd.DataFrame(res, columns = paralist)
        dat = dat.set_index('Date')
        conn.close()
        return dat
    except:
        print('Error: unable to fetch data. You might enter a wrong code')
aba = loadfromMysql(code = '603618', start_date ='2015-01-01', paralist = ['Date','Open','Close','High','Low'])        
def CCI(data,n):
    data.index=pd.to_datetime(data.index)
    data = data.reset_index() 
    df=pd.DataFrame(data,columns=['Date','Open','Close','High','Low',"TP",'MA','MA_CLOSE','MD'])
    CCI=pd.Series(0.0,index=data.Date)
    for i in range(len(df)):
        df['TP'][i]=(df['High'][i]+df['Low'][i]+df['Close'][i])/3          #TP=（最高价+最低价+收盘价）÷3
        df['MA']=pd.rolling_mean(df['Close'],n)     #MA=近N日收盘价的累计之和÷N    
        df['MA_CLOSE'][i]=df['MA'][i]-df['Close'][i]                                        #MD=近N日（MA－收盘价）的累计之和÷N    
        df['MD']=pd.rolling_mean(df['MA_CLOSE'],n)
    #CCI（N日）=（TP－MA）÷MD÷0.015    
        CCI[i]=(df['TP'][i]-df['MA'][i])/df['MD'][i]/0.15
    return (CCI)
CCI=CCI(aba,4)
plt.plot(CCI,color="r")        
#超买超卖
#当CCI曲线向上突破﹢100线而进入非常态区间时，表明股价开始进入强势状态，投资者应及时买入股票    
#当CCI曲线向上突破﹢100线而进入非常态区间后，只要CCI曲线一直朝上运行，就表明股价强势依旧，投资者可一路持股待涨。
     
        
        
        
        
        
        
        
        
        
        
        
        