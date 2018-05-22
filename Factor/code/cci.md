# CCI顺势指标

## 理论基础

专门测量股价、外汇或者贵金属交易是否已超出常态分布范围

属于超买超卖类指标中较特殊的一种。波动于正无穷大和负无穷大之间。但是，又不需要以0为中轴线，这一点也和波动于正无穷大和负无穷大的指标不同。

**CCI指标是根据统计学原理，引进价格与固定期间的股价平均区间的偏离程度的概念，强调股价平均绝对偏差在股市技术分析中的重要性**

它与其他超买超卖型指标又有自己比较独特之处。像KDJ、W%R等大多数超买超卖型指标都有“0-100”上下界限，因此，它们对待一般常态行情的研判比较适用，而对于那些短期内暴涨暴跌的股票的价格走势时，就可能会发生指标钝化的现象。而CCI指标却是波动于正无穷大到负无穷大之间，因此不会出现指标钝化现象，这样就有利于投资者更好地研判行情，特别是那些短期内暴涨暴跌的非常态行情。

## 公式
CCI（N日）=（TP－MA）÷MD÷0.015

其中，TP=（最高价+最低价+收盘价）÷3

MA=近N日收盘价的累计之和÷N

MD=近N日（MA－收盘价）的累计之和÷N

0.015为计算系数，N为计算周期

## 代码
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

## 超买超卖
1、当CCI曲线向上突破﹢100线而进入非常态区间时，表明股价开始进入强势状态，投资者应及时买入股票。

2、当CCI曲线向上突破﹢100线而进入非常态区间后，只要CCI曲线一直朝上运行，就表明股价强势依旧，投资者可一路持股待涨。

3、当CCI曲线在﹢100线以上的非常态区间,在远离﹢100线的地方开始掉头向下时，表明股价的强势状态将难以维持，是股价比较强的转势信号。如果前期的短期涨幅过高时，更可确认。此时，投资者应及时逢高卖出股票。

4、当CCI曲线在﹢100线以上的非常态区间，在远离﹢100线的地方处一路下跌时，表明股价的强势状态已经结束，投资者还应以逢高卖出股票为主。

5、当CCI曲线向下突破﹣100线而进入另一个非常态区间时，表明股价的弱势状态已经形成，投资者应以持币观望为主。

6、当CCI曲线向下突破﹣100线而进入另一个非常态区间后，只要CCI曲线一路朝下运行，就表明股价弱势依旧，投资者可一路观望。

7、当CCI曲线向下突破﹣100线而进入另一个非常态区间，如果CCI曲线在超卖区运行了相当长的一段时间后开始掉头向上，表明股价的短期底部初步找到，投资者可少量建仓。CCI曲线在超卖区运行的时间越长，越可以确认短期的底部。

8、当CCI指标在﹢100线——﹣100线的常态区间运行时，投资者则可以用KDJ、威廉等其他超买超卖指标进行研判。

## 回测