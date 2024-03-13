import plotly.express as px
import pandas as pd

def treatment_profiles_heatmap(data, non_numeric_cols=['Metadata_Metadata_Cytokine', 'Metadata_Metadata_Dose', 'ImageNumber', 'ObjectNumber',
                          'Metadata_Plate', 'Metadata_Well']):
    '''
    The function aggregates data to create a summary of each treatment combination of cytokine and dosage, and 
    a heatmap showing the similarity between treatment profiles.
    
    Inputs: 
    1. data: type(DataFrame), The data that will be aggregated.
    2. non_numeric_cols: type(list), Contains a list of the non-numerical columns of the dataframe so that
    the function can avoid taking the median of them when performing the group by. These features will be dropped.

    Returns: 
    1. fig: returns the Plotly object representing the heatmap    
    '''
    
    df_data = data
    # merge cytokine and dose
    # Reference: https://stackoverflow.com/questions/19377969/combine-two-columns-of-text-in-pandas-dataframe
    df_data['Cytokine_and_Dose'] = df_data['Metadata_Metadata_Cytokine'] + "-" + df_data['Metadata_Metadata_Dose'].astype(str)
    
    # drop non_numeric columns
    df_data.drop(columns=non_numeric_cols, inplace=True)
    
    df_data_medians = df_data.groupby(['Cytokine_and_Dose']).median()

    # Need transpose because correlation is computed on columns
    df_data_medians_T = df_data_medians.T

    # Compute Correlation
    corr_matrix = df_data_medians_T.corr(method='pearson')
    
    # Create an interactive heatmap with hover text
    fig = px.imshow(corr_matrix,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                labels=dict(color='Correlation'),
                color_continuous_scale='RdBu_r',
                title=f"Correlation Matrix Heatmap for the Cytokine Aggregate Profiles",
                width=1000, height=1000)
    
    # Add hover information
    fig.update_traces(hovertemplate='Correlation: %{z:.2f}')
    
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