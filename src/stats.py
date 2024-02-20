import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns
import scipy.stats as stats
from statsmodels.stats.power import TTestIndPower
from statsmodels.stats.power import FTestAnovaPower
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.power import TTestPower
from scipy.stats import f_oneway

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

def doses_Tukey_HSD(cytokine, feature, df):
    cytokine_doses = df[(df['Metadata_Metadata_Cytokine'] == cytokine)]
    cytokine_doses = cytokine_doses[['Metadata_Metadata_Dose', feature]]
    
    res = pairwise_tukeyhsd(endog=cytokine_doses[feature],
                          groups=cytokine_doses['Metadata_Metadata_Dose'],
                          alpha=0.05)
    
    return res

def get_ttest_wells(cytokine, feature, df):
    ttest_df = pd.DataFrame(columns=['Cytokine', 'Feature', 'Well Comparison', 'T-Statistic', 'p-value', 'Power'])
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

def plate_Tukey_HSD(untr, feature, df):
    untr_plates = df[(df['Metadata_Metadata_Cytokine'] == untr)]
    untr_plates = untr_plates[['Metadata_Plate', feature]]
    # should we change from groups=untr_plates['Metadata_Metadata_Dose']
    # to groups=untr_plates['Metadata_Metadata_Plate']
    res = pairwise_tukeyhsd(endog=untr_plates[feature],
                          groups=untr_plates['Metadata_Metadata_Dose'],
                          alpha=0.05)
    
    return res

def run_ANOVA_cytokines(df, feature, dose):
    sub_df = df[df['Metadata_Metadata_Dose'] == dose]
    
    # We're only looking at our treated cells, so filter out the untreated cells
    sub_df = sub_df[(sub_df['Metadata_Metadata_Cytokine'] != 'untr') & (sub_df['Metadata_Metadata_Cytokine'] != 'untr-50')]
    
    # Dropping the Dose and Well columns
    df_doses = df.drop(['Metadata_Metadata_Dose', 'Metadata_Plate', 'Metadata_Well'], axis=1)
    final_df = pd.DataFrame(columns=['Cytokine', 'Feature', 'F-stat', 'P-value'])
    
    # Get the length of the the subset dataframe
    obs = len(df_doses)
    
    # Calculating the power for this test using the size of the above subset
    power = TTestPower()
    anova_power = power.solve_power(nobs=obs, effect_size=0.5, power=None, alpha=0.05)
    
    # Group the subset by plate and perform One-Way ANOVA
    sub_df = sub_df[['Metadata_Metadata_Cytokine', feature]]
    grps = [d[feature] for _, d in sub_df.groupby('Metadata_Metadata_Cytokine')]
    F, p = f_oneway(*grps)
    
    # Append the results of our One-Way ANOVA to a dataframe and then return it along with the power
    final_df.loc[0] = [dose, feature, F, p]

    return final_df,anova_power

def plot_by_dose(df, feature, dose):
    cytokine_dose = df[(df['Metadata_Metadata_Dose'] == dose)]
    cytokine_dose = cytokine_dose[['Metadata_Metadata_Cytokine', feature]]
    grouped = cytokine_dose.groupby('Metadata_Metadata_Cytokine')[feature]

    fig,ax = plt.subplots(figsize=(8,6))

    boxplot = ax.boxplot(x=[group.values for name, group in grouped],
                         labels=grouped.groups.keys(),
                         patch_artist=True,
                         medianprops={'color': 'black'}
                        )
    # Define colors for each group
    #colors = ['orange', 'purple', '#69b3a2']

    # Assign colors to each box in the boxplot
    #for box, color in zip(boxplot['boxes'], colors):
        #box.set_facecolor(color)
        
    # Add a title and axis label
    ax.set_title('Cytokine Comparison: Mean Difference (' + feature + ',' + str(dose) + 'ng/ml)')
    ax.set_xlabel('Cytokines')

def cytokine_Tukey_HSD(df, feature, dose):
    
    # We're only looking at our treated cells, so filter out the untreated cells
    sub_df = df[(df['Metadata_Metadata_Cytokine'] != 'untr') & (df['Metadata_Metadata_Cytokine'] != 'untr-50')]
    
    cytokines = sub_df[(sub_df['Metadata_Metadata_Dose'] == dose)]
    cytokines = cytokines[['Metadata_Metadata_Cytokine', feature]]
    
    res = pairwise_tukeyhsd(endog=cytokines[feature],
                          groups=cytokines['Metadata_Metadata_Cytokine'],
                          alpha=0.05)
    
    return res