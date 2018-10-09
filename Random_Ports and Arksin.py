import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

'''
Исходя из закона Арксинуса и тому, что внутридневные принты случайны, рынок подвержен вечному, случайно сформированному
тренду. Те или иные макро-фундаментальные и экономические события дают случайной направленности однозначное направление 
вверх, которым пользуются инвесторы. Определение и направление этих событий, которые приносят волатильнсоть
позволяют сместить вероятность в пользу спекуянта, при условии, что смещённая вероятность перекроет все 
издержки и сборы, в процессе выполнения данного подхода, а плечи и просадки не уведут депозит к точке невозврата. 
Факт того, что при лонг сделке риск огранице 0, а профит не ограничен 
'''


charts_count = 20
port_positions = 10
days_for_trades = 100

start_capital = 100
max_down = 80  # Максимальная потеря в одной акции
max_profit = 83  # Максимальный профит в одной акции

up_trends = 0
down_trends = 0
for z in range(charts_count):

    dinamic_list = [start_capital]
    for i in range(days_for_trades):

        rand = 0
        for _ in range(port_positions):
            rand += np.random.randint(low=100-max_down, high=100+max_profit) / 100
        rand = rand / port_positions
        dinamic_list.append(dinamic_list[-1] * rand)

    plt.plot(np.arange(1, days_for_trades+2), dinamic_list)
    if dinamic_list[-1] > start_capital:
        up_trends += 1
    else:
        down_trends += 1

print(str(up_trends) + ' | ' + str(down_trends))
plt.show()