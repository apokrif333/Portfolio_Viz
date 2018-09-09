import os
import trading_lib as tl


# Variables
download_data = True
def_data_direct = 'exportTables'
tickers_list = ['QQQ', 'DIA', 'IBB']


if __name__ == '__main__':
    for t in tickers_list:
        if os.path.isfile(os.path.join(def_data_direct, str(t) + '.csv')) is False or download_data:
            tl.download_yahoo(t)
