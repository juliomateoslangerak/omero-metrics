import dash
from dash import dcc, html, Input, Output, callback, clientside_callback
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
import plotly.express as px
dashboard_name = 'omero_project_dash'
dash_app_project = DjangoDash(name=dashboard_name, serve_locally=True,assets_external_path="./statics/omero_metrics/dash_apps/js/")


dash_app_project.layout = dmc.MantineProvider([
    html.Div(id='blank-output'),
    html.Div([
    dcc.Tabs(id='tabs-example-1', value='tab-1', children=[
        dcc.Tab(label='Tab one', value='tab-1'),
        dcc.Tab(label='Tab two', value='tab-2'),
    ]),
    html.Div(id='tabs-example-content-1'),
    dmc.Title("Plot Over Time", c="#63aa47", size="h3", mb=10),
                        dcc.Graph(id="graph_line", figure={}),
    
])])

@dash_app_project.expanded_callback(
    dash.dependencies.Output('tabs-example-content-1', 'children'),
    dash.dependencies. Input('tabs-example-1', 'value')
)
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Tab content 1'),
            dcc.Graph(
                figure=dict(
                    data=[dict(
                        x=[1, 2, 3],
                        y=[3, 1, 2],
                        type='bar'
                    )]
                )
            )
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2'),
            dcc.Graph(
                figure=dict(
                    data=[dict(
                        x=[1, 2, 3],
                        y=[5, 10, 6],
                        type='bar'
                    )]
                )
            )
        ])

@dash_app_project.expanded_callback(
    dash.dependencies.Output('graph_line', 'figure'),
    [dash.dependencies.Input('tabs-example-1', 'value')])
def callback_project(*args, **kwargs):
    data  = kwargs['session_state']['data']
    fig = px.line(x=data['Dataset_ID'].to_list(), y=data['Date'].to_list(), markers=True)
    return fig

dash_app_project.clientside_callback(
    """
    function(tab_value) {
    var p = tab_value["points"][0]["x"]
    test(p)
    console.log(tab_value)
    }
    """,
    dash.dependencies.Output('blank-output', 'children'),
    [dash.dependencies.Input("graph_line", "clickData")])
#