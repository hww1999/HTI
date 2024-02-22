import base64, csv, io, os, json, dash, sys
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import numpy as np
from io import StringIO
from plotly.colors import n_colors
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State, callback
from src.heatmaps import corr_heatmap_generator
dash.register_page(__name__)

layout = html.Div([
    html.H1('This is our heatmap of correlations'),
    html.Div('This is our heatmap of correlations'),
    html.Div([
        dcc.Dropdown(
            placeholder='Choose Cytokine of Interest',
            id='cytokine1',
            style={'width': '48%'}
        ),
        dcc.Dropdown(
            placeholder='Choose Group of Variables of Interest',
            id='group',
            style={'width': '48%'}
        ),
        dcc.Graph(id='heatmap_output'),
        
    ]),
])

@callback(Output('cytokine1', 'options'), Input('cytokines', 'data'))
def update_dropdown(df):
    cytokines = df[1:-1].split(', ')
    cytokines = [i[1:-1] for i in cytokines]
    return sorted(cytokines)
    # return df[1:-1].split(', ')

@callback(Output('group', 'options'), Input('groups', 'data'))
def update_dropdown(df):
    groups = df[1:-1].split(', ')
    groups = [i[1:-1] for i in groups]
    return sorted(groups)
    # return df[1:-1].split(', ')

@callback(Output('heatmap_output', 'figure'),
          State('dfs', 'data'),
          State('cytokine1','value'),
          Input('group','value')
          )
def update_heatmap(data, cytokine_of_interest_dropdown_value, group):
    #convert to dataFrame
    df_data = json.loads(data)
    for k, v in zip(df_data.keys(), df_data.values()):
        df = pd.read_json(v, orient='split')
        fig = corr_heatmap_generator(df, groupby_cols = ['ImageNumber','Metadata_Metadata_Cytokine', 'Metadata_Metadata_Dose',
                                        'Metadata_Plate', 'Metadata_Well'], name_of_cytokine_column = 'Metadata_Metadata_Cytokine', 
                                cytokine_of_interest = cytokine_of_interest_dropdown_value, 
                                columns_of_interest_for_heatmap = group)
    return fig
