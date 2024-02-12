import base64, csv, io, os, json, dash, sys
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import numpy as np
from io import StringIO
from plotly.colors import n_colors
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State, callback
from src.violinPlots import generate_violins
dash.register_page(__name__)

layout = html.Div([
    html.H1('This is our visualization for violins'),
    html.Div('This is our visualization for violins'),
    html.Div([
        dcc.Dropdown(
            placeholder='Select Cytokine of Interest',
            id='cytokine',
            style={'width': '48%'}
        ),
        dcc.Dropdown(
            placeholder='Select Variable of Interest',
            id='var',
            style={'width': '48%'}
        ),
        # dcc.Dropdown(
        #     placeholder='Choose Dose of Interest',
        #     id='dose',
        #     style={'width': '48%'}
        # ),
        html.Br(),
        html.Div('Select Doses of Interest'),
        dcc.Checklist(
            id='dose',
            inline=True
        ),
        html.Div('Select Group by Wells'),
        dcc.Checklist(
            ['Group by Well'],
            id='group_by_well',
            inline=True
        ),
        dcc.Slider(1, 6, 1,
               value=4,
               id='sd'
        ),
        html.Div(id='sd-selected'),
        dcc.Graph(id='graph2'), 
    ]),
])

@callback(Output('cytokine', 'options'), Input('cytokines', 'data'))
def update_dropdown(df):
    cytokines = df[1:-1].split(', ')
    cytokines = [i[1:-1] for i in cytokines]
    return sorted(cytokines)

# @callback(Output('dose', 'options'), Input('doses', 'data'))
# def update_dropdown(df):
#     return df[1:-1].split(', ')
@callback(Output('dose', 'options'), Input('doses', 'data'))
def update_dropdown(df):
    doses = df[1:-1].split(', ')

    doses = [eval(i[1:-1]) for i in doses]
    return sorted(doses)

@callback(Output('var', 'options'), Input('df-columns', 'data'))
def update_dropdown(df):
    vars = df[1:-1].split(', ')
    vars = [i[1:-1] for i in vars]
    return sorted(vars)

@callback(
    Output('sd-selected', 'children'),
    Input('sd', 'value'))
def update_output(value):
    return 'You have selected "{}" standard deviations'.format(value)

@callback(
    Output('graph2', 'figure'), 
    Input('cytokine', 'value'), 
    Input('dose', 'value'), 
    Input('sd', 'value'),
    Input('var', 'value'), 
    Input('group_by_well', 'value'), 
    State('dfs', 'data'),
    prevent_initial_call=True
    )
def update_graph2(c, d, sd, y, group_by_well, dfs):
    dfs = json.loads(dfs)

    for k, v in zip(dfs.keys(), dfs.values()):
        data = pd.read_json(v, orient='split')
        data = data[data['Metadata_Metadata_Cytokine']==c]
        df = pd.DataFrame()
        for dose in d:
            df = pd.concat([df, data[data['Metadata_Metadata_Dose']==dose]])
        subdata = {}
        if group_by_well:
            cd = df.groupby(by=['Metadata_Metadata_Cytokine', 
                                'Metadata_Metadata_Dose',
                                'Metadata_Well'])[y].mean().index
        
            for i in cd:
                # c = i[0]
                d = i[1]
                w = i[2]
                name = c + ' ' + str(d) + ' ' + w
                # curr = df[df['Metadata_Metadata_Cytokine']==c]
                curr = df[df['Metadata_Metadata_Dose']==d]
                subdata[name] = curr[curr['Metadata_Well']==w][y]
        else:
            cd = df.groupby(by=['Metadata_Metadata_Cytokine', 
                                'Metadata_Metadata_Dose'])[y].mean().index
            for i in cd:
                # c = i[0]
                d = i[1]
                name = c + ' ' + str(d)
                # curr = df[df['Metadata_Metadata_Cytokine']==c]
                subdata[name] = df[df['Metadata_Metadata_Dose']==d][y]
        fig = generate_violins(subdata, y, sd)


    return fig
