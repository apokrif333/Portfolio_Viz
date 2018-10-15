import sys
sys.path.insert(0, 'C:/Users/Tom/PycharmProjects/Start/GibHub/My_Libs')

import pandas as pd
import numpy as np
import os
import trading_lib as tl

from datetime import datetime


# Построение структуры портов и переменные
def_data_direct = 'exportTables'

capital = 10_000
newest_dates = [datetime(2007, 1, 1)]  # Стартовая дата (можно не указывать)
oldest_dates = [datetime.now()]  # Конечная дата (можно не указывать)

max_risk_on_alloc = {}
risk_on_alloc = {}
max_risk_off_alloc = {}
risk_off_alloc = {}

# Чеки
bool_redownload_data = 1
bool_sma = 1
bool_mom = 1
bool_rebalance = 1  # 1 в конце месяца, 0 в начале месяца
chart_or_save = 1  # 1 вывести итоговый график, -1 сохранить файл, 0 вывести график и сохранить файл

# Условные константы
RISKON_TICKER = 'DIA'
RISKOFF_TCKER = 'TLT'
SMA_PERIOD = 200
SMA_UP = 1.005
SMA_DOWN = 0.995
MOM_RISK_ON = 2  # Окно моментума. Колонку посчитаем сразу как для последнего числа месяца, так и для первого
MOM_RISK_OFF = 2

NO_REBALANCE = 0.05  # Допустимое отклонение для активов без ребаланса
DIV_TAX = 0.9  # Что остаётся после налога на дивы
IB_COMM = 0.0055


''' Описание
1) Моментумы для DIA и TLT Done
2) SMA (close - average) / average, хотя можно просто SMA * 1.005 или SMA * 0.995. Done
2) Если SMA(DIA) > 0.5%,  MOM(DIA) > 0, MOM(TLT) < 0: QLD; FBT; FDN; DDM
3) Если SMA(DIA) > 0.5%,  MOM(DIA) < 0, MOM(TLT) > 0: QLD(0.15), IVW(0.35), FBT(0.2), FDN(0.2), TLT(0.1)
4) Если SMA(DIA) < -0.5%,  MOM(DIA) < 0: TLT, IEF, FXY
5) Если SMA(DIA) < -0.5%,  MOM(DIA) > 0 OR MOM(TLT) > 0: XLP(0.2), TLT(0.2), IEF(0.2), FXY(0.2)      
6) Ребаланс или 31 числа, или 1 числа. Если инструменты разошлились от весов на N%, то не балансируем  Done
7) Учесть левередж, так как в 4-ом условии капитал на 0.8 Done
8) Левередж писать так, чтобы учесть внедрение внутридневного VIX/VIX3M. VIX/VIX3M для снижения экспозы или смены порта. Done  
9) Комисиссии IB-шные Done

context.assets = { 
        symbol('QLD'): 0,
        symbol('IVW'): 0,
        symbol('FBT'): 0,
        symbol('FDN'): 0,
        symbol('DDM'): 0,
        symbol('XLP'): 0,
        symbol('TLT'): 0,
        symbol('IEF'): 0,
        symbol('FXY'): 0,
        symbol('FXF'): 0,
        symbol('UUP'): 0,
        symbol('GLD'): 0,
        symbol('ITA'): 0,
        } Done
'''


def calc_SMA(df: pd.DataFrame):
    tl.save_csv()


def calc_momentum(df: pd.DataFrame):
    tl.save_csv()


def dict_nonzero(dict: dict) -> dict:
    pass


if __name__ == '__main__':
    # Сложить ключи всех словарей, вывести уникальные и проверить если ли по ним data, и чекнуть на требование скачки
    tl.download_yahoo()

    # Изменить портфели-словари, выкинув из них все value с 0
    dict_nonzero()

    # Рассчитать SMA для DIA и сохранить колонку в DIA файл. И есть ли чек на расчёт SMA.
    calc_SMA()

    # Рассчитать моментумы DIA и TLT, сохранить колонку в файлы. Есть ли чек на расчёт моментума.
    calc_momentum()

    # Создаём словари с датой, так как количество тикеров - неизвестно
    max_risk_on_data = {}
    risk_on_data = {}
    max_risk_off_data = {}
    risk_off_data = {}

    # Обрезаем дату тикеров так, чтобы была одинаковая размерность

    # Создаём словарь с динамикой капитала, типа Capital, Cash, Shares_1 ... Shares_N, TickerName_1 ... TickerName_N,
    # DivTicker_1 ... Div_Ticker_N (столько N, сколько позиций в максимально позиционном порте). Из месяца в месяц будут
    # использоваться те же колонки, но для разных тикеров.

    # Берём из любой data торговые даты и начинаем перебирать
    past_port = ''
    for i in Date:
        # Если сегодня день для ротации и исходя из условий SMA и MOM мы берём тот же port, что и past_port:
            # Тогда проверяем отклонения, если они больше NO_REBALANCE, балансируемся.
            # Если меньше NO_REBALANCE, то просто чекам на дивы, оставляя сайзы прежними.

        # Если сегодня день для ротации и исходя из условий SMA и MOM мы берём иной port:
            # Чекаем прошлые позиции на ночные дивы исходя из вчерашних сайзов. Считаем капитал под конец дня с учётом
            # дивов. Если есть пересекающиеся старые тикеры, с новыми, считаем весовую разницу отдельной фукнцией.
            # Итерируем ключи нового порт-словаря и для каждого непересечённого тикера извлекаем его вес, рассчитываем
            # долю (уменьшенную на размер комиссии покупки и продажи), прописываем новые значения в capital-словарь.
            # Суммируем все новые доли и если они меньше 1, значит есть кэш. Перезаписываем past_port.

        # Если сегодня не день для ротации и past_port == '': мы ещё не торговали, тянем капитал, а количество акций
        # в колонках = 0

        # Если сегодня не день для ротации и past_port != '':  тянем сайзы и чекам дивы; В дальнешем здесь будет также
        # находится внутримесячная проверка на VIX/VIX3M, если она срабатывает: ...

    # Финальные if-условия. Вывести график, сохранить capital-словарь в файл или, и график, и файл.
