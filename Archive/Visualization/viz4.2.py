from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import base64, csv, io, os, json, dash
from io import StringIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        # store whole dataset
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '99%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
        dcc.Store(id='dfs'),
        dcc.Store(id='exps'),
        dcc.Store(id='cytokines'),
        dcc.Store(id='df-columns'),

        # html.Div([
        #     dcc.Dropdown(
        #         placeholder='Choose Cytokine of Interest',
        #         id='x-axis',
        #     ),
        # ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
        dcc.Dropdown(
            placeholder='Choose Cytokine of Interest',
            id='x-axis',
            style={'width': '48%'}
        ),
        dcc.Dropdown(
            placeholder='Choose Variable of Interest',
            id='y-axis',
            style={'width': '48%'}
        ),
        # html.Br(),
        # html.Br(),
        dcc.Graph(id='graph1'),
        # html.Div([
        #     dcc.Dropdown(
        #         placeholder='Choose Variable of Interest',
        #         id='y-axis'
        #     ),
        # ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
        
    ]),
    # html.Br(),
    # html.Br(),
    # dcc.Graph(id='graph1'),
])

def parse_contents(contents, filename):#, date):
    # print(contents)
    _, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    if 'csv' in filename:
        df = pd.read_csv(StringIO(decoded.decode('utf-8')))
    elif 'pkl' in filename:
        df = pd.read_pickle(io.BytesIO(decoded))
    elif 'json' in filename:
        df = pd.read_json(io.BytesIO(decoded))
    return df

@callback(
    Output('dfs', 'data'),
    Output('exps', 'data'),
    Output('cytokines', 'data'),
    Output('df-columns', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),)
    #State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names):
    dfs = {}
    cytokines = []
    df_columns = []
    # if list_of_contents is not None:
    for c, n in zip(list_of_contents, list_of_names):
        tmp = parse_contents(c, n)
        k = n.split('.')[0][0:]
        dfs[k] = tmp.to_json(orient='split', date_format='iso')
        cytokines = tmp['Metadata_Metadata_Cytokine'].unique()
        
        # find the features that the files have in common
        # Reference: https://stackoverflow.com/questions/2864842/common-elements-comparison-between-2-lists        
        # df_columns += list(tmp.columns)
        if len(df_columns) != 0:
            df_columns = list(set(df_columns).intersection(set(tmp.columns)))
        
        # if there is nothing in df_columns yet, we don't want to take the intersection or the result will be empty
        else:
            df_columns = list(tmp.columns)
            
    return json.dumps(dfs), json.dumps(list(dfs.keys())), json.dumps(list(cytokines)), json.dumps(sorted(list(set(df_columns))))


@callback(Output('x-axis', 'options'), Input('cytokines', 'data'))
def update_dropdown(df):
    return df[1:-1].split(', ')

@callback(Output('y-axis', 'options'), Input('df-columns', 'data'))
def update_dropdown(df):
    return df[1:-1].split(', ')

@callback(
    Output('graph1', 'figure'), 
    # Output('graph2', 'figure'), 
    Input('x-axis', 'value'), 
    Input('y-axis', 'value'), 
    Input('dfs', 'data')
    # Input('df', 'data')
    )
def update_graph1(x_axis_name, y_axis_name, dfs):
    dfs = json.loads(dfs)
    # figs = []
    # for k, v in zip(dfs.keys(), dfs.values()):
    #     df = pd.read_json(v, orient='split')
    #     df = df[df['Metadata_Metadata_Cytokine']==x_axis_name[1:-1]]
    #     fig = px.scatter(df, x="Metadata_Metadata_Dose", y=y_axis_name[1:-1],
    #                      title=k)
    #     figs.append(fig)
    y = y_axis_name[1:-1]
    fig = make_subplots(rows=1, cols=len(dfs), 
                        subplot_titles=list(dfs.keys()),
                        shared_yaxes=True, x_title='Dosage Level (log)',
                        y_title=y)
    
    # Reference: https://community.plotly.com/t/how-do-i-remove-legend-trace-from-subplot/59911
    fig.update_layout(showlegend=False)
    
    i = 1
    # l = 100
    # h = 0
    for k, v in zip(dfs.keys(), dfs.values()):
        df = pd.read_json(v, orient='split')
        df = df[df['Metadata_Metadata_Cytokine']==x_axis_name[1:-1]]


        fig.add_scatter(x=np.log(df['Metadata_Metadata_Dose']), y=df[y], 
                        mode="markers", marker=dict(size=5, color="LightSeaGreen"), 
                        row=1, col=i)
        # h = max(h, max(df[y_axis_name[1:-1]]))
        # l = min(l, min(df[y_axis_name[1:-1]]))
        
        i += 1
    fig.update_layout(
        autosize=True,
        height = 500,
        # xaxis_title="Dosage Level (log)",
        # yaxis_title=y_axis_name[1:-1],
        margin=dict(
            l=20,
            r=20,
            b=50,
            t=50,
            pad=4
        ),
        paper_bgcolor="LightSteelBlue",
    )
    # fig.update_yaxes(tick0=0.25, dtick=0.5)
    # fig.update_yaxes(range=[np.floor(l), np.ceil(h)])

    return fig


if __name__ == '__main__':
    app.run(debug=True)
