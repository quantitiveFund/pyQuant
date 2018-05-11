# Back Testing

## 数据存储类型

### 历史数据

* 数据类型

stock\_data = {keys = stock_code : values = stock\_history\_data}

* 类型说明

__stock\_code :__ 股票代码，str类型

__stock\_history\_data :__ 股票历史数据，DataFrame类型

### 交易日志

* 数据类型

trade\_data = {keys = date : values = {keys = stock\_code : values = [cost, position, market_price, amt, profit]}}

* 类型说明

__date :__ 交易日，str类型

__cost :__ 股票买入成本，float类型

__position :__ 股票持仓量，单位为手，float类型

__market\_price :__ 股票市价，通常为收盘价，float类型

__amt :__ 持有股票的总价格，float类型

__profit :__ 利润，float类型

### 资金账户

* 数据类型

money_account = {keys = 'leftovers' : values = money}

#building