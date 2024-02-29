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
from src.stats import run_ANOVA_doses, doses_Tukey_HSD
dash.register_page(__name__)

layout = html.Div([
    html.H1('Statstical Analysis between Doses for a given Cytokine'),
    html.Div('This is our visualization for statstical analysis between doses '),
    html.Div([
        dcc.Dropdown(
            placeholder='Select Cytokine of Interest',
            id='cyto_dose',
            style={'width': '48%'}
        ),
        dcc.Dropdown(
            placeholder='Select Variable of Interest',
            id='var_dose',
            style={'width': '48%'}
        ),
        html.Br(),
        html.Div('Results from ANOVA test of the doses'),
        dash_table.DataTable(
            id='dose-anova-table',
        ),
        html.Br(),
        html.Div('Results from Tukey test of the doses'),
        dash_table.DataTable(
            id='dose-tukey-table',
        ),
        html.Br(),
        dcc.Graph(id='graph5'), 
        ]),
])

@callback(Output('cyto_dose', 'options'), Input('cytokines', 'data'))
def update_dropdown(df):
    cytokines = df[1:-1].split(', ')
    cytokines = [i[1:-1] for i in cytokines]
    return sorted(cytokines)

@callback(Output('var_dose', 'options'), Input('df-columns', 'data'))
def update_dropdown(df):
    vars = df[1:-1].split(', ')
    vars = [i[1:-1] for i in vars]
    return sorted(vars)


@callback(
    Output('graph5', 'figure'), 
    Output('dose-anova-table', 'data'),
    Output('dose-tukey-table', 'data'),
    Input('cyto_dose', 'value'), 
    Input('var_dose', 'value'), 
    Input('dfs', 'data'),
    prevent_initial_call=True
    )
def update_graph4_box(c, y, dfs):
    dfs = json.loads(dfs)

    for k, v in zip(dfs.keys(), dfs.values()):
        data = pd.read_json(v, orient='split')
    anova_df = run_ANOVA_doses(c, y, data)
    tukey_df = doses_Tukey_HSD(c, y, data)
    data = data[data['Metadata_Metadata_Cytokine']==c]
    fig = generate_box(data, 'Metadata_Metadata_Dose', y)
    # tukey_df = tukey_df.summary()
    # tukey_df = pd.DataFrame.from_records(tukey_df.data)
    # new_header = tukey_df.iloc[0] #grab the first row for the header
    # tukey_df = tukey_df[1:] #take the data less the header row
    # tukey_df.columns = new_header
    
    return fig, anova_df[0].to_dict('records'), tukey_df.to_dict('records')
