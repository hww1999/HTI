# Common library packages
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from dash import Dash, html, dcc, callback 
from dash.dependencies import Input, Output, State 
import base64
import io
from io import StringIO
import json
import sys

# Custom Functions
sys.path.append('/home/logan/MSDS/Capstone/HTI/src')
from heatmaps import corr_heatmap_generator

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


# Define layout
app = Dash(__name__)
app.layout = html.Div(
    children=[
        html.H1("Heat Map Dashboard", style={"text-align": "center"}),

        # Widget for name_of_cytokine_column
        html.Div([
        # store whole dataset
        html.Label("Select Data File"),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select File')
            ]),
            style={
                'width': '100%',
                'height': '40px',
                'lineHeight': '40px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '0px'
            },
            # Prevent multiple files from being uploaded
            multiple=False
        ),
        dcc.Store(id='data_store'),
        
        html.Label("Select Name of Cytokine Column:"),
        dcc.Dropdown(
            id='name_of_cytokine_column_dropdown',
            #options=[{'label': 'Metadata_Metadata_Cytokine', 'value': 'Metadata_Metadata_Cytokine'}],
            # value='Metadata_Metadata_Cytokine',
            disabled=False  # Only one option, so disable the dropdown
        ),

        # Widget for cytokine_of_interest
        html.Label("Select Cytokine of Interest:"),
        dcc.Dropdown(
            id='cytokine_of_interest_dropdown',
            # options=[{'label': cytokine, 'value': cytokine} for cytokine in mean_df['Metadata_Metadata_Cytokine'].unique()],
            # value='EGF'
        ),

        # Widget for columns_of_interest_for_heatmap
        html.Label("Select Columns of Interest for Heatmap:"),
        dcc.Dropdown(
            id='columns_of_interest_dropdown',
            options=[
                {'label': 'Granularity', 'value': 'Granularity'},
                {'label': 'Intensity', 'value': 'Intensity'}, 
                {'label': 'RadialDistribution', 'value': 'RadialDistribution'},
                {'label': 'Texture_AngularSecondMoment', 'value': 'Texture_AngularSecondMoment'}, 
                {'label': 'Texture_Contrast', 'value': 'Texture_Contrast'}
            ],
            multi=False,
            # value='Granularity'  # Default selected value
        ),
        ]),
        # Output for displaying the heatmap
        dcc.Graph(id='heatmap_output',
                #   figure=heatmap_generator()
                  )
    ]
    ##add another html.div for a new visualisation
)

#callback for updating the data from the user-selected file
@callback(
    Output('data_store', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_file_selection(data, name):
    
    #parses the data and converts it to a dataframe
    df_data = parse_contents(data, name)
    
    # Danish's Preprocessing for perinuclear
    # df_data.drop(['Metadata_Date', 'Metadata_FileLocation', 'Metadata_Run' , 'FileName_Actin',
    #                 'FileName_DNA', 'FileName_DNA2' , 'FileName_Golgi', 'FileName_Mito', 'FileName_NileRed', 
    #                 'FileName_WGA', 'PathName_Actin', 'PathName_DNA', 'PathName_DNA2', 'PathName_Golgi',
    #                  'PathName_Mito', 'PathName_NileRed', 'PathName_WGA', 'Metadata_Frame', 
    #                 'ObjectNumber', 'Metadata_Series'], axis =1, inplace = True)
    
    # additional preprocessing needed beyond Matthew's
    # df_data.drop(['ObjectNumber', 'Metadata_well'], axis=1, inplace=True)
    
    #Grouping untr-50 and untr observations into untr
    # Replace 'untr-50' with 'untr' in the 'Metadata_Metadata_Cytokine' column
    # df_data['Metadata_Metadata_Cytokine'] = df_data['Metadata_Metadata_Cytokine'].replace('untr-50', 'untr')
    
    # Reference: https://stackoverflow.com/questions/51770485/typeerror-object-of-type-dataframe-is-not-json-serializable
    return json.dumps(df_data.to_json())

# Update cytokine column name selection
@callback(
    Output('name_of_cytokine_column_dropdown', 'options'),
    Input('data_store', 'data')    
)
def update_cyto_col_dropdown(data):
    df_data = pd.read_json(json.loads(data))
    return df_data.columns

# Update Cytokine Selection
@callback(
    Output('cytokine_of_interest_dropdown', 'options'),
    Input('name_of_cytokine_column_dropdown', 'value'),
    State('data_store', 'data')    
)
def update_cyto_dropdown(cytokine_name, data):
    df_data = pd.read_json(json.loads(data))
    cytokine_ls = df_data[cytokine_name].unique()
    return cytokine_ls

@callback(Output('heatmap_output', 'figure'),
          State('data_store', 'data'),
          State('name_of_cytokine_column_dropdown','value'),
          State('cytokine_of_interest_dropdown','value'),
          Input('columns_of_interest_dropdown','value')
          )
def update_heatmap(data, cytokine_column_dropdown_value, cytokine_of_interest_dropdown_value, columns_of_interest_dropdown_value):
    #convert to dataFrame
    df_data = pd.read_json(json.loads(data))
    
    return corr_heatmap_generator(df=df_data, name_of_cytokine_column=cytokine_column_dropdown_value,
                             cytokine_of_interest=cytokine_of_interest_dropdown_value,
                             columns_of_interest_for_heatmap=columns_of_interest_dropdown_value)

if __name__ == "__main__":
    app.run_server(debug=True)



