#101 alpha python
##Stand-by Phase
###get\_trade\_date(date, lag)

函数说明

* 获取交易日，交易日基准为上证指数，返回值为交易日列表

代码实现

	def get_trade_date(date, lag):
	    data = pd.read_sql('select * from stock_000001', conn)
	    target_date = data[data.index[data.Date.isin([date])][0] - lag:data.index[data.Date.isin([date])][0] + 1]
	    return list(target_date.Date)

参数说明

* __date :__ 基准日期，字符串类型
* __lag :__ 基准日期前lag日期，数值类型

使用实例

	trade_date_list = get_trade_date('2018-01-09', 5)

输出结果

	['2018-01-02',
 	 '2018-01-03',
 	 '2018-01-04',
 	 '2018-01-05',
 	 '2018-01-08',
 	 '2018-01-09']

###get\_panel\_data(stock\_pool, target\_data, date, lag)

函数说明

* 获取面板数据

代码实现

	def get_panel_data(stock_pool, target_data, date, lag):
    panel_data = pd.Series()
    date_lag = get_trade_date(date, lag)[0]
    for stock_code in stock_pool:
        time_series_data = pd.read_sql('select %s, %s from %s where Date between "%s" and "%s"'%(target_data, 'Date', stock_code[0], date_lag, date), conn, index_col='Date')
        time_series_data.columns = [stock_code[0]]
        panel_data = pd.concat([panel_data, time_series_data], axis=1)
    panel_data.drop(panel_data.columns[0], axis=1, inplace=True)
    return panel_data.dropna(axis=1)

参数说明

* __stock\_pool :__ 股票池，列表套元祖类型
* __target\_data :__ 股票交易数据类型，一次只能取一种，字符串类型

使用实例

	open = get_panel_data([('stock_603898'), ('stock_603899')], 'Open', '2018-01-09', 5)

输出结果

	            stock_603898  stock_603899
	Date                                  
	2018-01-02         29.92         24.60
	2018-01-03         30.25         24.61
	2018-01-04         30.10         24.31
	2018-01-05         30.19         24.05
	2018-01-08         30.20         24.96
	2018-01-09         30.88         25.17

###delta(panel_data, lag)

函数说明

* 获取当前面板数据与若干天前的面板数据之差

代码实现

	def delta(panel_data, lag):
		return panel_data.diff(lag)

参数说明

* __panel\_data :__ 面板数据

使用实例

	delta(open, 2)

输出结果

            stock_603898  stock_603899
	Date                                  
	2018-01-02           NaN           NaN
	2018-01-03           NaN           NaN
	2018-01-04          0.18         -0.29
	2018-01-05         -0.06         -0.56
	2018-01-08          0.10          0.65
	2018-01-09          0.69          1.12

###delay(panel_data, lag)

函数说明

* 获取当前面板数据若干天前的面板数据

代码实现
	
	def delay(panel_data, lag):
	    return panel_data.shift(lag)

使用实例

	delay(open, 2)

输出结果

            stock_603898  stock_603899
	Date                                  
	2018-01-02           NaN           NaN
	2018-01-03           NaN           NaN
	2018-01-04         29.92         24.60
	2018-01-05         30.25         24.61
	2018-01-08         30.10         24.31
	2018-01-09         30.19         24.05
	
###standard\_rank(panel_data, window, axis=1)

函数说明

* 对面板数据进行标准化排名

代码实现

	def standard_rank(panel_data, window, axis=1):
	    if axis == 1:
	        return panel_data.iloc[-window:, ].rank(axis=1, pct=True)
	    elif axis == 0:
	        return panel_data.iloc[-window:, ].rank(pct=True)

参数说明

* __window :__ 排名区间
* __axis :__ 默认为1，横向排名，可选为0，纵向排名

使用实例

	rank_data = standard_rank(open)

输出结果

            stock_603898  stock_603899
	Date                                  
	2018-01-03           1.0           0.5
	2018-01-04           1.0           0.5
	2018-01-05           1.0           0.5
	2018-01-08           1.0           0.5
	2018-01-09           1.0           0.5

###correlation(panel\_data\_1, panel\_data\_2, window)

函数说明

* 计算两个经过rank()函数操作后数据的相关系数

代码实现

	def correlation(panel_data_1, panel_data_2, window):
	    return panel_data_1.rolling(window).corr(panel_data_2)

应用实例

	close = get_panel_data([('stock_603898'), ('stock_603899')], 'Close', '2018-01-09', 5)
	corr = correlation(standard_rank(open), standard_rank(close), 5)

输出结果

	stock_603898    inf
	stock_603899    inf

###alpha\_sum(panel_data, window)

函数说明

* 移动求和

代码实现

	def alpha_sum(panel_data, window):
	    return panel_data.rolling(window).sum()

应用实例

	sum(open, 5)

输出结果

	            stock_603898  stock_603899
	Date                                  
	2018-01-02           NaN           NaN
	2018-01-03           NaN           NaN
	2018-01-04           NaN           NaN
	2018-01-05           NaN           NaN
	2018-01-08        150.66        122.53
	2018-01-09        151.62        123.10

###ts\_rank(panel\_data, day)

函数说明

* 时间序列排名

代码实现

	def ts_rank(panel_data, day):
	    return standard_rank(panel_data, day, axis=0)

应用实例

	ts_rank(open, 3)

输出内容

            stock_603898  stock_603899
	Date                                  
	2018-01-05      0.333333      0.333333
	2018-01-08      0.666667      0.666667
	2018-01-09      1.000000      1.000000

##Main Phase

__重要变量__

	open = get_panel_data(stock_pool, 'Open', date, lag=20)
	high = get_panel_data(stock_pool, 'High', date, lag=20)
	low = get_panel_data(stock_pool, 'Low', date, lag=20)
	close = get_panel_data(stock_pool, 'Close', date, lag=20)
	returns = get_panel_data(stock_pool, 'ChgRate', date, lag=20)
	volume = get_panel_data(stock_pool, 'Volume', date, lag=20)
	vwap = get_pane_data(stock_pool, 'Vwap', date, lag=20)

###alpha_002()

计算公式

* (-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6))

代码实现

	def alpha_002():
    	return -1 * correlation(standard_rank(delta(np.log(volume), 2)), standard_rank((close/open-1)), 6)

###alpha_003()

计算公式

* (-1 * correlation(standard_rank(open), standard_rank(volume), 10))

代码实现

	def alpha_003():
    	return -1 * correlation(standard_rank(open), standard_rank(volume), 10)

###alpha_006()

计算公式

* (-1 * correlation(open, volume, 10))

代码实现

	def alpha_006():
    	return -1 * correlation(open, volume, 10)

###alpha_008()

计算公式

* (-1 * rank(((sum(open, 5) * sum(returns, 5)) - delay((sum(open, 5) * sum(returns, 5)),
10))))

代码实现

	def alpha_008():
	    return  -1 * rank((alpha_sum(open, 5) * alpha_sum(returns, 5)) - delay(alpha_sum(open, 5) * alpha_sum(returns, 5), 10), 1)
