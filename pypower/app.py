from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, '/assets/styles.css'])
MethodNames = ['T-Test', 'One-way ANOVA', 'Single Proportion Test']


methodDD = html.Div(
    [
        dbc.Label("Statistic", html_for="method"),
        dcc.Dropdown(
            id="method",
            options=[dict(label=mn, value=mn) for mn in MethodNames]
        ),
    ],
    className="mt-2",
)

Params = {
    'T-Test': [
        dict(
            name="type",
            label="Category:",
            type="select",
            options=("two.sample", "one.sample", "paired"),
            ),
    ],
    'One-way ANOVA': [
        dict(
            name="k", label= "NGroups",
            type="number", default=2
        )
        ],
}

heading = html.H4(
    "Sample Size Calculator", className="bg-primary text-white p-2"
)


# app.layout = dbc.Container(
#     [heading, methodDD, dbc.Row(
#         [dbc.Col(
#             [ 
#             html.Div(id="otherParameters"),
#             ], md=4),
#         dbc.Col([], md=8)],
#     )]
# )


power = html.Div(
    [
        dbc.Label("power", html_for="power"),
        dbc.Input(
            id="power",
            value=0.8,
            type="number"
        ),
    ],
    className="mt-2",
)

alternative = html.Div(
    [
        dbc.Label("alternative", html_for="alternative"),
        html.Div(dbc.RadioItems(
                ("two.sided", "less", "greater"),className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-primary",    labelCheckedClassName="active",
                value="two.sided", id="alternative"
            ), className="radio-group")
    ],
    className="mt-2",
)

sig_level = html.Div(
    [
        dbc.Label("SigLevel", html_for="sig_level"),
        html.Div(dbc.RadioItems(
                ("0.05", "0.01", "0.001"),className=" btn-group",
                value="0.05",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-primary",    labelCheckedClassName="active",
                id="sig_level"
            ), className="radio-group")
    ],
    className="mt-2",
)

control_panel0 = dbc.Card(
    dbc.CardBody(
        [sig_level, power, alternative],
        className="bg-light",
    )
)



control_panel1 = dbc.Card(
    dbc.CardBody(
        [methodDD,],
        className="bg-light",
    )
)

control_panel2 = dbc.Card(
    dbc.CardBody(
        [],
        className="bg-light",
        id="otherParameters"
    )
)


graph = dbc.Card(
    [html.Div(id="error_msg", className="text-danger"), dcc.Graph(id="graph")]
)

app.layout = html.Div(
    [heading, dbc.Row([dbc.Col([control_panel0, control_panel1, control_panel2], md=4), dbc.Col(graph, md=8)])]
)

@app.callback(
    Output("otherParameters", "children"),
    Input("method", "value")
)
def update_parameters(method: str):
    params = Params.get(method)
    if not params:
        return ''
    children = []
    for p in params:
        if p['type'] == 'select':
            ele = dbc.RadioItems(
                p['options'],className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-primary",    labelCheckedClassName="active",
                value=p['options'][0], id=p['name']
            )
            ele = html.Div(ele, className="radio-group",)
        elif p['type'] == 'number':
            ele = dbc.Input(value=p.get('default'), id=p['name'], type="number")
        row = dbc.Row([dbc.Label(p['label'], html_for=p['name'], width=4),
                               dbc.Col(ele, width=8),
                       ])
        children.append(row)
        
    return children 


# @app.callback(
#     Output("graph", "figure"), 
#     Input("dropdown", "value"))
# def update_bar_chart(dims):
#     df = px.data.iris() # replace with your own data source
#     fig = px.scatter_matrix(
#         df, dimensions=dims, color="species")
#     return fig


app.run_server(debug=True)