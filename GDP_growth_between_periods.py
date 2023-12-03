import json
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests
import pandas as pd


def chunk_list(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]

def growth_with_labels(numbers, labels_data):
    growth_rates = [0]
    labels = ['']

    # calculate growth
    for i in range(1, len(numbers)):
        growth_rate = ((numbers[i] - numbers[i-1]) / numbers[i-1]) * 100
        growth_rates.append(growth_rate)

    # create list with lables
    for y in range(1, len(labels_data)):
        lable = labels_data[y], labels_data[y-1]
        labels.append(' vs '.join(lable))

    return growth_rates, labels

# collecting data
URL = 'https://api.worldbank.org/v2/countries/USA/indicators/NY.GDP.MKTP.CD?pages=2&per_page=500&format=json'
r = requests.get(URL)
data = json.loads(r.text)

years = [entry['date'] for entry in data[1]]
value = [entry['value'] for entry in data[1]]

df_gdp = pd.DataFrame(
   { 'Years': years[::-1],
    'Values': value[::-1]}
)

# Dash part
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
html.Div(
    style={'backgroundColor': 'black', 'color': '#FFFF'},
    children=[
    html.H1("GDP Growth rate in %"),

    dcc.Slider(
        id='slider', min=1, max=10, step=1,
        marks={i: str(i) for i in range(1, 10)},
        value=1
    ),
    dcc.Graph(id='period_plot')]),

    html.Div([
        html.H2("GDP Values over the years"),
        dcc.Graph(
            id='gdp_years',
            
            figure=px.line(df_gdp, x='Years', y='Values', template='plotly_dark')
        )
    ], style={'backgroundColor': 'black', 'color': '#FFFF'},)

])

@app.callback(
    Output('period_plot', 'figure'),
    [Input('slider', 'value')]
)
def update_plot(selected_value):

    def calculate_growth(year_period):

        year_chunks = chunk_list(years, year_period)
        value_chunks = chunk_list(value, year_period)

        X = []
        Y = []

        # create lables
        for y_ch in year_chunks:
            if len(y_ch) > 1 or year_period == 1:
                X.append('+'.join(y_ch))

        # sum years data
        for x_ch in value_chunks:
            if len(x_ch) > 1 or year_period == 1:
                Y.append(sum(x_ch))

        # reverse lists
        X = X[::-1]
        Y = Y[::-1]

        r_Y, r_X = growth_with_labels(Y, X)

        return r_X, r_Y


    filtered_df = calculate_growth(selected_value)

    # Sample data
    df = pd.DataFrame({
        'year': filtered_df[0],
        'value': filtered_df[1]
    })

    # Plotly Express plot
    fig = px.bar(df, x='year', y='value', text=df['value'].apply(lambda x: f'{x:.2f}%'), title=f'Filtered Data (years period: {selected_value} vs {selected_value})', labels={
                     "year": "Years",
                     "value": "Growth Between Periods",
                 },)
    fig.update_layout(template='plotly_dark')
    return fig


if __name__ == '__main__':
    app.run_server(debug=False)
