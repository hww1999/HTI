import numpy as np
import plotly.graph_objects as go
from plotly.colors import n_colors

def generate_violins(data, col, sd=4):
    '''
    This function returns violin plots to show distributions of subsets of data
    
    Arguments:

    - data: a dictionary that stores key-value pair, in which the keys are the characters
    of the values, which are subsets of the original dataframe that fall in to the 
    group specified by the corresponding key
    - col: the variable that we are interested in
    - sd: the number of standard deviations we are interested in
    
    Returns: 
    
    - A violin plot that shows the distributions of data of the same cytokine at 
    different dosage levels, comparing to untreated experiments, with vertical
    lines in each distribution that show segments points out of a certain number of 
    standard deviations from the rest
    '''
    colors = n_colors('rgb(5, 200, 200)', 'rgb(200, 10, 10)', 
                          len(data), colortype='rgb') if len(data) > 1 else ['rgb(5, 200, 200)']
        
    fig = go.Figure()
    for data_line, color in zip(data.keys(), colors):
        x = data[data_line]#[col]
        if 'untr' in data_line:
            color = 'rgb(200, 200, 200)'
        fig.add_trace(go.Violin(x=x, line_color=color, 
                                name=data_line))
        m = np.mean(x)
        std = np.std(x)
        l = m-sd*std
        r = m+sd*std
        if r <= max(x):
            fig.add_vline(x=r, line_dash="dash", line_color=color)
        if l >= min(x):
            fig.add_vline(x=l, line_dash="dash", line_color=color)

    annotation = ' (' + str(sd)+' sds away)' if sd else ''
    fig.update_layout(
        autosize=True,
        height = 400,
        margin=dict(
            l=20,
            r=20,
            b=50,
            t=50,
            pad=4
        ),
        paper_bgcolor="LightSteelBlue",
        title = col + annotation
    )
    fig.update_traces(orientation='h', side='positive', 
                      width=3, points='outliers')
    fig.update_layout(xaxis_showgrid=False, xaxis_zeroline=False, title = col + annotation)
    # fig.add_vrect(x0=0.9, x1=2)
    # fig.add_vline(x=0, line_width=3, line_dash="dash", line_color="green")
    return fig

# def generate_group(data, group, c, d):

#     tmp_c = c # cytokine
#     tmp_d = d # dose
#     tmp = data[data['Metadata_Metadata_Cytokine']==tmp_c][data['Metadata_Metadata_Dose']==tmp_d]
#     tmp_gran = tmp.filter(regex = group)

#     colors = n_colors('rgb(5, 200, 200)', 'rgb(200, 10, 10)', len(data), colortype='rgb')

#     fig = go.Figure()
#     for i, color in zip(range(tmp_gran.shape[1]), colors):
#         fig.add_trace(go.Violin(x=tmp_gran.iloc[:,i], line_color=color, name=tmp_gran.iloc[:,i].name))

#     fig.update_traces(orientation='h', side='positive', width=3, points='outliers')
#     fig.update_layout(xaxis_showgrid=False, xaxis_zeroline=False, title = tmp_c+' '+str(tmp_d))
#         # fig.add_vrect(x0=0.9, x1=2)
#     fig.add_vline(x=0, line_width=3, line_dash="dash", line_color="green")

#     return fig

def generate_box(data, x, col):
    '''
    This function returns box-plot of data to view the distribution 
    and potential outliers of the data
    
    Arguments:

    - data: the dataframe containing the data
    - x: the variable, usually a metadata, to group by
    - col: the variable that we are interested in
    
    Returns: 
    
    - A box-plot with distinct groups on the x-axis and variable of interest y-axis
    '''

    fig = go.Figure()
    # y = data[col]
    fig.add_trace(go.Box(x=data[x], y=data[col],
                         boxpoints='outliers', marker_size=6, showwhiskers=True))

    fig.update_layout(
        autosize=True,
        height = 500,
        margin=dict(
            l=20,
            r=20,
            b=50,
            t=50,
            pad=4
        ),
        paper_bgcolor="LightSteelBlue",
    )

    return fig