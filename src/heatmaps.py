# Imports
import plotly.express as px
import numpy as np
import pandas as pd

# FUNCTIONS

#Function for drawing heatmap 
def corr_heatmap_generator(df, groupby_cols = ['ImageNumber','Metadata_Metadata_Cytokine', 'Metadata_Metadata_Dose',
                                        'Metadata_Plate', 'Metadata_Well'],
                           name_of_cytokine_column = 'Metadata_Metadata_Cytokine', cytokine_of_interest = 'EGF', 
                      columns_of_interest_for_heatmap = 'Granularity'):
    
    '''
    This function helps generate heatmaps and calculate correlation matrix for the dataframe provided to it. 
    
    Arguments:

    - dataframe: the dataframe which is going to be used for finding correlation. Note: all columns in
    this dataframe that are not numerical must be listed in the groupby_cols argumnent,
    as the function will perform a groupby and take the mean of all other features.
    - groupby_cols: a list of the column names of the dataframe that you wish to groupby
    - name_of_cytokine_column: the name of the column which has different cytokine types
    - cytokine_of_interest: the name of the cytokine we wish to filter the data by
    and evaluate its effect on different features 
    - columns_of_interest_for_heatmap: the main attribute we are interested in, e.g. 'Granularity',
    'Intensity', etc. It selects all features that begin with the provided argument.
    
    Returns: 
    
    - Plotly figure object
    '''
    # get the remaining columns
    # Reference: https://stackoverflow.com/questions/3428536/how-do-i-subtract-one-list-from-another
    all_cols = df.columns.to_list()
    features_of_interest = [elt for elt in all_cols if elt not in groupby_cols]
    
    # Perform groupby and calculate average
    df = df.groupby(groupby_cols)[features_of_interest].mean().reset_index()
    
    # Select columns starting with columns_of_interest_for_heatmap
    selected_columns = df.filter(regex=f'^{columns_of_interest_for_heatmap}_', axis=1).columns.tolist()
    
    # Append dose to selected columns 
    selected_columns.append('Metadata_Metadata_Dose')
    
    # Calculate the correlation matrix
    corr_matrix = df[selected_columns].corr()

    # Create an interactive heatmap with hover text
    fig = px.imshow(corr_matrix,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                labels=dict(color='Correlation'),
                color_continuous_scale='RdBu_r',
                title=f"Correlation Matrix Heatmap for the Cytokine: {cytokine_of_interest}",
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

def corr_pairs(df):
    '''
    This function computes the pair-wise correlation between the features of a dataframe
    
    Arguments:

    - df: the dataframe containing the data you wish to compute the correlation for
    
    Returns: 
    
    - Pandas DataFrame containing the correlation values for each pair of features
    
    Notes: 
    - This function will return values of NaN for pair-wise correlation involving a feature
    with no variance in the dataset
    -  This function ignores non-numeric features in the provided df
    '''
    # compute correlation
    corr_df = df.corr(numeric_only=True)
    
    # reshape the data into a single column
    corr_array = corr_df.to_numpy()
    corr_array = np.reshape(a=corr_array, newshape=(-1, 1))
    
    feature_names = corr_df.columns.to_list()
    
    num_features = len(feature_names)
    new_df_rows = []
    corr_idx = 0
    
    # construct rows of new dataframe
    for i in range(num_features):
        for j in range(num_features):

            if i == j: # we can throw out the entries for the correlation of a feature with itself
                corr_idx += 1
            else: #construct a row
                corr_value = corr_array[corr_idx]
                # Reference: https://stackoverflow.com/questions/8220702/how-to-fix-typeerror-int-object-is-not-subscriptable
                new_row = [feature_names[i], feature_names[j], corr_value[0]]
                new_df_rows.append(new_row)
                
                corr_idx += 1
    
    # combine rows into new dataframe
    pairwise_df = pd.DataFrame(data=new_df_rows, columns=['Feature_1', 'Feature_2', 'Correlation'])
    
    return pairwise_df