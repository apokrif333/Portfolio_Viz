from plotly.offline import plot
from plotly import graph_objs as go

import math
import pandas as pd; pd.options.display.max_columns = 20; pd.options.display.max_rows = 100


def create_daily_prices(df: pd.DataFrame):
    yields_list = []
    yields_indexes = []

    df['BAA Yield Close'] = df['BAA Yield Close'].astype('float', copy=False)
    for i in range(6679, len(df)):
        if math.isnan(df['BAA Yield Close'][i]) == False:
            yields_list.append(df['BAA Yield Close'][i])
            yields_indexes.append(i)

    print(yields_list)
    print(yields_indexes)

    for i in range(1, len(yields_list)):
        every_day_add = (yields_list[i] - yields_list[i-1]) / (yields_indexes[i] - yields_indexes[i-1])
        print(every_day_add * 100)

        for j in range(yields_indexes[i-1]+1, yields_indexes[i]):
            df.loc[j, 'BAA Yield Close'] = df['BAA Yield Close'][j-1] + every_day_add

    df.to_csv('Total.csv')


# df.fillna(method='ffill').to_csv('Total.csv')
df = pd.read_csv('Total.csv')

# Das ist Plotly time
trace1 = go.Scatter(
    x=df['Date'],
    y=df['Bond price'],
    mode='lines',
    name='Bond price'
)
trace2 = go.Scatter(
    x=df['Date'],
    y=df['BAA 20+ price'],
    mode='lines',
    name='BAA 20+ price',
    # yaxis='y1'
)
trace3 = go.Scatter(
    x=df['Date'],
    y=df['DJA'],
    mode='lines',
    name='DJA price',
    yaxis='y2'
)
trace4 = go.Scatter(
    x=df['Date'],
    y=df['Effective FED rate'],
    mode='lines',
    name='Effective FED rate',
    yaxis='y3'
)

plt_data = [trace1, trace2, trace3, trace4]

plt_layout = go.Layout(
    title='Compare Stocks and Bonds',
    xaxis=dict(
        domain=[0.04, 1]
    ),
    yaxis=dict(
        title='Bond price',
        titlefont=dict(color='#1f77b4'),
        tickfont=dict(color='#1f77b4')
    ),
    yaxis2=dict(
        title='S&P price',
        titlefont=dict(color='#ff7f0e'),
        tickfont=dict(color='#ff7f0e'),
        type='log',
        autorange=True,
        overlaying='y',
        side='right'
    ),
    yaxis3=dict(
        title='Effective FED rate',
        titlefont=dict(color='#2ca02c'),
        tickfont=dict(color='#2ca02c'),
        overlaying='y',
        side='left',
        position=0.0
    )
)

fig = go.Figure(
    data=plt_data,
    layout=plt_layout
)
plot(fig, show_link=False, filename='Bond and SPY prices.html')
