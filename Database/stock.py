#爬取单个股票数据并存入单个数据表，以2001-2010为例
import requests
import pandas as pd 
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import re
from sqlalchemy import create_engine
import pymysql

engine = create_engine('mysql+mysqldb://root:*******@localhost:3306/**?charset=utf8')  

def get_page(url):
    try:
        header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
        response=requests.get(url,headers=header)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None
    

         
def parse_write(code):
    for ex_code in code:
        try:
            for year in range(2001,2010): 
                for season in range(1,5):   
                    url=('http://quotes.money.163.com/trade/lsjysj_'+str(ex_code)+'.html?year='+str(year)+'&season='+str(season))
                    html=get_page(url)
                    soup = BeautifulSoup(html,'lxml')
                    content = soup.select('.inner_box')[0]
                    tbl=pd.read_html(content.prettify(),header = 0)[0].drop([0])
                    tbl.columns=['Date','Open','High','Low','Close','ChgAmount','ChgRate','Volume','VolTrans','Swing','Turnover']
                    tbl=tbl.sort_values(by='Date', ascending=True)
                    pd.io.sql.to_sql(tbl, "stock_%s" % ex_code[0:6], engine, schema = '**', if_exists = 'append',index=False)
                    print("stock_%s" % ex_code[0:6]+"success")
                
        except:
            print("stock_%s" % ex_code[0:6]+"fail")

  
if __name__ == '__main__':
    code_html=get_page('http://quote.eastmoney.com/stocklist.html')
    pattern=re.compile('<a.*?com/\S\S(.*?).html">',re.S)
    allcode=re.findall(pattern,code_html)
    request_code=[]
    for code1 in allcode:
        if code1[0] =='0' or code1[0] == '3' or code1[0] =='6':
            request_code.append(code1)         
    parse_write(request_code)
    
    
#将数据表按时间分块并连接成大数据表
import pandas as pd
from sqlalchemy import create_engine

conn = create_engine('mysql+mysqldb://root:******@localhost:3306/test?charset=utf8')    


def get_trade_date(stock):
    start_date = pd.read_sql('select min(Date) from %s' % (stock), conn).iat[0, 0]
    end_date = pd.read_sql('select max(Date) from %s' % (stock), conn).iat[0, 0]
    trade_date = pd.read_sql('select date from index_000001 where date between "%s" and "%s"' % (start_date, end_date), conn, index_col='date')
    return trade_date

def get_stock_data(stock):
    stock_data = pd.read_sql('select * from %s' % (stock), conn, index_col='DATE')
    trade_date = get_trade_date(stock)
    return pd.concat([trade_date, stock_data], axis=1)


if __name__ == '__main__':
    tables = pd.read_sql('show tables', conn)
    stock_list = list(tables.iloc[2:, 0])   
    for stock in stock_list:
        stock_data = get_stock_data(stock)
        stock_data.reset_index(inplace=True)
        stock_data.rename(columns={'index' : 'DATE'}, inplace=True)
        stock_data=pd.concat([stock_data,pd.DataFrame(columns=['code']),],axis=1)
        stock_data.iloc[:,11]=str(stock)
        print(stock)
        pd.io.sql.to_sql(stock_data ,'block' ,conn, schema = 'blockdata', if_exists = 'append',index=False)
  
    
    
    
    
    
    
    
