from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import base64, csv, io, os, json, dash
from io import StringIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd

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

        html.Div([
            dcc.Dropdown(
                id='chosen-exp'
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        dcc.Store(id='df'),
        dcc.Store(id='df-columns'),

        html.Br(),


        html.Div([
            dcc.Dropdown(
                placeholder='choose x-axis',
                id='x-axis'
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
    dcc.Graph(id='graph2'),
    dcc.Graph(id='graph3'),
])

def parse_contents(contents, filename):#, date):
    # print(contents)
    if [contents, filename] == [None, None]:
        return dash.no_update
    _, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    if 'csv' in filename:
        df = pd.read_csv(StringIO(decoded.decode('utf-8')))
    elif 'pkl' in filename:
        df = pd.read_pickle(io.BytesIO(decoded))
    elif 'json' in filename:
        df = pd.read_json(io.BytesIO(decoded))
    return df#.to_json(orient='split', date_format='iso')

@callback(
    Output('dfs', 'data'),
    Output('exps', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),)
    #State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names):
    dfs = {}
    # if list_of_contents is not None:
    for c, n in zip(list_of_contents, list_of_names):
        tmp = parse_contents(c, n)
        k = n.split('.')[0][0:]
        dfs[k] = tmp.to_json(orient='split', date_format='iso')
    return json.dumps(dfs), json.dumps(list(dfs.keys())) 


@callback(Output('chosen-exp', 'options'), Input('exps', 'data'))
def update_dropdown(exps):
    return exps[1:-1].split(', ')


@callback(
    Output('df', 'data'),
    Output('df-columns', 'data'),
    Input('chosen-exp', 'value'),
    Input('dfs', 'data'),
    # Input('yaxis-column', 'value'),
    )
def choose_data(xaxis_column_name, dfs):#yaxis_column_name):
    dfs = json.loads(dfs)
    chosen = xaxis_column_name[1:-1]
     # data has to be converted to a string like JSON or base64 encoded binary data for storage
    df = pd.read_json(dfs[chosen], orient='split')#[results.index(yaxis_column_name)]
    df_1 = df[df['Metadata_Plate'] == 'Plate 1']
    df_2 = df[df['Metadata_Plate'] == 'Plate 2']
    df_3 = df[df['Metadata_Plate'] == 'Plate 3']

    datasets = {
        'df_1': df_1.to_json(orient='split', date_format='iso'),
        'df_2': df_2.to_json(orient='split', date_format='iso'),
        'df_3': df_3.to_json(orient='split', date_format='iso'),
    }

    return json.dumps(datasets), json.dumps(list(df.columns)) 
    # df.to_json(date_format='iso', orient='split')


@callback(Output('x-axis', 'options'), Input('df-columns', 'data'))
def update_dropdown(df):
    return df[1:-1].split(', ')

@callback(Output('y-axis', 'options'), Input('df-columns', 'data'))
def update_dropdown(df):
    return df[1:-1].split(', ')

@callback(
    Output('graph1', 'figure'), 
    Output('graph2', 'figure'), 
    Output('graph3', 'figure'), 
    Input('x-axis', 'value'), 
    Input('y-axis', 'value'), 
    Input('df', 'data')
    # Input('df', 'data')
    )
def update_graph1(x_axis_name, y_axis_name, df):
    datasets = json.loads(df)
    # datasets = pd.read_json(df, orient='split')
    dff1 = pd.read_json(datasets['df_1'], orient='split')
    dff2 = pd.read_json(datasets['df_2'], orient='split')
    dff3 = pd.read_json(datasets['df_3'], orient='split')

    # fig = make_subplots(rows=1, cols=3)

    # fig.add_scatter(x=dff1[x_axis_name[1:-1]], y=dff1[y_axis_name[1:-1]], 
    #                 mode="markers", marker=dict(size=2, color="LightSeaGreen"), 
    #                 row=1, col=1)
    
    # fig.add_scatter(x=dff2[x_axis_name[1:-1]], y=dff2[y_axis_name[1:-1]], 
    #                 mode="markers", marker=dict(size=2, color="LightSeaGreen"), 
    #                 row=1, col=2)
    
    # fig.add_scatter(x=dff3[x_axis_name[1:-1]], y=dff3[y_axis_name[1:-1]], opacity=0.5, 
    #                 mode="markers", marker=dict(size=2, color="LightSeaGreen"), 
    #                 row=1, col=3)

    fig1 = px.scatter(dff1, x=x_axis_name[1:-1], y=y_axis_name[1:-1], facet_col="Metadata_Metadata_Dose")
    fig2 = px.scatter(dff2, x=x_axis_name[1:-1], y=y_axis_name[1:-1], facet_col="Metadata_Metadata_Dose")
    fig3 = px.scatter(dff3, x=x_axis_name[1:-1], y=y_axis_name[1:-1], facet_col="Metadata_Metadata_Dose")
    # facet_col
    # https://plotly.com/python/setting-graph-size/
    # fig = px.scatter(datasets, x=x_axis_name[1:-1], y=y_axis_name[1:-1], facet_col="Metadata_Plate",
    #              width=800, height=400)

    # fig.update_layout(height=600, width=800, title_text="Side By Side Subplots")

    # df = pd.read_json(df, orient='split')
    # fig = px.scatter(dff, x=x_axis_name[1:-1], y=y_axis_name[1:-1])
    return fig1, fig2, fig3


if __name__ == '__main__':
    app.run(debug=True)