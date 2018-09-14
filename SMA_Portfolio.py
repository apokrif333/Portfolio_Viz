import os
import pandas as pd
import numpy as np
import trading_lib as tl

from datetime import datetime
from pprint import pprint as pp


# Variables
newest_dates = [datetime(2003, 1, 1)]  # Стартовая дата (можно не указывать)
oldest_dates = [datetime.now()]  # Конечная дата (можно не указывать)

def_data_direct = 'exportTables'
tickers_list = ['QQQ', 'DIA', 'IBB']  # Список тикеров для портфеля

sma_ticker = 'SPY'  # Тикер из которого берётся SMA для конца месяца
sma_period = 200

start_capital = 10_000

download_data = False  # Если не нужно перекачивать все инструменты False
calc_SMA = True
hedge_ticker = ''  # Тикер в который порт будет уходить для хэджа
chart_or_save = 1  # 1 вывести итоговый график, -1 сохранить файл, 0 вывести график и сохранить файл
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
    # Download data and create single dict
    tickers_dict = {}
    for t in tickers_list + [hedge_ticker] if hedge_ticker != '' else tickers_list:
        if os.path.isfile(os.path.join(def_data_direct, str(t) + '.csv')) is False or download_data:
            tl.download_yahoo(t)
        tickers_dict[str(t)] = tl.load_csv(str(t))

    # Download data for sma_ticker
    if os.path.isfile(os.path.join(def_data_direct, sma_ticker + '.csv')) is False or download_data:
        tl.download_yahoo(sma_ticker)

    # Calculation SMA
    sma_ticker_base = tl.load_csv(sma_ticker)
    if calc_SMA:
        calculate_SMA(sma_ticker_base, sma_ticker)
    tickers_dict[sma_ticker] = sma_ticker_base[['Date', 'Enter_' + str(sma_period)]]

    # Find start, end dates
    keys = [sma_ticker, hedge_ticker] if hedge_ticker != '' else [sma_ticker]
    keys += tickers_list
    for key in keys:
        newest_dates.append(tickers_dict[key]['Date'][0])
        oldest_dates.append(tickers_dict[key]['Date'].iloc[-1])
    start, end = max(newest_dates), min(oldest_dates)

    # Correct dict by dates
    for key in keys:
        tickers_dict[key] = tickers_dict[key].loc[
            (tickers_dict[key]['Date'] >= start) & (tickers_dict[key]['Date'] <= end)].reset_index(drop=True)

    # Create sub-dict for strategy calculation
    tickers_dict['Strategy'] = pd.DataFrame({})
    for key in tickers_list:
        tickers_dict['Strategy'][key+' Shares'] = [0] * len(tickers_dict[sma_ticker])
    if hedge_ticker != '':
        tickers_dict['Strategy'][str(hedge_ticker)+' Shares'] = [0] * len(tickers_dict[sma_ticker])
    tickers_dict['Strategy']['Capital'] = [0] * len(tickers_dict[sma_ticker])

    for i in range(len(tickers_dict[tickers_list[0]])):
        td_S = tickers_dict['Strategy']
        sma = tickers_dict[sma_ticker]['Enter_' + str(sma_period)]
        pre_capital = 0

        if i == 0 and sma[i] == 0:
            for key in tickers_list:
                td_S.loc[i, key+' Shares'] = 0
            if hedge_ticker != '':
                td_S.loc[i, hedge_ticker + ' Shares'] = start_capital / tickers_dict[hedge_ticker]['Close'][i]
            td_S.loc[i, 'Capital'] = start_capital
            
        elif i == 0 and sma[i] == 1:
            for key in tickers_list:
                td_S.loc[i, key + ' Shares'] = start_capital / positions / tickers_dict[key]['Close'][i]
            if hedge_ticker != '':
                td_S.loc[i, hedge_ticker + ' Shares'] = 0
            td_S.loc[i, 'Capital'] = start_capital

        elif sma[i] == 1 and sma[i-1] == 0:
            if hedge_ticker != '':
                hedge_divid = tickers_dict[hedge_ticker]['Dividend'][i] / tickers_dict[hedge_ticker]['Close'][i] + 1
                td_S.loc[i, hedge_ticker + ' Shares'] = td_S[hedge_ticker + ' Shares'][i - 1] * hedge_divid
                pre_capital = td_S[hedge_ticker + ' Shares'][i] * tickers_dict[hedge_ticker]['Close'][i]
            for key in tickers_list:
                td_S.loc[i, key + ' Shares'] = td_S['Capital'][i - 1] / positions / tickers_dict[key]['Close'][i]
            td_S.loc[i, 'Capital'] = pre_capital if hedge_ticker != '' else td_S['Capital'][i - 1]

        elif sma[i] == 0 and sma[i - 1] == 1:
            for key in tickers_list:
                dividend = tickers_dict[key]['Dividend'][i] / tickers_dict[key]['Close'][i] + 1
                td_S.loc[i, key + ' Shares'] = td_S[key + ' Shares'][i - 1] * dividend
                pre_capital += td_S[key + ' Shares'][i] * tickers_dict[key]['Close'][i]
            if hedge_ticker != '':
                td_S.loc[i, hedge_ticker + ' Shares'] = pre_capital / tickers_dict[hedge_ticker]['Close'][i]
            td_S.loc[i, 'Capital'] = pre_capital

        elif sma[i] == 1:
            for key in tickers_list:
                dividend = tickers_dict[key]['Dividend'][i] / tickers_dict[key]['Close'][i] + 1
                td_S.loc[i, key + ' Shares'] = td_S[key + ' Shares'][i - 1] * dividend
                pre_capital += td_S[key + ' Shares'][i] * tickers_dict[key]['Close'][i]
            if hedge_ticker != '':
                td_S.loc[i, hedge_ticker + ' Shares'] = 0
            td_S.loc[i, 'Capital'] = pre_capital

        elif sma[i] == 0 and hedge_ticker != '':
            hedge_divid = tickers_dict[hedge_ticker]['Dividend'][i] / tickers_dict[hedge_ticker]['Close'][i] + 1
            td_S.loc[i, hedge_ticker + ' Shares'] = td_S[hedge_ticker +' Shares'][i - 1] * hedge_divid
            pre_capital = td_S[hedge_ticker + ' Shares'][i] * tickers_dict[hedge_ticker]['Close'][i]
            for key in tickers_list:
                td_S.loc[i, key + ' Shares'] = 0
            td_S.loc[i, 'Capital'] = pre_capital

        elif sma[i] == 0:
            for key in tickers_list:
                td_S.loc[i, key + ' Shares'] = 0
            td_S.loc[i, 'Capital'] = td_S['Capital'][i - 1]

        print(i, sma[i], td_S['Capital'][i])

    # Add data for strategy
    tickers_dict['Strategy']['Date'] = tickers_dict[sma_ticker]['Date']
    for key in tickers_list + [hedge_ticker] if hedge_ticker != '' else tickers_list:
        tickers_dict['Strategy'][key + ' Close'] = tickers_dict[key]['Close']
        tickers_dict['Strategy'][key + ' Dividend'] = tickers_dict[key]['Dividend']

    if chart_or_save == 1:
        tl.plot_capital(list(tickers_dict['Strategy']['Date']), list(tickers_dict['Strategy']['Capital']))
    elif chart_or_save == -1:
        tl.save_csv(def_data_direct, 'SMA_calc ' + str(sma_period), tickers_dict['Strategy'])
    elif chart_or_save == 0:
        tl.plot_capital(list(tickers_dict['Strategy']['Date']), list(tickers_dict['Strategy']['Capital']))
        tl.save_csv(def_data_direct, 'SMA_calc ' + str(sma_period), tickers_dict['Strategy'])
    else:
        print('Передано не верное значение chart_or_save')
