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
    doses = [int(i[1:-1]) for i in doses]
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
    State('dfs', 'data'),
    prevent_initial_call=True
    )
def update_graph2(c, d, sd, y, dfs):
    dfs = json.loads(dfs)
    annotation = ' (' + str(sd)+' sds away)'
    fig = make_subplots(rows=len(dfs), cols=1, 
                        subplot_titles=list(dfs.keys()),
                        shared_xaxes=True, 
                        x_title=y)
    i = 1
    for k, v in zip(dfs.keys(), dfs.values()):
        data = pd.read_json(v, orient='split')
        data = data[data['Metadata_Metadata_Cytokine']==c]
        df = pd.DataFrame()
        for dose in d:
            df = pd.concat([df, data[data['Metadata_Metadata_Dose']==dose]])

        try:
            wells = df['Metadata_Well'].unique()
            colors = n_colors('rgb(5, 200, 200)', 'rgb(200, 10, 10)', len(wells), colortype='rgb')
            subdata = {}
            for well in wells:
                # subdata[c + ' ' + dose + ' ' + well] = df[df['Metadata_Well']==well]
                curr = df[df['Metadata_Well']==well]
                currdose = curr['Metadata_Metadata_Dose'].iloc[0]
                subdata[c + ' ' + str(currdose) + ' ' + well] = curr
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
        title = y + annotation
    )
    # fig.update(layout_showlegend=False)
    fig.update_traces(orientation='h', side='positive', 
                      width=3, points='outliers')
    fig.update_layout(xaxis_showgrid=False, xaxis_zeroline=False)
    fig.add_vline(x=0, line_width=3, line_dash="dash", line_color="green")

    return fig