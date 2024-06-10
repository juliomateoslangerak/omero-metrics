import dash
from dash import dcc, html
from django_plotly_dash import DjangoDash
import plotly.express as px


dashboard_name = 'omero_dataset_dash'
dash_app_dataset = DjangoDash(name=dashboard_name, serve_locally=True, )

dash_app_dataset.layout = html.Div(id='main', children=[
    html.Div([dcc.Dropdown(id='my-dropdown1',
                           options={},
                           value="Channel 0",
                           className='col-md-12',
                           ),
              html.Div(id='test-output-div')
              ]),

    html.Div(id='test-output-div4')]
                                   )


@dash_app_dataset.expanded_callback(
    dash.dependencies.Output('test-output-div4', 'children'),
    dash.dependencies.Output('my-dropdown1', 'options'),
    [dash.dependencies.Input('my-dropdown1', 'value')])
def callback_test4(*args, **kwargs):
    image_omero = kwargs['session_state']['ima']
    imaaa = image_omero[0, 0, :, :, int(args[0][-1])] / 255

    channel_list = [f"channel {i}" for i in range(0, image_omero.shape[4])]
    fig = px.imshow(imaaa, zmin=imaaa.min(), zmax=imaaa.max(), color_continuous_scale="gray")
    gra = dcc.Graph(id='line-area-graph3', figure=fig, style={'display': 'inline-block', 'width': '100%',
                                                              'height': '100%;'})
    children = [gra]

    return children, channel_list
