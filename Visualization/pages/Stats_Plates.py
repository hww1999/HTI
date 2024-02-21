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
from src.stats import run_ANOVA_plates, plate_Tukey_HSD
dash.register_page(__name__)

layout = html.Div([
    html.H1('Statstical Analysis between Plates'),
    html.Div('This is our visualization for statstical analysis between plates'),
    html.Div([
        dcc.Dropdown(
            placeholder='Select Variable of Interest',
            id='var_plate',
            style={'width': '48%'}
        ),
        html.Br(),
        html.Div('Results from ANOVA test of the plates'),
        dash_table.DataTable(
            id='plate-anova-table',
        ),
        html.Br(),
        html.Div('Results from Tukey test of the plates'),
        dash_table.DataTable(
            id='plate-tukey-table',
        ),
        html.Br(),
        dcc.Graph(id='graph_plate'), 
        ]),
])

@callback(Output('var_plate', 'options'), Input('df-columns', 'data'))
def update_dropdown(df):
    vars = df[1:-1].split(', ')
    vars = [i[1:-1] for i in vars]
    return sorted(vars)

@callback(
    Output('graph_plate', 'figure'), 
    Output('plate-anova-table', 'data'),
    Output('plate-tukey-table', 'data'),
    # Input('cytokine_stat', 'value'), 
    # Input('dose_stat', 'value'), 
    Input('var_plate', 'value'), 
    State('dfs', 'data'),
    prevent_initial_call=True
    )
def update_graph4_box(y, dfs):
    dfs = json.loads(dfs)

    for k, v in zip(dfs.keys(), dfs.values()):
        data = pd.read_json(v, orient='split')
        anova_df = run_ANOVA_plates('untr', y, data)
        tukey_df = plate_Tukey_HSD('untr', y, data)
        data = data[data['Metadata_Metadata_Cytokine']=='untr']
    fig = generate_box(data, 'Metadata_Plate', y)
    tukey_df = tukey_df.summary()
    tukey_df = pd.DataFrame.from_records(tukey_df.data)
    new_header = tukey_df.iloc[0] #grab the first row for the header
    tukey_df = tukey_df[1:] #take the data less the header row
    tukey_df.columns = new_header
    
    return fig, anova_df[0].to_dict('records'), tukey_df.to_dict('records')
