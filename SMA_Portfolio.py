import os
import pandas as pd
import numpy as np
import trading_lib as tl

from pprint import pprint as pp


# Variables
download_data = False
def_data_direct = 'exportTables'
tickers_list = ['QQQ', 'DIA', 'IBB']  # Список тикеров для портфеля

sma_ticker = 'SPY'  # Тикер из которого берётся SMA для конца месяца
calc_SMA = False
sma_period = 200

start_capital = 10_000
positions = len(tickers_list)


# Calculate SMA
def calculate_SMA(file: pd.DataFrame, ticker: str):
    file['SMA ' + str(sma_period)] = file['Close'].rolling(sma_period).mean()

    for i in range(len(file['Date'])):
        if i == 0:
            temp = [0]
        elif i < len(file) - 1 and file['Date'][i].month != file['Date'][i + 1].month and tl.empty_check(
                file['SMA ' + str(sma_period)][i]):
            if file['Close'][i] >= file['SMA ' + str(sma_period)][i]:
                temp.append(1)
            else:
                temp.append(0)
        else:
            temp.append(temp[-1])

    file['Enter_' + str(sma_period)] = temp
    tl.save_csv(def_data_direct, ticker, file)


if __name__ == '__main__':
    tickers_dict = {}
    for t in tickers_list:
        if os.path.isfile(os.path.join(def_data_direct, str(t) + '.csv')) is False or download_data:
            tl.download_yahoo(t)
        cur_base = tl.load_csv(str(t))
        tl.str_list_to_date(cur_base)
        tickers_dict[str(t)] = cur_base

    if os.path.isfile(os.path.join(def_data_direct, sma_ticker + '.csv')) is False or download_data:
        tl.download_yahoo(sma_ticker)

    sma_ticker_base = tl.load_csv(sma_ticker)
    if calc_SMA:
        calculate_SMA(sma_ticker_base, sma_ticker)

    tickers_dict[sma_ticker] = sma_ticker_base[['Date', 'Enter_' + str(sma_period)]]
    # pp(tickers_dict['DIA']['Close'][tickers_dict['DIA']['Close'] == 81.66].index[2])

    newest_dates = []
    oldest_dates = []
    keys = [sma_ticker]
    keys += tickers_list
    for key in keys:
        newest_dates.append(tickers_dict[key]['Date'][0])
        oldest_dates.append(tickers_dict[key]['Date'].iloc[-1])
    start, end = max(newest_dates), min(oldest_dates)

    for key in keys:
        tickers_dict[key] = tickers_dict[key].loc[
            (tickers_dict[key]['Date'] >= start) & (tickers_dict[key]['Date'] <= end)].reset_index(drop=True)

    tickers_dict['Strategy'] = pd.DataFrame({})
    for key in tickers_list:
        tickers_dict['Strategy'][key+' Shares'] = [x for x in range(len(tickers_dict[sma_ticker]))]
    tickers_dict['Strategy']['Capital'] = [x for x in range(len(tickers_dict[sma_ticker]))]

    pp(tickers_dict)

    for i in range(len(tickers_dict[tickers_list[0]])):
        sma = tickers_dict[sma_ticker]['Enter_' + str(sma_period)]
        pre_capital = 0
        capital = tickers_dict['Strategy']['Capital']

        if i == 0:
            for key in tickers_list:
                tickers_dict['Strategy'][key+' Shares'].iloc[i] = 0
            tickers_dict['Strategy']['Capital'].iloc[i] = start_capital

        elif sma[i] == 1 and sma[i-1] == 0:
            for key in tickers_list:
                tickers_dict['Strategy'][key + ' Shares'].iloc[i] = capital[i-1] / positions / tickers_dict[key]['Close'][i]

                pre_capital += tickers_dict['Strategy'][key + ' Shares'][i] * tickers_dict[key]['Close'][i]
            tickers_dict['Strategy']['Capital'].iloc[i] = pre_capital

        elif sma[i] == 0 and sma[i - 1] == 1:
            for key in tickers_list:
                dividend = tickers_dict[key]['Dividend'][i] / tickers_dict[key]['Close'][i] + 1
                tickers_dict['Strategy'][key + ' Shares'].iloc[i] = tickers_dict['Strategy'][key + ' Shares'][i - 1] * dividend
                pre_capital += tickers_dict['Strategy'][key + ' Shares'][i] * tickers_dict[key]['Close'][i]
            tickers_dict['Strategy']['Capital'].iloc[i] = pre_capital

        elif sma[i] == 1:
            for key in tickers_list:
                dividend = tickers_dict[key]['Dividend'][i] / tickers_dict[key]['Close'][i] + 1
                tickers_dict['Strategy'][key + ' Shares'].iloc[i] = tickers_dict['Strategy'][key + ' Shares'][i - 1] * dividend
                pre_capital += tickers_dict['Strategy'][key + ' Shares'][i] * tickers_dict[key]['Close'][i]
            tickers_dict['Strategy']['Capital'].iloc[i] = pre_capital

        elif sma[i] == 0:
            for key in tickers_list:
                tickers_dict['Strategy'][key + ' Shares'].iloc[i] = 0
            tickers_dict['Strategy']['Capital'].iloc[i] = capital[i - 1]

        print(i, sma[i], tickers_dict['Strategy']['Capital'].iloc[i])