import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pylab import *
import itertools

dt_start = dt.datetime(2010, 1, 1)
dt_end = dt.datetime(2010, 12, 31)
dt_timeofday = dt.timedelta(hours=16)
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

def simulate(start_date, end_date, ls_symbols):
    print "Start Date: %s" % start_date
    print "End Date: %s" % end_date
    print "Symbols: %s" % ls_symbols

    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # get data
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # fill forward
    df_rets = d_data['close'].copy()
    df_rets = df_rets.fillna(method='ffill')
    df_rets = df_rets.fillna(method='bfill')

    # extract prices as values
    na_price = df_rets.values

    # calculate normalized prices as cumulative return
    na_normalized_price = na_price / na_price[0,:]
    #print na_normalized_price

    # create array with legal combinations of the portfolio
    shares = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
    legal_ports = []
    set = [p for p in itertools.product(shares, repeat=len(ls_symbols))]
    for x in set:
        if sum(x)==1.0:
            legal_ports.append(list(x))

    #print legal_ports

    highest_sharpe = 0
    for comb in legal_ports:
        na_port_rets = np.sum(na_normalized_price*comb, axis=1)
        #print na_port_rets
        
        normalized_portfolio_return = na_port_rets.copy()
        port_daily_rets = tsu.returnize0(normalized_portfolio_return)
        #print port_daily_rets
        #na_port_daily_rets = np.sum(daily_ret*ls_alloc, axis=1)
        
        # calculate metrics
        port_mean=mean(port_daily_rets.copy())
        port_std=std(port_daily_rets.copy())
        sharpe_port = sqrt(252)*(port_mean/port_std.copy())
        if sharpe_port > highest_sharpe:
            highest_sharpe = sharpe_port.copy()
            opt_alloc = comb

    print "Volatility (stdev of daily returns): %f" % port_std
    print "Sharpe Ratio: %f" % highest_sharpe
    print "Optimal Alloc: %s" % opt_alloc
    print "Average daily return: %f" % port_mean
    print "Cumulative Return: %f" % na_port_rets[-1]

    return opt_alloc


print simulate(dt_start,dt_end,['AAPL','GOOG','IBM','MSFT'])

