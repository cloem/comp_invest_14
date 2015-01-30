import datetime as dt
import pandas as pd
import numpy as np 
import sys
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep
 
if __name__ == "__main__":
    init_wealth = float(sys.argv[1])
    in_filename = sys.argv[2]
    out_filename = sys.argv[3]
    read_trades = pd.read_csv(in_filename, keep_default_na=0, names=['year', 'month', 'day', 'symb', 'b/s', 'qt'], parse_dates=[['year','month','day']])
    
    #print read_trades
    trades = read_trades
    sorted_trades= trades.sort(['year_month_day', 'symb', 'b/s', 'qt'])
    print sorted_trades

    # extract symbols and timespan from dataframe
    for i in range(0,len(sorted_trades)):
        sorted_trades.loc[i,'symb'] = sorted_trades.loc[i,'symb'].strip()
        
    set_symbols = set(sorted_trades.loc[:,'symb'])
    ls_symbols = list(set_symbols)
    #ls_symbols.append('SPY')
    #print ls_symbols

    set_dates = set(trades.loc[:,'year_month_day'])
    ls_dates = list(set_dates)

    #set trading days
    dt_start = min(ls_dates)
    dt_end = max(ls_dates)
    dt_end += dt.timedelta(days=1)
    ldt_timestamps = du.getNYSEdays(dt_start,dt_end, dt.timedelta(hours=16))
    ls_keys = ['close']

    #read in data
    dataobj = da.DataAccess('Yahoo')
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    #fill missing data
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_close = d_data['close']
    #print df_close 

    timestamps = df_close.index

    df_cash = pd.Series(init_wealth, index=timestamps)
    df_value = pd.Series(0,index=timestamps)

    df_own = copy.deepcopy(df_close)
    df_own = df_own * 0

    for i in range(0,len(sorted_trades.index)):
        dt_trunc = str(sorted_trades.loc[i,'year_month_day'].date())
        dt_end_trunc = str(dt_end.date())
        
        # update cash array
        delta_cash = float(df_close[dt_trunc][sorted_trades.loc[i,'symb']].values) * float(sorted_trades.loc[i,'qt'])

        if(sorted_trades.loc[i,'b/s'] == 'Buy'):
            df_cash.ix[dt_trunc:dt_end_trunc] -= delta_cash
            df_own[sorted_trades.loc[i,'symb']].ix[dt_trunc:dt_end_trunc] += float(sorted_trades.loc[i, 'qt'])
        else:
            df_cash.ix[dt_trunc:dt_end_trunc] += delta_cash
            df_own[sorted_trades.loc[i,'symb']].ix[dt_trunc:dt_end_trunc] -= float(sorted_trades.loc[i, 'qt'])

    # calculate value of portfolio
    for j in range(0,len(timestamps)):
        f_portfolio_value = df_value.ix[timestamps[j]]
        for s_sym in ls_symbols:
            f_portfolio_value += df_own[s_sym].ix[timestamps[j]] * df_close[s_sym].ix[timestamps[j]]

        df_value.ix[timestamps[j]] = f_portfolio_value + df_cash.ix[timestamps[j]]

    #print df_own
    #print df_cash
    #print df_value
    na_returns = df_value.values
    total_ret = 1+ (na_returns[-1]-na_returns[0])/na_returns[0]
    print "Total Return: " + str(total_ret)
    tsu.returnize0(na_returns)
    n_std = np.std(na_returns)
    print "Standard Deviation: " + str(n_std)
    av_rets = sum(na_returns)/len(na_returns)
    print "Average Return: " + str(av_rets)

    n_shra = math.sqrt(252)*av_rets/n_std
    print "Sharpe Ratio: " + str(n_shra)

    df_value.to_csv(out_filename, sep=',')
