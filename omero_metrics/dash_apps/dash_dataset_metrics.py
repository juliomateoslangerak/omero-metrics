import dash
from dash import dcc, html, dash_table
import plotly.graph_objs as go
import numpy as np
from django_plotly_dash import DjangoDash
import plotly.express as px
import dash_mantine_components as dmc

c1 = "#d8f3dc"
c2 = "#eceff1"
c3 = "#189A35"

dashboard_name = 'omero_dataset_metrics'
dash_app_dataset = DjangoDash(name=dashboard_name, serve_locally=True, )

dash_app_dataset.layout = dmc.MantineProvider([dmc.Container(
    [
        dmc.Center(
            dmc.Text(
                id='title',
                c="#189A35",
                mb=30,
                style={"margin-top": "20px", "fontSize": 40},
            )
        ),
        dmc.Grid(
            [
                dmc.GridCol(
                    dmc.Stack(
                        [
                            dmc.Text("Microscope", size="sm"),
                            dcc.Dropdown(["Microscope L", "Microscope B", "Microscope G"]),
                            dmc.Text("Type of Analysis", size="sm"),
                            dcc.Dropdown(["Field Of Illumination"]),
                            dmc.Text("Analysis", size="sm"),
                            dcc.Dropdown(["L", "B", "G"]),
                        ]
                    ),
                    span=2,
                    style={
                        "background-c": c2,
                        "margin-right": "10px",
                        "border-radius": "0.5rem",
                    },
                ),
                dmc.GridCol(
                    [
                        dmc.Stack(
                            [
                                dmc.Title(
                                    "Key Measurements", c="#189A35", size="h3", mb=10
                                ),
                                dash_table.DataTable(
                                    id="table",
                                    page_size=10,
                                    sort_action="native",
                                    sort_mode="multi",
                                    sort_as_null=["", "No"],
                                    sort_by=[{"column_id": "pop", "direction": "asc"}],
                                    editable=False,
                                    style_cell={
                                        "textAlign": "left",
                                        "fontSize": 10,
                                        "font-family": "sans-serif",
                                    },
                                    style_header={
                                        "backgroundColor": "#189A35",
                                        "fontWeight": "bold",
                                        "fontSize": 15,
                                    },
                                ),
                            ]
                        )
                    ],
                    span="auto",
                    style={
                        "background-c": c2,
                        "margin-right": "10px",
                        "border-radius": "0.5rem",
                    },
                ),
                dmc.GridCol(
                    [dcc.Dropdown(value="Channel 0", id="channel_ddm"),
                     dmc.Title("Intensity Map", c="#189A35", size="h3", mb=10),
                     dcc.Graph(id="dataset_image_graph", figure={}, style={'display': 'inline-block', 'width': '100%',
                                                                           'height': '100%;'}),
                     ],
                    span="auto",
                    style={"background-c": "#eceff1", "border-radius": "5px"},
                ),
            ],
            justify="space-between",
            align="stretch",
            gutter="xl",
            style={
                "margin-top": "20px",
            },
        ),
    ],
    fluid=True,
)])


@dash_app_dataset.expanded_callback(
    dash.dependencies.Output('dataset_image_graph', 'figure'),
    dash.dependencies.Output('channel_ddm', 'options'),
    dash.dependencies.Output('title', 'children'),
    dash.dependencies.Output('table', 'data'),
    [dash.dependencies.Input('channel_ddm', 'value')])
def dataset_callback_intensity_map(*args, **kwargs):
    title = kwargs['session_state']['title']
    table = kwargs['session_state']['key_values_df']
    images = kwargs['session_state']['images']
    imaaa = images[0, 0, :, :, int(args[0][-1])] / 255
    channel_list = [f"channel {i}" for i in range(0, images.shape[4])]
    fig = px.imshow(imaaa, zmin=imaaa.min(), zmax=imaaa.max(), color_continuous_scale="gray")
    return fig, channel_list, title, table.to_dict('records')
