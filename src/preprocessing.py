import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import warnings
import sys
sys.path.append('../src/')
warnings.filterwarnings('ignore')

def drop_columns(data):
    data.drop(list(data.filter(regex = 'FileName_')), axis=1, inplace=True) # Dropping all of the columns starting with 'FileName_'
    data.drop(list(data.filter(regex = 'PathName_')), axis=1, inplace=True) # Dropping all of the columns starting with 'PathName_'
    data.drop(['Metadata_Date', 'Metadata_FileLocation', 'Metadata_Frame',
              'Metadata_Run', 'Metadata_Series'], axis=1, inplace=True)
    
def replace_NA(data):
    measurements = data.iloc[:,6:].columns # since we know which columns we're dropping, should this subset be fixed?
    for measure in measurements:
        if data[measure].isna().any():
            data[measure].fillna(data[measure].mean(), inplace=True)
            
# Decide with team whether we have a consistent threshold/SD or leave it to user
            
def replace_outliers_with_sd(df, feature, c, d, w, n):
    sub_df= df[df['Metadata_Metadata_Cytokine']==c]
    sub_df = sub_df[sub_df['Metadata_Metadata_Dose']==d]
    sub_df = sub_df[sub_df['Metadata_Well']==w]
    sub_df = sub_df[feature]
    m = np.mean(sub_df)
    sd = np.std(sub_df)
    bool_col = (sub_df < (m - n * sd)) | (sub_df > (m + n * sd))
    return bool_col

def outlier_detection(df, sd, thresh):
    df_copy = df.copy()
    features = df_copy.columns[6:]

    threshold = round(thresh * len(features))

    # Preferable to groupby as this maintains the unique combination of cytokine, dose, and well in the same 
    # order as they appear in the original dataframe
    unique_pairs = df_copy[['Metadata_Metadata_Cytokine', 
                           'Metadata_Metadata_Dose', 
                           'Metadata_Well']].drop_duplicates().reset_index(drop=True)
    
    # This final outlier dataset will contain the outliers for all cytokines and their respective doses and wells
    all_outliers = pd.DataFrame()
    
    # loop through each specific cytokine, dose, and well combination in the specific order that they're in 
    # the original dataframe
    for i, row in unique_pairs.iterrows():
        
        # This outlier dataset will be used to find outliers for each specific cytokine, dose treatment, and well
        # for all features. 
        outlier_cols = pd.DataFrame()

        cytokine = row[0]
        dose = row[1]
        well = row[2]

        # again, this is calculating the outliers for each specific cytokine, dose, and well in
        # the same order they appear in the original dataframe. 
        for feature in features:
            test = replace_outliers_with_sd(df_copy, feature, cytokine, dose, well, sd)
            col_name = feature + '_outliers'
            outlier_cols.loc[:, col_name] = test

        all_outliers = pd.concat([all_outliers, outlier_cols])

    # get the sum value where an image is an outlier for each feature (i.e True from the above function)  
    cols = all_outliers.columns
    df['Outlier_Count'] = (all_outliers[cols] == True).sum(1)

    # Get the images that have outliers that exceed our threshold and those that don't
    outliers = df[df['Outlier_Count'] >= threshold]
    sub_data = df[df['Outlier_Count'] < threshold]
    
    # Drop the outlier count columns in both datasets
    outliers.drop(['Outlier_Count'], axis=1, inplace=True)
    sub_data.drop(['Outlier_Count'], axis=1, inplace=True)
    
    # I'm only returning the outliers for the team to show our sponsors which images are outliers. 
    # We can remove this part of the function in our final product. 
    return outliers, sub_data


