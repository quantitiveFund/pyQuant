# OBV交易策略（能量潮指标）

## 理论基础

市场价格的有效变动必须有成交量配合，量是价的先行指标。利用OBV可以验证当前股价走势的可靠性，并可以得到趋势可能反转的信号。比起单独使用成交量来，OBV看得更清楚。

## 公式


今日OBV=昨日OBV + sgn × 今天的成交量（成交股票手数）

sgn=+1 , 今日收盘价≥昨日收盘价    其成交量计入多方的能量

sgn=-1 , 今日收盘价<昨日收盘价    成交量计入空方的能量

计算OBV时的初始值可自行确定，一般用第一日的成交量代替。

### 多空比率净额

由于OBV的计算方法过于简单化，所以容易受到偶然因素的影响，为了提高OBV的准确性，可以采取多空比率净额法对其进行修正。

多空比率净额= [（收盘价－最低价）－（最高价-收盘价）] ÷（ 最高价－最低价）×V 
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
	def OBV(code, start_date,end_date=time.strftime('%Y-%m-%d',time.localtime(time.time())),paralist = ['Date','Close']): 
	    data = loadfromMysql(code = code, start_date = start_date, paralist = paralist)
	    data.index=pd.to_datetime(data.index)   #为画图横轴做准备
	    data = data.reset_index()  #重设index
	    aaa=data[["Date", "Open", "Close", "High","Low","Volume"]]
	    data=pd.DataFrame(aaa,columns = ["Date", "Open", "Close", "High","Low","Volume","VA"])  #建立新dataframe
	    data['VA'][0]=data['Volume'][0]#((data['Close'][0]-data['Low'][0])-(data['High'][0]-data['Close'][0]))/(data['High'][0]-data['Low'][0]+(np.e**(-10)))*data['Volume'][0]
	    OBV=pd.Series(0.0,index=data.Date)
	    OBV[0]=data['Volume'][0] 
	    for i in range(1,len(data)):        
	        data['VA'][i]=data['VA'][i-1]+((data['Close'][i]-data['Low'][i])-(data['High'][i]-data['Close'][i]))/(data['High'][i]-data['Low'][i]+(np.e**(-10)))*data['Volume'][i]   #np.e**(-10)表示e的负十次
		#去除OBV的偶然性    修正型多空比率净额OBV  多空比率净额= v+[（收盘价－最低价）－（最高价-收盘价）] ÷（ 最高价－最低价）×V  
	        diff=data['Close'][i]-data['Close'][i-1]
	        if diff>=0:
	            OBV[i]=OBV[i-1]+data['VA'][i]
	        else:
	            OBV[i]=OBV[i-1]-data['VA'][i]
	    return(OBV) 
	OBV=OBV('603618','2015-01-01','2018-01-01', paralist = ['Date','Open','Close','High','Low','Volume'])
	plt.plot(OBV,color="r",label='OBV')
##回测
