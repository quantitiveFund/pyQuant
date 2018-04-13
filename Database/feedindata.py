# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 23:11:16 2018
@author: CS
"""
import urllib.request
from bs4 import BeautifulSoup
import re
import time
import csv
import requests
import os
import pandas as pd
import mysql.connector

conn = mysql.connector.connect(host="localhost",port=3306,user="root",\
                       password="",database="",charset="utf8")
cur = conn.cursor()

def table_exist(tab_name):
    cur.execute('show tables')  # 罗列所有当前库里面的所有表格
    tables = cur.fetchall()
    selectab = re.compile(r'\w*stock_\w*')
    tabnames = selectab.findall(str(tables))
    res = tab_name in tabnames
    return res

def get_html(url):
    #获取请求头，以浏览器身份查看网页信息
    headers = ("User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36")
    opener = urllib.request.build_opener()
    opener.addheaders = [headers]
    html = opener.open(url).read()
    html = html.decode("gbk","ignore")
    return html


def get_stockcode(html):
    #利用正则表达式定位股票代码
    pat = '<a target="_blank" href="http://quote.eastmoney.com/\S\S(.*?).html">'
    #根据正则表达式的定位爬取所有股票代码
    code = re.compile(pat).findall(html)
    return code


#定义一个爬虫函数，锁定网易财经网页中股票数据的具体位置
def crawl_stockdata(code):
    #将网址中自变量设置为str类型
    try:
        for yr in range(1991,2019):
            for season in range(1,5):
                pagecontent = requests.get('http://quotes.money.163.com/trade/lsjysj_'+code+'.html?year='+yr+'&season='+season)
                #利用BeautiSoup库将HTML文档格式化
                soup = BeautifulSoup(pagecontent.text, 'lxml')
                #利用BeautiSoup库中的find_all(div,attr)函数定位到股票数据的表格
                table = soup.find_all('table',{'class':'table_bg001'})[0]
                #从大表格中具体定位到<tr></tr>标签下的11个股票数据
                revrows = table.find_all('tr')
                # 原来的顺序相反
                rows = revrows[::-1]
                # 将数据梳理出来
                for row in rows:
                    rowinpage = []
                    if row.find_all('td') != []:
                        for cell in row.find_all('td'):
                            rowinpage.append(cell.get_text())
                        if rowinpage != []:
                            writeintocsv(code, rowinpage)
                            writeintosql(code, rowinpage)
    except:
        #如果爬虫失败则抛出异常
        print("crawling goes wrong.")
    return 
   

def writeintocsv(code, rowinpage):
    code = str(code)
    fileloc = 'E:\\FangCloudSync\\python\\workfiles\\winddata\\data\\'
    try:
        csvFile = open( fileloc + code + '.csv')
        writer = csv.writer(csvFile)
        writer.writerow(rowinpage)
    except FileNotFoundError:
        csvFile = open( fileloc + code + '.csv','w',newline = '')
        writer = csv.writer(csvFile)
        writer.writerow(('Date','Open',\
        'High','Low','Close','ChgRate','ChgAmount','Volume','VolTrans','Ranges','Turnover'))
        writer.writerow(rowinpage)


def writeintosql(code, rowinpage):
    for code in rowinpage:
    #数据库手动建表可以以纯数字作为表名，以代码建表不能以纯数字作为表名，报ProgrammingError
        sql2 = "CREATE TABLE stock_%s" % code[0:6] + " (\
     Date DATE,\
     Open DECIMAL(18,2),\
     High DECIMAL(18,2),\
     Low  DECIMAL(18,2),\
     Close DECIMAL(18,2),\
     ChgRate DECIMAL(18,2),\
     ChgAmount FLOAT,\
     Volume BIGINT,\
     VolTrans BIGINT,\
     Ranges FLOAT,\
     Turnover FLOAT)"
    cur.execute(sql2)
    print("%s" % code[0:6] + " is now storing.")
    time_start = time.time()
    length = len(data)
    for s in range(0,len(data)):
        record = tuple(data.loc[s])
        try:
            sql3 = "INSERT INTO stock_%s" % code[0:6] + "\
            (Date,Open,High,Low,Close,ChgRate,ChgAmount,Volume,VolTrans,Ranges,Turnover)\
            VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " % record
            sql3 = sql3.replace('nan','null').replace('NaN','null')\
            .replace('None','null').replace('none','null')
            cur.execute(sql3)
        except:
            break

    conn.commit()
    cur.close()
    print('Time spent on stock '+s+' is %d sec.' % (time.time()-time_start))
conn.close()
    
#主函数
if __name__ == '__main__':
    #东方财富网所有股票代码的URL
    codeUrl = 'http://quote.eastmoney.com/stocklist.html'
    #调用上述函数获取所有股票代码
    code = get_stockcode(get_html(codeUrl))
    #code = get_stockcode(requests.get(codeUrl))
    codeList = []#创建一个存储所有股票代码的列表
    
    #遍历所有股票代码中的个股，取出其中的深沪，创业板，中小板股票代码
    for single in code:
        if single[0] == '0':
            codeList.append(single)
        if single[0] == '3':
            codeList.append(single)
        if single[0] == '6':
            codeList.append(single)
    # codeList.append(single for single in code if single[0] == ('0' or '3' or '6'))
#    #遍历集合中每一个股票代码,将对应数据爬取到csv文件中
    for code in codeList:
        time_start = time.time()
        tablename = 'stock_'+ code
        if table_exist(tablename):
            #update the SQL and CSV
        else:
            crawl_stockdata(code)
 
        print('Time spent on stock '+s+' is %d sec.' % (time.time()-time_start))
