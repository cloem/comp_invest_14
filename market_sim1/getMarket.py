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
    out_filename = sys.argv[1]
    dt_start = dt.datetime(2010,1,1,)
    dt_end = dt.datetime(2010,12,31)
    ldt_timestamps = du.getNYSEdays(dt_start,dt_end, dt.timedelta(hours=16))
    ls_keys = ['close']
    ls_symbols = ["AAPL"]

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

    df_close.to_csv(out_filename, date_format="%Y,%m,%d", sep=',')
