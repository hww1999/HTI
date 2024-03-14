import base64, csv, io, os, json, dash, sys
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import numpy as np
from io import StringIO
from plotly.colors import n_colors
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State, callback

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)
import src
app = Dash(__name__, use_pages=True, pages_folder="pages")

app.layout = html.Div([
    # html.H1('Multi-page app with Dash Pages'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    html.Div([
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
            multiple=False
        ),
        dcc.Store(id='dfs'),
        dcc.Store(id='cytokines'),
        dcc.Store(id='groups'),
        dcc.Store(id='doses'),
        dcc.Store(id='df-columns'),
    ]),

    dash.page_container
])

def parse_contents(contents, filename):
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
    Output('cytokines', 'data'),
    Output('groups', 'data'),
    Output('doses', 'data'),
    Output('df-columns', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),)
def update_output(data, name):
    dfs = {}
    cytokines = []
    doses = []
    groups = ['Granularity', 'Intensity',
             'Texture_AngularSecondMoment', 
             'Texture_Contrast',
             'RadialDistribution_MeanFrac',
             'RadialDistribution_ZernikeMagnitude',
             'Area'
             ]
    group = []
    tmp = parse_contents(data, name)
    for g in groups:
        if tmp.filter(regex=g, axis=1).columns.tolist():
            group.append(g)
    dfs[name] = tmp.to_json(orient='split', date_format='iso')
    cytokines = tmp['Metadata_Metadata_Cytokine'].unique()
    doses = [str(i) for i in tmp['Metadata_Metadata_Dose'].unique()]
    df_columns = list(tmp.columns)
    return json.dumps(dfs), json.dumps(list(cytokines)), json.dumps(group), json.dumps(list(doses)), json.dumps(sorted(list(set(df_columns))))


if __name__ == '__main__':
    app.run(debug=True)