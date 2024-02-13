import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns
from statsmodels.stats.power import TTestIndPower
from statsmodels.stats.power import TTestPower
from scipy.stats import f_oneway
from scipy import stats
from statsmodels.stats.power import FTestAnovaPower
from statsmodels.stats.multicomp import pairwise_tukeyhsd

def replace_column_outliers(df, feature, c, d, w):
    sub_df= df[df['Metadata_Metadata_Cytokine']==c]
    sub_df = sub_df[sub_df['Metadata_Metadata_Dose']==d]
    sub_df = sub_df[sub_df['Metadata_Well']==w]
    sub_df = sub_df[feature]
    q1 = np.quantile(sub_df, .25)
    q2 = np.quantile(sub_df, .75)
    IQR = q2 - q1
    return [i for i in sub_df.index if sub_df[i] < (q1-1.5*IQR) or sub_df[i] > (q2+1.5*IQR)]
    # return pd.Series(np.where((x < (q1 - 1.5*IQR)) | (x > (q2+1.5*IQR)), float('nan'), x))

# sds would be an array of number of standard deviation we are interested in
def replace_outliers_with_sd(df, feature, c, d, w, sds):
    sub_df= df[df['Metadata_Metadata_Cytokine']==c]
    sub_df = sub_df[sub_df['Metadata_Metadata_Dose']==d]
    sub_df = sub_df[sub_df['Metadata_Well']==w]
    sub_df = sub_df[feature]
    m = np.mean(sub_df)
    sd = np.std(sub_df)
    rs = {}
    for n in sds:
        rs[n] = [i for i in sub_df.index if sub_df[i] < (m - n * sd) or sub_df[i] > (m + n * sd)]
    return rs
    # return [i for i in sub_df.index if sub_df[i] < (m - n * sd) or sub_df[i] > (m + n * sd)]

def run_ANOVA_doses(cytokine, feature, df):
    # Dropping the Dose and Well columns
    df_doses = df.drop(['Metadata_Plate', 'Metadata_Well'], axis=1)
    final_df = pd.DataFrame(columns=['Cytokine', 'Feature', 'F-stat', 'P-value'])
    
    # subsetting the dataframe for the specified untreated cells
    sub_cyto_df = df_doses[df_doses['Metadata_Metadata_Cytokine'] == cytokine]
    obs = len(sub_cyto_df)
    
    # Calculating the power for this test using the size of the above subset
    power = TTestPower()
    anova_power = power.solve_power(nobs=obs, effect_size=0.5, power=None, alpha=0.05)
    
    # Group the subset by plate and perform One-Way ANOVA
    sub_df = sub_cyto_df[['Metadata_Metadata_Dose', feature]]
    grps = [d[feature] for _, d in sub_df.groupby('Metadata_Metadata_Dose')]
    F, p = f_oneway(*grps)
    
    # Append the results of our One-Way ANOVA to a dataframe and then return it along with the power
    final_df.loc[0] = [cytokine, feature, F, p]

    return final_df,anova_power

# Plot means of wells for each feature and each cytokine

def plot_by_dose(cytokine, feature, df):
    cytokine_dose = df[(df['Metadata_Metadata_Cytokine'] == cytokine)]
    cytokine_dose = cytokine_dose[['Metadata_Metadata_Dose', feature]]
    grouped = cytokine_dose.groupby('Metadata_Metadata_Dose')[feature]

    fig,ax = plt.subplots(figsize=(8,6))

    boxplot = ax.boxplot(x=[group.values for name, group in grouped],
                         labels=grouped.groups.keys(),
                         patch_artist=True,
                         medianprops={'color': 'black'}
                        )
    # Define colors for each group
    colors = ['orange', 'purple', '#69b3a2']

    # Assign colors to each box in the boxplot
    for box, color in zip(boxplot['boxes'], colors):
        box.set_facecolor(color)
        
    # Add a title and axis label
    ax.set_title('Dose Comparison: Mean Difference (' + cytokine + ' , ' + feature + ')')
    ax.set_xlabel('Doses')

def doses_Tukey_HSD(cytokine, feature, df):
    cytokine_doses = df[(df['Metadata_Metadata_Cytokine'] == cytokine)]
    cytokine_doses = cytokine_doses[['Metadata_Metadata_Dose', feature]]
    
    res = pairwise_tukeyhsd(endog=cytokine_doses[feature],
                          groups=cytokine_doses['Metadata_Metadata_Dose'],
                          alpha=0.05)
    
    return res

