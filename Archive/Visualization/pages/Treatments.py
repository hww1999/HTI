from dash import Dash, dcc, html, Input, Output, State, callback, dash_table
import dash
import json
import pandas as pd
from src.treatment_profiling import treatment_profiles_heatmap
from sklearn.preprocessing import StandardScaler
import scipy.cluster.hierarchy as sch
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import plotly.figure_factory as ff

# References: See references below

dash.register_page(__name__)

layout = html.Div([
    html.H1('Treatment Similarity:'),
    html.H2('Heatmap:'),
    html.Div([
        dcc.Graph(id='treatment_heatmap')
    ]),
    html.H2('Clustering:'),
    html.Div([
        dcc.Graph(id='dendrogram')
    ])
])

# inputs: data
# outputs: figure
@callback(
    Output('treatment_heatmap', 'figure'),
    Input('dfs', 'data')
)
def update_heatmap(data):
    #convert to dataFrame
    # Reference: 
    # - https://stackoverflow.com/questions/21104592/json-to-pandas-dataframe
    # - https://stackoverflow.com/questions/57631895/dictionary-to-dataframe-error-if-using-all-scalar-values-you-must-pass-an-ind   
    
    data_dict = json.loads(data)
    v = list(data_dict.values())[0]
    df = pd.read_json(v, orient='split')
    
    fig = treatment_profiles_heatmap(df)
    return fig

# perform clustering (new attempt)
@callback(
    Output('dendrogram', 'figure'),
    Input('dfs', 'data')
)
def create_dendrogram(data):
    #convert to dataFrame
    # Reference: 
    # - https://stackoverflow.com/questions/21104592/json-to-pandas-dataframe
    # - https://stackoverflow.com/questions/57631895/dictionary-to-dataframe-error-if-using-all-scalar-values-you-must-pass-an-ind
    
    data_dict = json.loads(data)
    v = list(data_dict.values())[0]
    df = pd.read_json(v, orient='split')
    
    # merge cytokine and dose
    # Reference: https://stackoverflow.com/questions/19377969/combine-two-columns-of-text-in-pandas-dataframe
    df['Cytokine_and_Dose'] = df['Metadata_Metadata_Cytokine'] + "-" + df['Metadata_Metadata_Dose'].astype(str)

    treatment_col = df['Cytokine_and_Dose']
    df.drop(columns=['Cytokine_and_Dose'], inplace=True)

    # drop non_numeric columns
    df.drop(columns=['Metadata_Metadata_Cytokine', 'Metadata_Metadata_Dose', 'ImageNumber', 'ObjectNumber',
                        'Metadata_Plate', 'Metadata_Well'], inplace=True)

    # scale the data
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df))

    # add back in treatment column
    df_scaled['Cytokine_and_Dose'] = treatment_col

    # aggregate
    df_scaled_medians = df_scaled.groupby(['Cytokine_and_Dose']).median()
    
    # perform clustering
    # References:
    # - Scipy and Plotly Figure Factory Documentation
    # - https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html#scipy.spatial.distance.pdist
    # - https://plotly.com/python/dendrogram/
    # - https://plotly.com/python-api-reference/generated/plotly.figure_factory.html
    # - https://github.com/plotly/plotly.py/blob/master/packages/python/plotly/plotly/figure_factory/_dendrogram.py 
    # - https://plotly.github.io/plotly.py-docs/generated/plotly.figure_factory.create_dendrogram.html
    # - https://plotly.com/python/figure-factories/
    fig = ff.create_dendrogram(df_scaled_medians, orientation='left', labels=df_scaled_medians.index.to_list())
    fig.update_layout(height=600)
    return fig


