# CMO钱德动量摆动指标Chande Momentum Osciliator

## 理论
与其他动量指标摆动指标如相对强弱指标（RSI）和随机指标（KDJ）不同，钱德动量指标在计算公式的分子中采用上涨日和下跌日的数据。 

CMO指标是寻找极度超买和极度超卖的条件。
## 公式
CZ1:=IF(CLOSE-REF(CLOSE,1)>0,CLOSE-REF(CLOSE,1),0);

CZ2:=IF(CLOSE-REF(CLOSE,1)<0,ABS(CLOSE-REF(CLOSE,1)),0);

SU:=SUM(CZ1,N);      Su是今日收盘价与昨日收盘价（上涨日）差值加总。若当日下跌，则增加值为0

SD:=SUM(CZ2,N);      ；Sd是今日收盘价与做日收盘价（下跌日）差值的绝对值加总。若当日上涨，则增加值为0；

CMO:(SU-SD)/(SU+SD)*100;

MACMO:MA(CMO,M);

N为统计周期，M为CMO的M周期的移动平均。
## 指标用法
CMO作为一个通用规则，把超买水平定量在+50以上，把超卖水平定量在-50以下。

CMO的绝对值日越高，趋势越强。较低的CMO绝对值（0附近）标示标的证券在水平方向波动。在+50，上涨日的动量是下跌日动量的3倍；同样，在-50，下跌日的动量是上涨日动量的3倍。这些水平值可与RSI指标中的70/30相对应。

可以通过用CMO的移动平均线来建立进入和退出规则。可以利用CMO来衡量证券趋势强度的能力，来改进趋势跟踪机制。例如当CMO的绝对值较高时仅根据趋势跟踪指标来操作；当CMO的绝对值较低时转而采用交易范围指标。
## 指标代码

	import mysql.connector
	import time
	import pandas as pd
	import matplotlib.pyplot as plt
	import numpy as np
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
	aba = loadfromMysql(code = '603618', start_date ='2015-01-01', paralist = ['Date','Open','Close','High','Low','Volume'])
	def MACMO(data,n):
	    data.index=pd.to_datetime(data.index)
	    data = data.reset_index()  #重设index
	    aaa=data[['Date','Close']]
	    df=pd.DataFrame(aaa,columns = ["Date","Close","up","down","Su","Sd"])
	    CMO=pd.Series(0.0,index=data.Date)
	    for i in range(1,len(data)):
	        diff=data['Close'][i]-data['Close'][i-1]
	        if diff >= 0:
	            df['up'][i]=diff
	            df['down'][i]=0
	        else:
	            df['up'][i]=0
	            df['down'][i]=-diff
	        df['Su'][i]=np.sum(df['up'][:i+1])  #b=np.sum(df['Close'][:5])将01234行的加和
	        df['Sd'][i]=np.sum(df['down'][:i+1])                                                                                                                                                                                                                                                                                                                                                                                                                              
	        CMO[i]=100*(df['Su'][i]-df['Sd'][i])/(df['Su'][i]+df['Sd'][i])                     #CMO:(SU-SD)/(SU+SD)*100;
	    MACMO=pd.rolling_mean(CMO,n)   #计算简单CMO算术移动平均线MA  
	    return  MACMO
	MACMO=MACMO(aba,5)
	#画图
	plt.plot(MACMO,color='r')

## 回测