import dash
from dash import dcc, html, dash_table
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import plotly.express as px
import dash_mantine_components as dmc


dashboard_name1 = 'dash_example_1'
dash_example1 = DjangoDash(name=dashboard_name1,
                           serve_locally=True,
                           # app_name=app_name
                          )

dash_example1.layout = html.Div(id='main',
                                children=[
                                    html.Div([dcc.Dropdown(id='my-dropdown1',
                                                          options={}, 
                                                          value="Channel 0",
                                                           className='col-md-12',
                                                          ),
                                              html.Div(id='test-output-div')
                                             ]),

                                    html.Div(id='test-output-div4'),
                                    html.Div([
                                    dash_table.DataTable(id='table1', page_size=5),
                                    dash_table.DataTable(id='table2', page_size=5),
                                    dash_table.DataTable(id='table3', page_size=5),])

                                ]) 



@dash_example1.expanded_callback(
    dash.dependencies.Output('test-output-div4', 'children'),
    dash.dependencies.Output('my-dropdown1', 'options'),
    dash.dependencies.Output('table1', 'data'),
    dash.dependencies.Output('table2', 'data'),
    dash.dependencies.Output('table3', 'data'),
    [dash.dependencies.Input('my-dropdown1', 'value')])
def callback_test4(*args, **kwargs):
    image_omero = kwargs['session_state']['ima']
    df_project = kwargs['session_state']['df_project']
    df_dataset = kwargs['session_state']['df_dataset']
    df_image = kwargs['session_state']['df_image']
    df = kwargs['session_state']['df_project']
    imaaa = image_omero[0, 0, :, :, int(args[0][-1])] / 255
    channel_list = [f"channel {i}" for i in range(0, image_omero.shape[4])]
    fig = px.imshow(imaaa, zmin=imaaa.min(), zmax=imaaa.max(), color_continuous_scale="gray")
    gra = dcc.Graph(id='line-area-graph3', figure=fig, style={'display':'inline-block', 'width':'100%',
                                                                     'height':'100%;'})
    children = [gra]

    return children, channel_list, df_project.to_dict('records'), df_dataset.to_dict('records'), df_image.to_dict('records')


