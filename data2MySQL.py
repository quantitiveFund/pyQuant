# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 23:11:16 2018

@author: CS
"""

import urllib.request
from bs4 import BeautifulSoup
import re
import time
import mysql.connector
import requests


#连接MySQL数据库
conn = mysql.connector.connect(host="localhost",port=3306,user="root",\
                       password="lemonseth5571.",database="ashare",charset="utf8")
cur = conn.cursor()


def table_exist(tab_name):
    cur.execute('show tables')  # 罗列所有当前库里面的所有表格
    tables = cur.fetchall()
    selectab = re.compile(r'\w*stock_\w*')
    tabnames = selectab.findall(str(tables))
    res = tab_name in tabnames
    return res
  
#定义读取整个网页的函数
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
def crawl_stockdata(code,year,season):
    #将网址中自变量设置为str类型
    #code = str(code)
    year = str(year)
    season = str(season)
    #网易财经的URL形式
    dataUrl = dataUrl = 'http://quotes.money.163.com/trade/lsjysj_'+code+'.html?year='+year+'&season='+season
    #获取网易财经的整版网页
    stockdata = requests.get(dataUrl)
    #利用BeautiSoup库将HTML文档格式化
    soup = BeautifulSoup(stockdata.text,'lxml')
    #利用BeautiSoup库中的find_all(div,attr)函数定位到股票数据的表格
    table = soup.find_all('table',{'class':'table_bg001'})[0]
    #从大表格中具体定位到<tr></tr>标签下的11个股票数据
    rows = table.find_all('tr')
    return rows[::-1]


'''定义一个写入csv文件的函数，所有股票代码已经通过正则表达式从东方财经爬取，
而一年只有四个季度，后来又发现随便输入一个年份网页不会报错，仅仅显示没有数据，
不妨从1991年开始爬取，表格中数据为空则跳过对应年份的网页接着爬'''
def crawl2MySQL(code):
    #创建股票数据库表
    sql = "CREATE TABLE IF NOT EXISTS stock_%s" % code[0:6] + "\
    (Date TEXT,\
     Open TEXT,\
     High TEXT,\
     Low TEXT,\
     Close TEXT,\
     ChgAmount TEXT,\
     ChgRate TEXT,\
     Volume TEXT,\
     VolTrans TEXT,\
     Swing TEXT,\
     Turnover TEXT)"
    cur.execute(sql)
    try:
        #遍历1991年到2018年的URL
        for i in range(1991,2019):
            #遍历每个年份1季度到4季度的URL
            for j in range(1,5):
                #调用定位具体股票数据位置的函数
                rows = crawl_stockdata(code,i,j)
                #将<table></table>标签中的11个数据写入csv文件中
                for row in rows:
                    Row = []
                    if row.find_all('td') != []:
                        for cell in row.find_all('td'):
                            Row.append(cell.get_text().replace(',',''))
                        if Row != []:
                            cur.execute("INSERT INTO stock_%s" %code[0:6] + \
                                        "(Date,Open,High,Low,Close,ChgAmount,\
                                        ChgRate,Volume,VolTrans,Swing,Turnover)\
                                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", Row)
            time.sleep(2)#睡眠2秒
    
    except:
        #如果爬虫失败则抛出异常
        print("crawling goes wrong.")
    
    
    '''
    finally:
        conn.commit()
        cur.close()
        conn.close()
    '''
#主函数
if __name__ == '__main__':
    codeUrl = 'http://quote.eastmoney.com/stocklist.html'
    #调用上述函数获取所有股票代码
    wholecodelist = get_stockcode(get_html(codeUrl))
    codeList = []#创建一个存储所有股票代码的列表
    
    #遍历所有股票代码中的个股，取出其中的深沪，创业板，中小板股票代码
    for single in wholecodelist:
        if single[0] == '0' or single[0] == '3' or single[0] == '6':
            codeList.append(single)
    #遍历集合中每一个股票代码,将对应数据存储到MySQL数据库中
    for code in codeList[0:4]:
        tablename = 'stock_'+ code
        if table_exist(tablename):
            print('Stock '+code+ ' exist in the database.')
        else:
            time_start = time.time()
            crawl2MySQL(code)
            print('Time spent on stock '+code+' is %d sec.' % (time.time()-time_start))
        






































