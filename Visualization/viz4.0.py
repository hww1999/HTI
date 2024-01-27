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
                'width': '100%',
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
        #         id='chosen-exp'
        #     ),
        # ], style={'width': '48%', 'display': 'inline-block'}),

        # dcc.Store(id='df'),
        

        html.Br(),


        html.Div([
            dcc.Dropdown(
                placeholder='choose x-axis',
                id='x-axis',
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                placeholder='choose y_axis',
                id='y-axis'
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
        
    ]),
    html.Br(),
    html.Br(),
    dcc.Graph(id='graph1'),
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
        df_columns += list(tmp.columns)
    return json.dumps(dfs), json.dumps(list(dfs.keys())), json.dumps(list(cytokines)), json.dumps(list(set(df_columns)))


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

    fig = make_subplots(rows=len(dfs), cols=1, subplot_titles=list(dfs.keys()))
    i = 1
    l = 100
    h = 0
    for k, v in zip(dfs.keys(), dfs.values()):
        df = pd.read_json(v, orient='split')
        df = df[df['Metadata_Metadata_Cytokine']==x_axis_name[1:-1]]


        fig.add_scatter(x=np.log(df['Metadata_Metadata_Dose']), y=df[y_axis_name[1:-1]], 
                        mode="markers", marker=dict(size=5, color="LightSeaGreen"), 
                        row=i, col=1)
        h = max(h, max(df[y_axis_name[1:-1]]))
        l = min(l, min(df[y_axis_name[1:-1]]))
        
        i += 1
    fig.update_layout(
        autosize=True,
        height = 500 * len(dfs),
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
    fig.update_yaxes(range=[np.floor(l), np.ceil(h)])

    return fig


if __name__ == '__main__':
    app.run(debug=True)
