
import os
os.environ['R_HOME']=r'D:\Program Files\R\R-4.3.3'
print(os.environ['R_HOME'])
from rpy2.robjects.packages import importr
import rpy2.robjects as robjects
pwr = importr("pwr")
webpower = importr("WebPower")
# ttest = pwr.pwr_t_test
import plotly.graph_objects as go
from dash import Dash
import pandas as pd
import plotly.express as px
from pathlib import Path
HERE = Path(__file__).parent.absolute()
from typing import List
from functools import cached_property

class Functions:
    datafile = HERE / 'functions.csv'
    TestNameCol = 'name of Test'
    PackageCol = 'Package'
    FunctionCol = 'Function'
    AdjCol = 'adj'
    Parameters = {
        'pwr.pwr.t.test': {}
    }
    
    @cached_property
    def rows(self)->List[dict]:
        df = pd.read_csv(self.datafile)
        return df.to_dict('records')
    
    @cached_property
    def name2package(self)->dict:
        map = {}
        for row in self.rows:
            map[row[self.TestNameCol]] = row[self.PackageCol]
            
    @cached_property
    def name2function(self)->dict:
        map = {}
        for row in self.rows:
            map[row[self.TestNameCol]] = row[self.FunctionCol]
            
            

def ttest(n=None, d=None, sig_level=.05, power=.8, type="one.sample", alternative="two.sided"):
    if n is None and d is None:
        raise ValueError('Parameter n and d should not be None at the same time')
    assert type in ("two.sample", "one.sample", "paired")
    assert alternative in ("two.sided", "less", "greater")
    params = dict(sig_level=sig_level, power=power, type=type, alternative=alternative)
    if d is None:
        params['n'] = n
    else:
        params['d'] = d
    r = pwr.pwr_t_test(**params)
    return dict(
        n=r[0][0],
        d=r[1][0],
        sig_level=r[2][0],
        power=r[3][0],
        alternative=r[4][0]
    )  

def genfig():
    ds = []
    ns = []
    for i in range(89):
        d = 0.05 + i * 0.01
        ds.append(d)
        r=ttest(d=d)
        ns.append(r['n'])
    df = pd.DataFrame({
        'SampleSize': ns,
        'EffectSize': ds,
    })
    return px.line(df, x='EffectSize', y='SampleSize')



from dash import Dash, dcc, html, Input, Output
import plotly.express as px

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Analysis of Iris data using scatter matrix'),
    dcc.Dropdown(
        id="dropdown",
        options=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
        value=['sepal_length', 'sepal_width'],
        multi=True
    ),
    dcc.Graph('graph', figure=genfig()),
])


# @app.callback(
#     Output("graph", "figure"), 
#     Input("dropdown", "value"))
# def update_bar_chart(dims):
#     df = px.data.iris() # replace with your own data source
#     fig = px.scatter_matrix(
#         df, dimensions=dims, color="species")
#     return fig


app.run_server(debug=True)