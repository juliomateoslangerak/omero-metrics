import dash
from dash import dcc, html, Input, Output, callback
from django_plotly_dash import DjangoDash


dashboard_name = 'omero_project_dash'
dash_app_project = DjangoDash(name=dashboard_name, serve_locally=True,)


dash_app_project.layout = html.Div([
    dcc.Tabs(id='tabs-example-1', value='tab-1', children=[
        dcc.Tab(label='Tab one', value='tab-1'),
        dcc.Tab(label='Tab two', value='tab-2'),
    ]),
    html.Div(id='tabs-example-content-1')
])

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

