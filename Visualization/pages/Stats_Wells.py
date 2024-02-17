import base64, csv, io, os, json, dash, sys
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import numpy as np
from io import StringIO
from plotly.colors import n_colors
from plotly.subplots import make_subplots
from dash import dash_table, dcc, html, Input, Output, State, callback
from src.violinPlots import generate_violins, generate_box
from src.stats_eda import get_ttest_wells_d, plot_by_wells_d
dash.register_page(__name__)

layout = html.Div([
    html.H1('Statstical Analysis between Wells'),
    html.Div('This is our visualization for statstical analysis between wells'),
    html.Div([
        dcc.Dropdown(
            placeholder='Select Cytokine of Interest',
            id='cytokine_stat',
            style={'width': '48%'}
        ),
        dcc.Dropdown(
            placeholder='Select Variable of Interest',
            id='var_stat',
            style={'width': '48%'}
        ),
        dcc.Dropdown(
            placeholder='Choose Dose of Interest',
            id='dose_stat',
            style={'width': '48%'}
        ),
        html.Div('Results from T-test of the two wells'),
        dash_table.DataTable(
            id='well-ttest-table',
        ),
        html.Br(),
        dcc.Graph(id='graph3'), 
        ]),
])

@callback(Output('cytokine_stat', 'options'), Input('cytokines', 'data'))
def update_dropdown(df):
    cytokines = df[1:-1].split(', ')
    cytokines = [i[1:-1] for i in cytokines]
    return sorted(cytokines)

# @callback(Output('dose', 'options'), Input('doses', 'data'))
# def update_dropdown(df):
#     return df[1:-1].split(', ')
@callback(Output('dose_stat', 'options'), Input('doses', 'data'))
def update_dropdown(df):
    doses = df[1:-1].split(', ')
    doses = [eval(i[1:-1]) for i in doses]
    return sorted(doses)

@callback(Output('var_stat', 'options'), Input('df-columns', 'data'))
def update_dropdown(df):
    vars = df[1:-1].split(', ')
    vars = [i[1:-1] for i in vars]
    return sorted(vars)

# @callback(
#     Output('graph3', 'figure'), 
#     Input('cytokine_stat', 'value'), 
#     Input('dose_stat', 'value'), 
#     Input('var_stat', 'value'), 
#     State('dfs', 'data'),
#     prevent_initial_call=True
#     )
# def update_graph3_violin(c, d, y, dfs):
#     dfs = json.loads(dfs)

#     for k, v in zip(dfs.keys(), dfs.values()):
#         data = pd.read_json(v, orient='split')
#         data = data[data['Metadata_Metadata_Cytokine']==c][data['Metadata_Metadata_Dose']==d]
#         subdata = {}
#         cd = data.groupby(by=['Metadata_Metadata_Cytokine', 
#                             'Metadata_Metadata_Dose',
#                             'Metadata_Well'])[y].mean().index
        
#         for i in cd:
#             w = i[2]
#             name = c + ' ' + str(d) + ' ' + w
#             # curr = df[df['Metadata_Metadata_Cytokine']==c]
#             # curr = data[data['Metadata_Metadata_Dose']==d]
#             subdata[name] = data[data['Metadata_Well']==w][y]
#         fig = generate_violins(subdata, y, sd=0)

#     return fig

@callback(
    Output('graph3', 'figure'), 
    Output('well-ttest-table', 'data'),
    Input('cytokine_stat', 'value'), 
    Input('dose_stat', 'value'), 
    Input('var_stat', 'value'), 
    State('dfs', 'data'),
    prevent_initial_call=True
    )
def update_graph3_box(c, d, y, dfs):
    dfs = json.loads(dfs)

    for k, v in zip(dfs.keys(), dfs.values()):
        data = pd.read_json(v, orient='split')
        data = data[data['Metadata_Metadata_Cytokine']==c]
        data = data[data['Metadata_Metadata_Dose']==d]
    fig = generate_box(data, 'Metadata_Well', y)
    text_df = get_ttest_wells_d(c, d, y, data)
    # text_df = text_df.to_dict('records')
    return fig, text_df.to_dict('records')

    # OSError: [WinError 10038]
    # fig = plot_by_wells_d(c, d, y, data)