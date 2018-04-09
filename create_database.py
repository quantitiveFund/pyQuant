# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 00:54:50 2018

@author: Pikari
"""

import mysql.connector
import pandas as pd
from WindPy import w
w.start()

code_list = w.wset("SectorConstituent","sectorId=a001010100000000;field=wind_code").Data[0]
global d
d = ["open, high, low, close, pre_close, volume, amt, dealnum, chg, \
     pct_chg, vwap, adjfactor, close2, turn, free_turn, oi, oi_chg, pre_settle, \
     settle, chg_settlement, pct_chg_settlement, lastradeday_s, last_trade_day, \
     rel_ipo_chg, rel_ipo_pct_chg, susp_reason, close3, pe_ttm, \
     val_pe_deducted_ttm, pe_lyr, pb_lf, ps_ttm, ps_lyr, dividendyield2, ev, \
     mkt_cap_ard, pb_mrq, pcf_ocf_ttm, pcf_ncf_ttm, pcf_ocflyr, pcf_nflyr, \
     trade_status"]
#D = str.upper(str(d))

def write(code):
    data = w.wsd(code, d, 'ipo')
    data = pd.DataFrame(data.Data, index=data.Fields, columns=data.Times).T
    te = 'create table ' + code[:6] + code[-2:] + ' (id int unsigned auto_increment primary key, \
    trade_date datetime null, \
    open float(20) null, \
    high float(20) null, \
    low float(20) null, \
    close float(20) null, \
    pre_close float(20) null, \
    volume float(20) null, \
    amt float(20) null, \
    dealnum float(20) null, \
    chg float(20) null, \
    pct_chg float(20) null, \
    vwap float(20) null, \
    adjfactor float(20) null, \
    close2 float(20) null, \
    turn float(20) null, \
    free_turn float(20) null, \
    oi float(20) null, \
    oi_chg float(20) null, \
    pre_settle float(20) null, \
    settle float(20) null, \
    chg_settlement float(20) null, \
    pct_chg_settlement float(20) null, \
    rel_ipo_chg float(20) null, \
    rel_ipo_pct_chg float(20) null, \
    susp_reason varchar(50) null, \
    close3 float(20) null, \
    pe_ttm float(20) null, \
    val_pe_deducted_ttm float(20) null, \
    pe_lyr float(20) null, \
    pb_lf float(20) null, \
    ps_ttm float(20) null, \
    ps_lyr float(20) null, \
    dividendyield2 float(20) null, \
    ev float(20) null, \
    mkt_cap_ard float(20) null, \
    pb_mrq float(20) null, \
    pcf_ocf_ttm float(20) null, \
    pcf_ncf_ttm float(20) null, \
    pcf_ocflyr float(20) null, \
    pcf_nflyr float(20) null, \
    trade_status varchar(20) null)'
    cursor.execute(te)
                                     
    for i in range(1, len(data)+1):
        #temp = [str(data.index[i-1]), str(data.OPEN[i-1]), str(data.HIGH[i-1]), str(data.LOW[i-1]), str(data.CLOSE[i-1]), str(data.PRE_CLOSE[i-1]), str(data.VOLUME[i-1]), str(data.AMT[i-1]), str(data.DEALNUM[i-1]), str(data.CHG[i-1]), str(data.PCT_CHG[i-1]), str(data.VWAP[i-1]), str(data.ADJFACTOR[i-1]), str(data.CLOSE2[i-1]), str(data.TURN[i-1]), str(data.FREE_TURN[i-1]), str(data.OI[i-1]), str(data.OI_CHG[i-1]), str(data.PRE_SETTLE[i-1]), str(data.SETTLE[i-1]), str(data.CHG_SETTLEMENT[i-1]), str(data.PCT_CHG_SETTLEMENT[i-1]), str(data.REL_IPO_CHG[i-1]), str(data.REL_IPO_PCT_CHG[i-1]), str(data.SUSP_REASON[i-1]), str(data.CLOSE3[i-1]), str(data.PE_TTM[i-1]), str(data.VAL_PE_DEDUCTED_TTM[i-1]), str(data.PE_LYR[i-1]), str(data.PB_LF[i-1]), str(data.PS_TTM[i-1]), str(data.PS_LYR[i-1]), str(data.DIVIDENDYIELD2[i-1]), str(data.EV[i-1]), str(data.MKT_CAP_ARD[i-1]), str(data.PB_MRQ[i-1]), str(data.PCF_OCF_TTM[i-1]), str(data.PCF_NCF_TTM[i-1]), str(data.PCF_OCFLYR[i-1]), str(data.PCF_NFLYR[i-1]), str(data.TRADE_STATUS[i-1])]
        #上面把None转化成字符串所以报错了
        temp = [str(data.index[i-1]), data.OPEN[i-1], data.HIGH[i-1], data.LOW[i-1], data.CLOSE[i-1], data.PRE_CLOSE[i-1], data.VOLUME[i-1], data.AMT[i-1], data.DEALNUM[i-1], data.CHG[i-1], data.PCT_CHG[i-1], data.VWAP[i-1], data.ADJFACTOR[i-1], data.CLOSE2[i-1], data.TURN[i-1], data.FREE_TURN[i-1], data.OI[i-1], data.OI_CHG[i-1], data.PRE_SETTLE[i-1], data.SETTLE[i-1], data.CHG_SETTLEMENT[i-1], data.PCT_CHG_SETTLEMENT[i-1], data.REL_IPO_CHG[i-1], data.REL_IPO_PCT_CHG[i-1], data.SUSP_REASON[i-1], data.CLOSE3[i-1], data.PE_TTM[i-1], data.VAL_PE_DEDUCTED_TTM[i-1], data.PE_LYR[i-1], data.PB_LF[i-1], data.PS_TTM[i-1], data.PS_LYR[i-1], data.DIVIDENDYIELD2[i-1],data.EV[i-1], data.MKT_CAP_ARD[i-1], data.PB_MRQ[i-1], data.PCF_OCF_TTM[i-1], data.PCF_NCF_TTM[i-1], data.PCF_OCFLYR[i-1], data.PCF_NFLYR[i-1], data.TRADE_STATUS[i-1]]
        sql = 'insert into ' + code[:6] + code[-2:] + ' (trade_date, open, high, low, close, pre_close, volume, amt, dealnum, chg, pct_chg, vwap, adjfactor, close2, turn, free_turn, oi, oi_chg, pre_settle, settle, chg_settlement, pct_chg_settlement, rel_ipo_chg, rel_ipo_pct_chg, susp_reason, close3, pe_ttm, val_pe_deducted_ttm, pe_lyr, pb_lf, ps_ttm, ps_lyr, dividendyield2, ev, mkt_cap_ard, pb_mrq, pcf_ocf_ttm, pcf_ncf_ttm, pcf_ocflyr, pcf_nflyr, trade_status) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, temp)
        
    conn.commit()

conn = mysql.connector.connect(port=3306, user='root', password='888888', database='stock_database')   
cursor = conn.cursor()
conn.commit()

#for code in code_list:
write('000002.SZ')
