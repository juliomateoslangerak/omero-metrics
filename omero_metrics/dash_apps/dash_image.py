import dash
from dash import dcc, html, dash_table
import plotly.graph_objs as go
import numpy as np
from django_plotly_dash import DjangoDash
import plotly.express as px
from ..tools.data_preperation import *
import dash_mantine_components as dmc

colorscales = px.colors.named_colorscales()

dashboard_name = 'omero_image_dash'
dash_app_image = DjangoDash(name=dashboard_name, serve_locally=True,)

dash_app_image.layout = dmc.MantineProvider([dmc.Container(id='main',children=[
                                                             
                                    dmc.Center(dmc.Title("Dashboard For Image", c="#63aa47", size="h3")),
                                    dmc.Grid(
                                    [ dmc.GridCol(
                                            [
                                                html.H3("Select Channel"),
                                                dcc.Dropdown(id='my-dropdown1',
                                                          options={}, 
                                                          value="channel 0",
                                                          ),
                                            ],
                                            span="auto",
                                           
                                        ),
                                        dmc.GridCol(
                                            [
                                                html.H3("Select The Color Scale"),
                                                dcc.Dropdown(
                                                            id='dropdownColorScale', 
                                                            options=colorscales,
                                                            value='hot'
                                                        ),
                                            ],
                                            span="auto",
                                        ),
                                        dmc.GridCol(
                                            [html.H3("Add Rois"),
                                            dcc.RadioItems(
                                                            options=["Raw Image", "ROIS Image"],
                                                            value="Raw Image",
                                                            inline=True,
                                                            id="rois-radio",
                                                        ),],
                                            span="auto",
                                        )
                                    ],
                                ),
                                    
                                             
                        dcc.Graph(figure={}, id="rois-graph", style={"margin-top": "20px", "margin-bottom": "20px"}),
                        html.Div([           
                        dmc.Title("Intensity Profiles", c="#63aa47", size="h3"),
                        dcc.Graph(id='intensity_profiles',figure={}),
                        ] )
                    ], fluid=True,style={"background-color": "#eceff1", "margin":"20px" }
                                 )])



@dash_app_image.expanded_callback(
    dash.dependencies.Output('rois-graph', 'figure'),
    dash.dependencies.Output('my-dropdown1', 'options'),
    [dash.dependencies.Input('my-dropdown1', 'value'),
     dash.dependencies.Input('rois-radio', 'value'),
     dash.dependencies.Input('dropdownColorScale', 'value')])
def callback_test4(*args, **kwargs):
    image_omero = kwargs['session_state']['ima']
    imaaa = image_omero[0, 0, :, :, int(args[0][-1])] / 255
    imaa_fliped = np.flip(imaaa, axis=1)
    rb = imaaa[:,-1]
    lb= imaaa[:,0]
    dr = np.fliplr(imaaa).diagonal()
    dl = np.fliplr(imaa_fliped).diagonal()
    df_rects  = kwargs['session_state']['df_rects']
    df_lines  = kwargs['session_state']['df_lines']
    df_points = kwargs['session_state']['df_points']
    channel_list = [f"channel {i}" for i in range(0, image_omero.shape[4])]
    fig = px.imshow(imaaa, zmin=imaaa.min(), zmax=imaaa.max(), color_continuous_scale=args[2])
    fig1 = px.imshow(imaaa, zmin=imaaa.min(), zmax=imaaa.max(), color_continuous_scale=args[2])
    fig1 = add_rect_rois(go.Figure(fig1), df_rects)
    fig1 = add_line_rois(go.Figure(fig1), df_lines)
    fig1 = add_point_rois(go.Figure(fig1), df_points)
    if args[1] == "Raw Image":
        return fig, channel_list
    elif args[1] == "ROIS Image":
        return fig1, channel_list
    else:
        return fig, channel_list

@dash_app_image.expanded_callback(
    dash.dependencies.Output('intensity_profiles', 'figure'),
    [dash.dependencies.Input('my-dropdown1', 'value')])
def callback_test5(*args, **kwargs):
    df_intensity_profiles  = kwargs['session_state']['df_intensity_profiles']
    fig = px.line(df_intensity_profiles, markers=True)
    return fig