# Below is a funciton that will run t-test for each cytokine across both wells at 100 ng/ml

def get_ttest_wells(cytokine, feature, df):
    ttest_df = pd.DataFrame(columns=['Cytokine', 'Feature', 'Well Comparison', 'T-Statistic', 'p-value', 'Power'])
    # is it okay if we generalize the Metadata_Metadata_Dose to input by users
    cytokine_wells = df[(df['Metadata_Metadata_Dose'] == 100) & (df['Metadata_Metadata_Cytokine'] == cytokine)]
    obs = len(cytokine_wells)
    wells = cytokine_wells['Metadata_Well'].unique().tolist()
    
    well_1 = wells[0]
    well_2 = wells[1]
    
    well_comp = str(well_1) + ' vs ' + str(well_2)
    
    well_1_means = cytokine_wells.where(cytokine_wells['Metadata_Well'] == well_1).dropna()[feature]
    well_2_means = cytokine_wells.where(cytokine_wells['Metadata_Well'] == well_2).dropna()[feature]
    
    results = stats.ttest_ind(well_1_means,well_2_means, equal_var=False)
    power = TTestPower()
    ttest_power = power.solve_power(nobs=obs, effect_size=0.5, power=None, alpha=0.05)
    
    Tstat = round(results[0],3)
    Pvalue = round(results[1],3)
    
    ttest_df = ttest_df.append({'Cytokine' : cytokine, 'Feature': feature, 'Well Comparison': well_comp,
                               'T-Statistic': Tstat, 'p-value': Pvalue, 'Power': ttest_power}, ignore_index=True)
    return ttest_df

# base on Matthew's code, add in choice of dose

def get_ttest_wells_d(cytokine, dose, feature, df):
    ttest_df = pd.DataFrame(columns=['Cytokine', 'Feature', 'Well Comparison', 'T-Statistic', 'p-value', 'Power'])
    # is it okay if we generalize the Metadata_Metadata_Dose to input by users
    cytokine_wells = df[(df['Metadata_Metadata_Dose'] == dose) & (df['Metadata_Metadata_Cytokine'] == cytokine)]
    obs = len(cytokine_wells)
    wells = cytokine_wells['Metadata_Well'].unique().tolist()
    
    well_1 = wells[0]
    well_2 = wells[1]
    
    well_comp = str(well_1) + ' vs ' + str(well_2)
    
    well_1_means = cytokine_wells.where(cytokine_wells['Metadata_Well'] == well_1).dropna()[feature]
    well_2_means = cytokine_wells.where(cytokine_wells['Metadata_Well'] == well_2).dropna()[feature]
    
    results = stats.ttest_ind(well_1_means,well_2_means, equal_var=False)
    power = TTestPower()
    ttest_power = power.solve_power(nobs=obs, effect_size=0.5, power=None, alpha=0.05)
    
    Tstat = round(results[0],3)
    Pvalue = round(results[1],3)
    
    ttest_df = ttest_df.append({'Cytokine' : cytokine, 'Feature': feature, 'Well Comparison': well_comp,
                               'T-Statistic': Tstat, 'p-value': Pvalue, 'Power': ttest_power}, ignore_index=True)
    return ttest_df

# Plot means of wells for each feature and each cytokine

def plot_by_wells(cytokine, feature, df):
    cytokine_wells = df[(df['Metadata_Metadata_Dose'] == 100) & (df['Metadata_Metadata_Cytokine'] == cytokine)]
    cytokine_wells = cytokine_wells[['Metadata_Well', feature]]
    grouped = cytokine_wells.groupby('Metadata_Well')[feature]

    fig,ax = plt.subplots(figsize=(8,6))

    boxplot = ax.boxplot(x=[group.values for name, group in grouped],
                         labels=grouped.groups.keys(),
                         patch_artist=True,
                         medianprops={'color': 'black'}
                        )
    # Define colors for each group
    colors = ['orange', 'purple', '#69b3a2']

    # Assign colors to each box in the boxplot
    for box, color in zip(boxplot['boxes'], colors):
        box.set_facecolor(color)
        
    # Add a title and axis label
    ax.set_title('Well Comparison: TMean Difference at 100 ng/ml ( ' + cytokine + ' , ' + feature + ' )')
    ax.set_xlabel('Wells')

