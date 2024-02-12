import numpy as np
import plotly.graph_objects as go
from plotly.colors import n_colors

def generate_violins(data, col, sd=4):
    colors = n_colors('rgb(5, 200, 200)', 'rgb(200, 10, 10)', 
                          len(data), colortype='rgb') if len(data) > 1 else ['rgb(5, 200, 200)']
        
    fig = go.Figure()
    for data_line, color in zip(data.keys(), colors):
        x = data[data_line]#[col]
            
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
    annotation = ' (' + str(sd)+' sds away)'
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
    fig.add_vline(x=0, line_width=3, line_dash="dash", line_color="green")
    return fig