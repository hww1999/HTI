from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import os, json


experiments = os.listdir()[:-1]
exps = []
for exp in experiments:
    if exp.startswith('PAM'):
        exps.append(exp)
exp_key = {i:key for i, key in zip(range(len(exps)), exps)}
results = ['', 'Experiment', 'FilteredNuclei', 'Image', 'ObjAllcyto', 
        'ObjCell', 'ObjNuclei', 'ObjPerinucCyto', 'ObjPerinuclear']
results_key = {i:key for i, key in zip(range(len(results)), results)}
dfs = {}

for val in exp_key.values():
    dfs[val] = []
    loc_key = {i:val+'/'+val[:6]+j for i, j in zip(range(len(results)), results)}
    for i in loc_key.keys():
        dfs[val].append(pd.read_csv(loc_key[int(i)]+'.csv'))
k = list(dfs.keys())

app = Dash(__name__)

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                k,
                'PAM194_Keratino_CytoPanel_1',
                id='xaxis-column'
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                results,
                '',
                id='yaxis-column'
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

        # data has to be converted to a string like JSON or base64 encoded binary data for storage
        dcc.Store(id='df'),
        dcc.Store(id='df-columns'),

        html.Br(),

        html.Div([
            dcc.Dropdown(
                id='x-axis'
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='y-axis'
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
        
    ]),
    html.Br(),
    html.Br(),
    dcc.Graph(id='graph1'),
])

@callback(
    Output('df', 'data'),
    Output('df-columns', 'data'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value'),
    )
def obtain_columns(xaxis_column_name, yaxis_column_name):

     # data has to be converted to a string like JSON or base64 encoded binary data for storage
    df = dfs[xaxis_column_name][results.index(yaxis_column_name)]
    df_1 = df[df['Metadata_Plate'] == 'Plate 1']
    df_2 = df[df['Metadata_Plate'] == 'Plate 2']
    df_3 = df[df['Metadata_Plate'] == 'Plate 3']

    datasets = {
        'df_1': df_1.to_json(orient='split', date_format='iso'),
        'df_2': df_2.to_json(orient='split', date_format='iso'),
        'df_3': df_3.to_json(orient='split', date_format='iso'),
    }

    return json.dumps(datasets), json.dumps(list(df.columns)) 
    # df.to_json(date_format='iso', orient='split')

@callback(Output('x-axis', 'options'), Input('df-columns', 'data'))# Input('df-columns', 'data'))
def update_dropdown(df):
    return df[1:-1].split(', ')

@callback(Output('y-axis', 'options'), Input('df-columns', 'data'))
def update_dropdown(df):
    return df[1:-1].split(', ')


# different scatter plots https://plotly.com/python/box-plots/
@callback(
    Output('graph1', 'figure'), 
    Input('x-axis', 'value'), 
    Input('y-axis', 'value'), 
    Input('df', 'data')
    )
def update_graph1(x_axis_name, y_axis_name, df):
    datasets = json.loads(df)
    # datasets = pd.read_json(df, orient='split')
    dff1 = pd.read_json(datasets['df_1'], orient='split')
    dff2 = pd.read_json(datasets['df_2'], orient='split')
    dff3 = pd.read_json(datasets['df_3'], orient='split')

    trace0 = go.Box(x=dff1[x_axis_name[1:-1]], y=dff1[y_axis_name[1:-1]],
                    boxpoints='all', name='Plate_1', marker_size=2)

    trace1 = go.Box(x=dff2[x_axis_name[1:-1]], y=dff2[y_axis_name[1:-1]],
                    boxpoints='all', name='Plate_2', marker_size=2)

    trace2 = go.Box(x=dff3[x_axis_name[1:-1]], y=dff3[y_axis_name[1:-1]],
                    boxpoints='all', name='Plate_3', marker_size=2)

    fig = make_subplots(rows=1, cols=3)

    fig.append_trace(trace0, row = 1, col = 1)
    fig.append_trace(trace1, row = 1, col = 2)
    fig.append_trace(trace2, row = 1, col = 3)
    # add_scatter -> box
    # fig.add_scatter(x=dff1[x_axis_name[1:-1]], y=dff1[y_axis_name[1:-1]], 
    #                 mode="markers", marker=dict(size=2, color="LightSeaGreen"), 
    #                 row=1, col=1)
    
    # fig.add_scatter(x=dff2[x_axis_name[1:-1]], y=dff2[y_axis_name[1:-1]], 
    #                 mode="markers", marker=dict(size=2, color="LightSeaGreen"), 
    #                 row=1, col=2)
    
    # fig.add_scatter(x=dff3[x_axis_name[1:-1]], y=dff3[y_axis_name[1:-1]], opacity=0.5, 
    #                 mode="markers", marker=dict(size=2, color="LightSeaGreen"), 
    #                 row=1, col=3)

    # facet_col
    # https://plotly.com/python/setting-graph-size/
    # fig = px.scatter(datasets, x=x_axis_name[1:-1], y=y_axis_name[1:-1], facet_col="Metadata_Plate",
    #              width=800, height=400)

    # fig.update_layout(height=600, width=800, title_text="Side By Side Subplots")
    # fig.show()

    # df = pd.read_json(df, orient='split')
    # fig = px.scatter(dff, x=x_axis_name[1:-1], y=y_axis_name[1:-1])
    return fig

if __name__ == '__main__':
    app.run(debug=True)