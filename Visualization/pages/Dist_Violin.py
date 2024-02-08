import base64, csv, io, os, json, dash
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import numpy as np
from io import StringIO
from plotly.colors import n_colors
# from src.ttest_plot import generate_violins, well_ttest
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State, callback

dash.register_page(__name__)

layout = html.Div([
    html.H1('This is our visualization for violins'),
    html.Div('This is our Archive page content.'),
    html.Div([
        dcc.Dropdown(
            placeholder='Choose Cytokine of Interest',
            id='cytokine',
            style={'width': '48%'}
        ),
        dcc.Dropdown(
            placeholder='Choose Dose of Interest',
            id='dose',
            style={'width': '48%'}
        ),
        dcc.Dropdown(
            placeholder='Choose Variable of Interest',
            id='var',
            style={'width': '48%'}
        ),
        dcc.Graph(id='graph2'),
        
    ]),
])

@callback(Output('cytokine', 'options'), Input('cytokines', 'data'))
def update_dropdown(df):
    return df[1:-1].split(', ')

@callback(Output('dose', 'options'), Input('doses', 'data'))
def update_dropdown(df):
    return df[1:-1].split(', ')

@callback(Output('var', 'options'), Input('df-columns', 'data'))
def update_dropdown(df):
    return df[1:-1].split(', ')

@callback(
    Output('graph2', 'figure'), 
    Input('cytokine', 'value'), 
    Input('dose', 'value'), 
    Input('var', 'value'), 
    State('dfs', 'data'),
    prevent_initial_call=True
    )
def update_graph2(c, d, var, dfs):
    dfs = json.loads(dfs)
    y = var[1:-1]
    c = c[1:-1]
    d = d[1:-1]
    sd = 4
    annotation = ' (' + str(sd)+' sds away)'
    fig = make_subplots(rows=len(dfs), cols=1, 
                        subplot_titles=list(dfs.keys()),
                        shared_xaxes=True, 
                        x_title=y)
    i = 1
    for k, v in zip(dfs.keys(), dfs.values()):
        df = pd.read_json(v, orient='split')
        df = df[df['Metadata_Metadata_Cytokine']==c][df['Metadata_Metadata_Dose']==int(d)]

        try:
            colors = n_colors('rgb(5, 200, 200)', 'rgb(200, 10, 10)', 2, colortype='rgb')
            wells = df['Metadata_Well'].unique()
            subdata = {}
            for well in wells:
                subdata[c + ' ' + str(d) + ' ' + well] = df[df['Metadata_Well']==well]
            for data_line, color in zip(subdata.keys(), colors):
                x = subdata[data_line][y]
                    
                fig.append_trace(go.Violin(x=x, line_color=color, 
                                        name=data_line), row = i, col = 1)
                
                m = np.mean(x)
                std = np.std(x)
                l = m-sd*std
                r = m+sd*std
                if r <= max(x):
                    fig.add_vline(x=r, line_dash="dash", line_color=color, row=i, col=1)
                if l >= min(x):
                    fig.add_vline(x=l, line_dash="dash", line_color=color, row=i, col=1)
            # fig.append_trace(trace0, row = 1, col = i)
        except:
            pass
        
        i += 1

    fig.update_layout(
        autosize=True,
        height = 400 * len(dfs),
        margin=dict(
            l=20,
            r=20,
            b=50,
            t=50,
            pad=4
        ),
        paper_bgcolor="LightSteelBlue",
        title = var + annotation
    )
    fig.update(layout_showlegend=False)
    fig.update_traces(orientation='h', side='positive', 
                      width=3, points='outliers')
    fig.update_layout(xaxis_showgrid=False, xaxis_zeroline=False)
    fig.add_vline(x=0, line_width=3, line_dash="dash", line_color="green")

    return fig