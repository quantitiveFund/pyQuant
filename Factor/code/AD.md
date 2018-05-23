
# 量价指标

**量价指标是指证券市场技术分析中分析成交量与成交价格关系的一大类指标。**

## Accumulation/Distribution (AD)集散指标 收集派发线

### 理论基础
A/D也叫集散量指标,是根据股票的最高价和最低价来算的. 

累积/派发线（Accumulation/Distribution Line）指标由Marc·Chaikin提出，是一种非常流行的平横交易量指标。

其原理与OBV类似，但是只以当日的收盘价位来估算成交流量，用于估定一段时间内该证券累积的资金流量。

### 公式  
A/D line＝昨天的A/D值+( 收盘价位置常数*成交量）  
收盘价位置常数=((收盘价－最低价)－(最高价－收盘价))/(最高价－收盘价)

### 代码
	
	import mysql.connector
	import time
	import pandas as pd
	import numpy as np
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
	aba= loadfromMysql(code = '603618', start_date ='2015-01-01', paralist = ['Date','Open','Close','High','Low','Volume'])        
	def AD(data):
	    data.index=pd.to_datetime(data.index)    #转化为时间
	    data=data.reset_index()        #重设index
	    data=pd.DataFrame(data,columns=['Date','Open','Close','High','Low','Volume','constant'])
	    AD=pd.Series(0.0,index=data.Date)
	    for i in range(1,len(data)):
	        data['constant'][0]=(2*data['Close'][0]-data['Low'][0]-data['High'][0])/(data['High'][0]-data['Close'][0]+np.e**(-10))
	        data['constant'][i]=(2*data['Close'][i]-data['Low'][i]-data['High'][i])/(data['High'][i]-data['Close'][i]+np.e**(-10))    #防止分母为0
	        #是否需要避免high=close但是close！=low的情况
	        AD[0]=0
	        AD[i]=AD[i-1]+(data['constant'][i]*data['Volume'][i])
	    return AD
	AD=AD(aba)
	plt.plot(AD,color='r')


### 买卖信号
1. ADV测量资金流向，向上的ADV表明买方占优势，而向下的ADV表明卖方占优势；  
2. ADV与价格的背离可视为买卖信号，即底背离考虑买入，顶背离考虑卖出；
3. 应当注意ADV忽略了缺口的影响，事实上，跳空缺口的意义是不能轻易忽略的。  
ADV指标无需设置参数。但在应用时，可结合指标的均线进行分析。

### 回测









 
