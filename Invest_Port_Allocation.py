import sys
sys.path.insert(0, 'C:/Users/Tom/PycharmProjects/Start/GibHub/My_Libs')

import pandas as pd
import numpy as np
import os
import trading_lib as tl

''' Описание
1) Моментумы для DIA и TLT
2) SMA (close - average) / average, хотя можно просто SMA * 1.005 или SMA * 0.995. 
2) Если SMA(DIA) > 0.5%,  MOM(DIA) > 0, MOM(TLT) < 0: QLD; FBT; FDN; DDM
3) Если SMA(DIA) > 0.5%,  MOM(DIA) < 0, MOM(TLT) > 0: QLD(15), IVW(0.35), FBT(0.2), FDN(0.2), TLT(0.1)
4) Если SMA(DIA) < -0.5%,  MOM(DIA) < 0: TLT, IEF, FXY
5) Если SMA(DIA) < -0.5%,  MOM(DIA) > 0 OR MOM(TLT) > 0: XLP(0.2), TLT(0.2), IEF(0.2), FXY(0.2)      
6) Ребаланс или 31 числа, или 1 числа. Если инструменты разошлили от весов на N%, то не балансируем 
7) Учесть левередж, так как в 4-ом условии капитал на 0.8
8) Левередж писать так, чтобы учесть внедрение внутридневного VIX/VIX3M. VIX/VIX3M для снижения экспозы или смены порта.  
9) Комисиссии IB-шные

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
        }
'''