import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from dash import Dash, html, dcc, callback 
from dash.dependencies import Input, Output 


##Data Preprocessing 

df_perinuclear = pd.read_csv('/Users/apple/Desktop/DATA_590/BRI_Capstone/PAM194_Keratino_CytoPanel_1/pam194ObjPerinuclear.csv', 
                            low_memory = False)


df_perinuclear.drop(['Metadata_Date', 'Metadata_FileLocation', 'Metadata_Run' , 'FileName_Actin',
                    'FileName_DNA', 'FileName_DNA2' , 'FileName_Golgi', 'FileName_Mito', 'FileName_NileRed', 
                    'FileName_WGA', 'PathName_Actin', 'PathName_DNA', 'PathName_DNA2', 'PathName_Golgi',
                     'PathName_Mito', 'PathName_NileRed', 'PathName_WGA', 'Metadata_Frame', 
                    'ObjectNumber', 'Metadata_Series'], axis =1, inplace = True)

##Grouping untr-50 and untr observations into untr
# Replace 'untr-50' with 'untr' in the 'Metadata_Metadata_Cytokine' column
df_perinuclear['Metadata_Metadata_Cytokine'] = df_perinuclear['Metadata_Metadata_Cytokine'].replace('untr-50', 'untr')

features_of_interest = df_perinuclear.columns[5:]

# Perform groupby and calculate average
mean_df = df_perinuclear.groupby(['ImageNumber','Metadata_Metadata_Cytokine', 'Metadata_Metadata_Dose',
                                    'Metadata_Plate', 'Metadata_Well'])[features_of_interest].mean().reset_index()

##Function for drawing heatmap 
def heatmap_generator( name_of_cytokine_column = 'Metadata_Metadata_Cytokine', cytokine_of_interest = 'EGF', 
                      columns_of_interest_for_heatmap = 'Granularity', dataframe = mean_df):
    
    '''
    This function helps generate heatmaps and calculate correlation matrix for the dataframe provided to it. 
    
    Arguments:

    - dataframe: the dataframe which is going to be used for finding correlation
    - name_of_cytokine_column: the name of the column which has different cytokine types
    - cytokine_of_interest: the name of the cytokine we are interested to filter the data and evaluate effect on 
    different features 
    - columns_of_interest_for_heatmap: the main attribute we are interested in e.g. Granularity, Intensity etc
    
    Output: 
    
    - Prints heatmap of the selected features and type of cytokine 
    
    Returns: 
    
    - Correlation Matrix 
    '''
    
    
    filtered_dataframe = dataframe[dataframe[name_of_cytokine_column] == 
                                   cytokine_of_interest].drop(['Metadata_Well'], axis = 1)
    
    # Select columns starting with "columns_of_interest_for_heatmap"
    selected_columns = df_perinuclear.filter(regex=f'^{columns_of_interest_for_heatmap}_', axis=1).columns.tolist()
    
    # Append dose to selected columns 
    selected_columns.append('Metadata_Metadata_Dose')
    
    # Calculate the correlation matrix
    corr_matrix = filtered_dataframe[selected_columns].corr()

    # Create a heatmap of the correlation matrix
    #plt.figure(figsize=(10, 8))
    #sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', fmt=".2f", linewidths=.5)
    #plt.title(f"Correlation Matrix Heatmap for the Cytokine: {cytokine_of_interest}")
    #plt.show()
    

    # Create an interactive heatmap with hover text
    fig = px.imshow(corr_matrix,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                labels=dict(color='Correlation'),
                color_continuous_scale='RdBu',
                title=f"Correlation Matrix Heatmap for the Cytokine: {cytokine_of_interest}",
                width=1000, height=1000)

    # Add hover information
    fig.update_traces(hovertemplate='Correlation: %{z:.2f}')

    # Show the interactive heatmap
    #fig.show()

        # Add separation lines between points
    for i in range(len(corr_matrix.columns) - 1):
        fig.add_shape(
            type='line',
            x0=i + 0.5,
            x1=i + 0.5,
            y0=-0.5,
            y1=len(corr_matrix.columns) - 0.5,
            line=dict(color='black', width=1)
        )

        fig.add_shape(
            type='line',
            x0=-0.5,
            x1=len(corr_matrix.columns) - 0.5,
            y0=i + 0.5,
            y1=i + 0.5,
            line=dict(color='black', width=1)
        )
    
    return fig


# Define layout

app = Dash(__name__)
app.layout = html.Div(
    children=[
        html.H1("Heat Map Dashboard", style={"text-align": "center"}),

        # Widget for name_of_cytokine_column
        html.Div([
        html.Label("Select Name of Cytokine Column:"),
        dcc.Dropdown(
            id='name_of_cytokine_column_dropdown',
            #options=[{'label': 'Metadata_Metadata_Cytokine', 'value': 'Metadata_Metadata_Cytokine'}],
            options = mean_df.columns,
            value='Metadata_Metadata_Cytokine',
            disabled=False  # Only one option, so disable the dropdown
        ),

        # Widget for cytokine_of_interest
        html.Label("Select Cytokine of Interest:"),
        dcc.Dropdown(
            id='cytokine_of_interest_dropdown',
            options=[{'label': cytokine, 'value': cytokine} for cytokine in mean_df['Metadata_Metadata_Cytokine'].unique()],
            value='EGF'
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
            value='Granularity'  # Default selected value
        ),
        ]),
        # Output for displaying the heatmap
        dcc.Graph(id='heatmap_output', figure=heatmap_generator())
    ]
    ##add another html.div for a new visualisation
)

#Define callback 
@callback(Output('heatmap_output', 'figure'), [Input('name_of_cytokine_column_dropdown','value'), Input('cytokine_of_interest_dropdown','value'), 
                                            Input('columns_of_interest_dropdown','value')])
def update_heatmap(name_of_cytokine_column_dropdown,cytokine_of_interest_dropdown,columns_of_interest_dropdown):
    return heatmap_generator(name_of_cytokine_column_dropdown,cytokine_of_interest_dropdown,columns_of_interest_dropdown)

if __name__ == "__main__":
    app.run_server(debug=True)



