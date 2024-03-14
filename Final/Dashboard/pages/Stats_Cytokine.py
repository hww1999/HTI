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
from src.stats import run_ANOVA_cytokines, cytokine_Tukey_HSD
dash.register_page(__name__)

layout = html.Div([
    html.H1('Statstical Analysis between Cytokines at a given dosage treatment'),
    html.Div('This is our visualization for statstical analysis between cytokines '),
    html.Div([
        dcc.Dropdown(
            placeholder='Select Variable of Interest',
            id='var_cyto',
            style={'width': '48%'}
        ),
        dcc.Dropdown(
            placeholder='Select Dose of Interest',
            id='dose_cyto',
            style={'width': '48%'}
        ),
        html.Br(),
        html.Div('Results from ANOVA test of the cytokines'),
        dash_table.DataTable(
            id='cytokine-anova-table',
        ),
        html.Br(),
        html.Div('Results from Tukey test of the cytokines'),
        dash_table.DataTable(
            id='cytokine-tukey-table',
        ),
        html.Br(),
        dcc.Graph(id='graph6'), 
        ]),
])

@callback(Output('var_cyto', 'options'), Input('df-columns', 'data'))
def update_dropdown(df):
    vars = df[1:-1].split(', ')
    vars = [i[1:-1] for i in vars]
    return sorted(vars)

@callback(Output('dose_cyto', 'options'), Input('doses', 'data'))
def update_dropdown(df):
    doses = df[1:-1].split(', ')
    doses = [eval(i[1:-1]) for i in doses]
    return sorted(doses)

@callback(
    Output('graph6', 'figure'), 
    Output('cytokine-anova-table', 'data'),
    Output('cytokine-tukey-table', 'data'),
    Input('dose_cyto', 'value'),
    Input('var_cyto', 'value'),
    Input('dfs', 'data'),
    prevent_initial_call=True
    )
def update_graph4_box(d, y, dfs):
    dfs = json.loads(dfs)

    for k, v in zip(dfs.keys(), dfs.values()):
        data = pd.read_json(v, orient='split')
        print(data)
        anova_df = run_ANOVA_cytokines(data, y, d)
        tukey_df = cytokine_Tukey_HSD(data, y, d)
        data = data[data['Metadata_Metadata_Dose']==d]
    fig = generate_box(data, 'Metadata_Metadata_Cytokine', y)
    
    return fig, anova_df[0].to_dict('records'), tukey_df.to_dict('records')