# base on Matthew's code, add in choice of dose
    
def plot_by_wells_d(cytokine, dose, feature, df):
    cytokine_wells = df[(df['Metadata_Metadata_Dose'] == dose) & (df['Metadata_Metadata_Cytokine'] == cytokine)]
    cytokine_wells = cytokine_wells[['Metadata_Well', feature]]
    grouped = cytokine_wells.groupby('Metadata_Well')[feature]

    fig,ax = plt.subplots(figsize=(8,6))

    boxplot = ax.boxplot(x=[group.values for name, group in grouped],
                         labels=grouped.groups.keys(),
                         patch_artist=True,
                         medianprops={'color': 'black'}
                        )
    # Define colors for each group
    colors = ['orange', 'purple', '#69b3a2']

    # Assign colors to each box in the boxplot
    for box, color in zip(boxplot['boxes'], colors):
        box.set_facecolor(color)
        
    # Add a title and axis label
    ax.set_title('Well Comparison: TMean Difference at 100 ng/ml ( ' + cytokine + ' , ' + feature + ' )')
    ax.set_xlabel('Wells')
    return fig

# Perform One-Way ANOVA to test mean differences across plates

def run_ANOVA_plates(untr, feature, df):
    # Dropping the Dose and Well columns
    df_doses = df.drop(['Metadata_Metadata_Dose', 'Metadata_Well'], axis=1)
    final_df = pd.DataFrame(columns=['Cytokine', 'Feature', 'F-stat', 'P-value'])
    
    # subsetting the dataframe for the specified untreated cells
    sub_cyto_df = df_doses[df_doses['Metadata_Metadata_Cytokine'] == untr]
    obs = len(sub_cyto_df)
    
    # Calculating the power for this test using the size of the above subset
    power = TTestPower()
    anova_power = power.solve_power(nobs=obs, effect_size=0.5, power=None, alpha=0.05)
    
    # Group the subset by plate and perform One-Way ANOVA
    sub_df = sub_cyto_df[['Metadata_Plate', feature]]
    grps = [d[feature] for _, d in sub_df.groupby('Metadata_Plate')]
    F, p = f_oneway(*grps)
    
    # Append the results of our One-Way ANOVA to a dataframe and then return it along with the power
    final_df.loc[0] = [untr, feature, F, p]

    return final_df,anova_power

# Visualizing the mean differences

def plot_by_plate(untr, feature, df):
    cytokine_plate = df[(df['Metadata_Metadata_Cytokine'] == untr)]
    cytokine_plate = cytokine_plate[['Metadata_Plate', feature]]
    grouped = cytokine_plate.groupby('Metadata_Plate')[feature]

    fig,ax = plt.subplots(figsize=(8,6))

    boxplot = ax.boxplot(x=[group.values for name, group in grouped],
                         labels=grouped.groups.keys(),
                         patch_artist=True,
                         medianprops={'color': 'black'}
                        )
    # Define colors for each group
    colors = ['orange', 'purple', '#69b3a2']

    # Assign colors to each box in the boxplot
    for box, color in zip(boxplot['boxes'], colors):
        box.set_facecolor(color)
        
    # Add a title and axis label
    ax.set_title('Plate Comparison: Mean Differences for untreatd cells (' + feature + ')')
    ax.set_xlabel('Plates')

# The following function will serve to supplement the above One-Way ANOVA by identifying which specific pairs 
# of plates are significantly different - Ideally, our dashboard should call this function when there is a significant
# difference between plates for cytokine

def plate_Tukey_HSD(untr, feature, df):
    untr_plates = df[(df['Metadata_Metadata_Cytokine'] == untr)]
    untr_plates = untr_plates[['Metadata_Plate', feature]]
    # should we change from groups=untr_plates['Metadata_Metadata_Dose']
    # to groups=untr_plates['Metadata_Metadata_Plate']
    res = pairwise_tukeyhsd(endog=untr_plates[feature],
                          groups=untr_plates['Metadata_Metadata_Dose'],
                          alpha=0.05)
    
    return res