import requests
import pandas as pd 
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import re
from sqlalchemy import create_engine    
engine = create_engine('mysql+mysqldb://root:11031103@10.23.0.2:3306/balance_sheet?charset=utf8')

def get_page(url):
    try:
        header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
        response=requests.get(url,headers=header)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None
    

def get_sheet(code):
    for ex_code in request_code: 
        try:
            url=('http://quotes.money.163.com/f10/zcfzb_'+str(ex_code)+'.html#01c05')
            html=get_page(url)
            soup = BeautifulSoup(html,'lxml')
            content = soup.select('.inner_box')[0] 
            tbl=pd.read_html(content.prettify(),header = 0)
            data1=tbl[0].drop([0,1,2,56,57,28,90,101],axis=0).reset_index(drop=True)
            result = data1.join(tbl[1])
            print( "stock_%s" % ex_code[0:6])
            pd.io.sql.to_sql(result, "stock_%s" % ex_code[0:6], engine, schema = 'balance_sheet', if_exists = 'append',index=False)
        except:
            print( "stock_%s" % ex_code[0:6]+'fail')

  
if __name__ == '__main__':
    code_html=get_page('http://quote.eastmoney.com/stocklist.html')
    pattern=re.compile('<a.*?com/\S\S(.*?).html">',re.S)
    allcode=re.findall(pattern,code_html)
    request_code=[]
    for code1 in allcode:
        if code1[0] =='0' or code1[0] == '3' or code1[0] =='6':
            request_code.append(code1)    
    get_sheet(request_code)
    
    
#上述代码的URL为资产负债表，只需替换URL和写入的数据库即可 
#利润表   url=('http://quotes.money.163.com/f10/lrb_'+str(ex_code)+'.html#01c06')
#现金流量表 url=('http://quotes.money.163.com/f10/xjllb_'+str(ex_code)+'.html#01c07')
       