# References:
# - https://towardsdatascience.com/machine-learning-algorithms-part-12-hierarchical-agglomerative-clustering-example-in-python-1e18e0075019
# - https://www.kaggle.com/code/sgalella/correlation-heatmaps-with-hierarchical-clustering/notebook
# - ChatGPT for help understanding code from other reference
# - https://www.kaggle.com/code/minc33/visualizing-high-dimensional-clusters/notebook#Clustering:
# - https://stackoverflow.com/questions/54815631/dendrogram-y-axis-labeling-confusion
# - https://datascience.stackexchange.com/questions/22355/when-is-centering-and-scaling-needed-before-doing-hierarchical-clustering
# - https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html#plot-all-scaling-standard-scaler-section
# - https://stats.stackexchange.com/questions/195456/how-to-select-a-clustering-method-how-to-validate-a-cluster-solution-to-warran/195481#195481
# - https://stats.stackexchange.com/questions/195446/choosing-the-right-linkage-method-for-hierarchical-clustering
# - https://www.nature.com/articles/nmeth.4397
# - https://stackoverflow.com/questions/34162443/why-do-many-examples-use-fig-ax-plt-subplots
# - https://matplotlib.org/3.1.1/gallery/subplots_axes_and_figures/figure_title.html
# - https://stackoverflow.com/questions/332289/how-do-i-change-the-size-of-figures-drawn-with-matplotlib
# - https://www.viewsonic.com/library/tech/monitor-resolution-aspect-ratio/#:~:text=27%2Dinch%201440p%20monitor%20has%20a%20pixel%20density%20of%20about%20108%20ppi
# - https://www.geeksforgeeks.org/python-lambda-anonymous-functions-filter-map-reduce/
# - https://en.wikipedia.org/wiki/Cophenetic#:~:text=In%20the%20clustering%20of%20biological,grouped%20into%20the%20same%20cluster
# - https://stackoverflow.com/questions/28687882/cutting-scipy-hierarchical-dendrogram-into-clusters-via-a-threshold-value
# - https://stackoverflow.com/questions/47412139/cutting-scipy-hierarchical-dendrogram-into-clusters-on-multiple-threshold-values
# - https://stackoverflow.com/questions/16883412/how-do-i-get-the-subtrees-of-dendrogram-made-by-scipy-cluster-hierarchy?noredirect=1&lq=1
# - https://stackoverflow.com/questions/11917779/how-to-plot-and-annotate-hierarchical-clustering-dendrograms-in-scipy-matplotlib
# - https://stackoverflow.com/questions/10305111/pruning-dendrogram-in-scipy-hierarchical-clustering
# - https://stackoverflow.com/questions/54815631/dendrogram-y-axis-labeling-confusion
# - https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering
# - https://scikit-learn.org/stable/modules/clustering.html
# - https://www.youtube.com/watch?v=EItlUEPCIzM


# References Debugging Using Matplotlib in Dash:
# - https://stackoverflow.com/questions/34764535/why-cant-matplotlib-plot-in-a-different-thread?rq=3
# - https://community.plotly.com/t/matplotlib-charts-in-multipage-app/66396
# - https://community.plotly.com/t/best-way-to-incorporate-matplotlib-plot-in-dash-app/12896
# - https://stackoverflow.com/questions/49851280/showing-a-simple-matplotlib-plot-in-plotly-dash/56932297#56932297
# - https://stackoverflow.com/questions/58495420/how-to-save-a-scipy-dendrogram-as-high-resolution-file
# - https://community.plotly.com/t/showing-matplotlib-figures-with-dash-mpl-to-plotly/15710/2
# - https://stackoverflow.com/questions/23015055/how-can-i-save-a-dendrogram-plot-from-scipy-cluster-hierarchy-dendrogram-as-a-fi
# - https://github.com/plotly/plotly.py/issues/1568
# - https://stackoverflow.com/questions/68036484/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-though-it
# - https://stackoverflow.com/questions/58782687/matplotlib-gives-this-application-failed-to-start-because-it-could-not-find-or-l
# - https://www.riverbankcomputing.com/static/Docs/PyQt5/installation.html#understanding-the-correct-version-to-install
# - https://stackoverflow.com/questions/59809703/could-not-load-the-qt-platform-plugin-xcb-in-even-though-it-was-found?rq=3
# - https://support.schrodinger.com/s/article/1842#:~:text=Windows%208%20and%20Windows%2010&text=To%20create%20a%20new%20environment,the%20Environment%20Variables%20dialog%20box
# - https://ioflood.com/blog/ldd-linux-command/#:~:text=The%20ldd%20command%20in%20Linux%20is%20a%20handy%20tool%20used,dependencies%20your%20program%20relies%20on.&text=In%20this%20example%2C%20we've,on%20the%20'ls'%20command
# - https://stackoverflow.com/questions/11542255/ldconfig-erroris-not-a-symbolic-link-when-using-linux-loader