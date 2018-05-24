# 回测框架

## Event

注：属性调用方法为Class.attribution，方法即函数，调用方法为Class.method()

### Event()

类说明

* Event大类，仅用于区分其他大类

### MarketEvent(Event)

类说明

* MarketEvent是Event的子类，继承了Event所有属性，当市场产生交易时，会生成该类（未实现）。

属性说明

* __type :__ 用于区分Event下各个子类

### OrderEvent(Event)

类说明

* OrderEvent是Event的子类，向市场投放订单时，会调用该类。

属性说明

* __type :__ 用于区分Event下各个子类
* __symbol :__ 股票代码
* __order\_type :__ 订单类型，限价单或市价单（未实现）
* __quantity :__ 股票数量，单位为股
* __direction :__ 买入或卖出

方法说明

* __to\_dict() :__ 返回一个字典

### FillEvent(Event)

类说明

* FillEvent是Event的子类，向市场投放订单后，订单交易完成后会调用该类

属性说明

* __type :__ 用于区分Event下各个子类
* __timeindex :__ 订单完成时间
* __symbol :__ 股票代码
* __cost :__ 订单总价格（不含手续费）
* __quantity :__ 股票数量
* __direction :__ 买入或卖出
* __commission :__ 手续费

方法说明

* __calculate\_commission() :__ 计算手续费（未实现）

## DataHandler

### DataHandler():

类说明

* DataHandler大类，用于区分其他大类

特别说明

* __@abstractmethod :__ 虚拟方法声明，表示下列定义方法为虚拟方法，每定义一个虚拟方法前都须声明一次。 虚拟方法不直接实现，而会在子类中实现。

### DatabaseHandler(DataHandler)

类说明

* DatabaseHandler是DataHandler的子类，用于处理各类数据

属性说明

* __events :__ 一个Event类，实际用途未知
* __symbol\_list :__ 股票代码池
* __symbol\_data :__ 股票历史数据，{keys = symbol : values = DataFrame}
* __symbol\_latest\_data :__ 股票最新数据，{keys = symbol : values = [()]}
* __continue :__ 回测终止判断？
* __generator :__ 迭代器，用于模拟实盘交易环境，{keys = symbol : values = generator}

特别说明

* __\_function() :__ 在类方法前加一个下划线表示该方法仅用于该类内部调用，外部调用虽然不会报错，但是不建议调用
* __yield :__ 生成一个迭代器，只能在函数中存在，并且在循环中调用, 当循环执行至yield时，会停止执行，等待next()命令，输入命令后，会再次执行并再次终止等待，直到循环结束。
* __next() :__ 在上一次迭代器终止处执行迭代器，循环完成后再执行会报错

例子

* 生成一个迭代器

		def generator():
			for i in range(5):
				yield print(i)
		
		gen = generator()

* 执行next()

		In [1]: next(gen)
		Out [1]: 0
		In [2]: next(gen)
		Out [2]: 1
		In [3]: next(gen)
		Out [3]: 2
		In [4]: next(gen)
		Out [4]: 3
		In [5]: next(gen)
		Out [5]: 4
		In [6]: next(gen)
		Out [6]: StopIteration

方法说明

* __\_load\_from\_database() :__ 缓存数据库中的数据，并存入symbol\_data中
* __\_get\_new\_bars() :__ 迭代器，逐条获取数据
* __\_get\_generator() :__ 生成迭代器并存入generator中
* __get\_latest\_data() :__ 获取某只股票的最新一天的数据
* __updata\_data() :__ 执行迭代器，从symbol\_data中逐条获取数据

## Portfolio

### Portfolio()

类说明

* Portfolio大类，用于区分其他大类

### NaviePortfolio(Portfolio)

类说明

* Portfolio的子类，用于存放各类信息

属性说明

* __bars :__ 应该指一条数据，但实际用的是DataHandler类
* __events :__ 一个Event类，实际用途未知
* __start\_date :__ 回测开始日期
* __initial\_cash :__ 初始资金
* __symbol\_list :__ 股票代码池
* __all\_positions :__ 详见代码
* __current\_positions :__ 详见代码
* __all\_holdings :__ 详见代码
* __current\_holdings :__ 详见代码

方法说明

* __construct\_all\_positions() :__ 创建all\_positions
* __construct\_all\_holdings() :__ 创建all\_holdings
* __construct\_current\_holdings() :__ 创建current\_holdings
* __update\_timeindex() :__ 传入一个FillEvent并调整all\_positions
* __update\_positions\_from\_fill() :__ 传入一个FillEvent并调整current\_positions
* __update\_holdings\_from\_fill() :__ 传入一个FillEvent并调整current\_holdings
* __update\_fill() :__ 同时调用update\_positions\_from\_fill()与update\_holdings\_from\_fill()方法
