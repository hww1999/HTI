import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA 
from sklearn.model_selection import train_test_split
from typing import Optional, Union

#FUNCTIONS

##Function 1 
def principal_component_analysis(data, number_of_components = 10, 
                                 columns_to_drop: Optional[list] = None, number_of_column: Optional[int] = None, 
                                 columns_to_keep: Optional[list] = None):
    
    '''
    The function performs principal component analysis on the provided dataset. It can take inputs for columns of 
    interest in various forms
    
    Inputs: 
    1. data: type(DataFrame), The main dataframe on which PCA has to be performed 
    2. number_of_components: type(int), This is the number of components which will be used for doing PCA
    Note: 
    For the below three inputs only providing 1 is sufficient 
    3. columns_to_drop: type(list), provide the name of all columns to be dropped in a list 
    4. number_of_column: type(int), this is the number of column including and after which we want to keep all 
    variables for PCA. 
    5. columns_to_keep: type(list), provide the name of all columns to keep in a list  

    Returns: 
    1. pca: returns the entire PCA Object 
    2. relevant_columns: returns the columns used in the principal component analysis
    
    '''
    
    if columns_to_drop is not None: 
        relevant_dataset = data.drop(columns_to_drop, axis = 1)
    elif number_of_column is not None: 
        all_columns = data.columns
        relevant_columns = all_columns[number_of_column:]
        relevant_dataset = data[relevant_columns]
    elif columns_to_keep is not None: 
        relevant_dataset = data[columns_to_keep]
    else:
        raise ValueError("One of 'columns_to_drop', 'number_of_column', or 'columns_to_keep' must be provided.")
        
        
    # Data Cleaning for now won't be needed afterwards
    relevant_dataset.dropna(inplace = True)
    
    
    #Scale the input variables 
    
    #Scale the data 
    scaler = MinMaxScaler()

    # Apply Min-Max scaling to selected columns
    relevant_dataset_scaled = scaler.fit_transform(relevant_dataset) 
    
    #Perform PCA 
    
    # Perform PCA on the scaled dataset
    pca = PCA(n_components = number_of_components)
    # Fit PCA on the standardized data
    principal_components = pca.fit_transform(relevant_dataset_scaled)
    
    return pca, relevant_columns

## Function 2 
def view_principal_components(pca_object, columns_used_for_pca, number_of_components):

    '''
    This functions assists in viewing the weights of the principal components. A new column is added to the display which calculates the 
    absolute sum of the weights across all components and sorts by that column in descending column. 

    Inputs: 
    1. pca_object: the entire principal component object 
    2. columns_used: the original columns used for pca 
    3. number_of_components: the number of components used for the principal component analysis for which the object is passed in 

    Output:
    1. fig: A heatmap of the weights matrix 
    2. weights_df_transposed: The dataframe of weights transposed
    '''
    
    weights_df = pd.DataFrame(pca_object.components_,columns=columns_used_for_pca)
    weights_df_transposed = weights_df.T
    weights_df_transposed['sum_of_abs_weights'] = weights_df_transposed.abs().sum(axis=1)
    
    weights_df_transposed.sort_values(by='sum_of_abs_weights', ascending=False, inplace = True)
    xlabels = [f'PC{i}' for i in range(1,number_of_components+1)] 
    xlabels.append('TC')
    
    # Create a transposed heatmap of the weights
    plt.figure(figsize=(10, 100))
    sns.heatmap(weights_df_transposed, annot=True, cmap='coolwarm', fmt=".2f", 
                xticklabels=xlabels, 
                yticklabels=weights_df_transposed.reset_index()['index'].values)
    plt.title("Weights of Features in Principal Components (Transposed)")
    fig = plt.gcf()
    return fig, weights_df_transposed
    

#Function 3 
def get_features_below_threshold(dataframe, threshold):  
    # Drop features below the threshold
    filtered_dataframe = dataframe[dataframe['sum_of_abs_weights'] >= threshold].reset_index()

    return filtered_dataframe['index'].values

#Function 4 
def plot_variance_explained(pca_object, title="Variance Explained by Principal Components"):

    '''
    This function returns a graph showing variance explained by each principal component using a bar chart and a line chart to express 
    cummulative variance explained by additional principal components.

    Inputs: 
    1. pca_object: takes the original pca object to extract relevant attributes 
    2. titles: type(string), Optional, the title for the graph 

    Outputs:
    Prints the graph 
    '''
    # Get the percentage of variance explained by each principal component
    variance_explained_ratio = pca_object.explained_variance_ratio_

    # Calculate the cumulative variance explained
    cumulative_variance_explained = variance_explained_ratio.cumsum()

    # Plot both bar chart and line chart on the same graph
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = 'tab:blue'
    ax1.set_xlabel('Principal Components')
    ax1.set_ylabel('Percentage Variance Explained', color=color)
    
    # Plot bar chart for percentage variance explained by each PC
    ax1.bar(range(1, len(variance_explained_ratio) + 1), variance_explained_ratio * 100, color=color, label='Individual PC')
    ax1.tick_params(axis='y', labelcolor=color)
    
    # Create a second y-axis for cumulative variance explained
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Cumulative Variance Explained', color=color)
    
    # Plot line chart for cumulative variance explained
    ax2.plot(range(1, len(cumulative_variance_explained) + 1), cumulative_variance_explained * 100, color=color, label='Cumulative')
    ax2.tick_params(axis='y', labelcolor=color)

    # Set titles and legends
    plt.title(title)
    fig.tight_layout()
    fig.legend(loc='upper right')
    
    # Show the plot
    plt.show()

def return_csv(dataframe, file_path):
    '''
    This function takes in a dataframe and filepath and stores it to a csv file.
    '''
    return dataframe.to_csv(file_path)

