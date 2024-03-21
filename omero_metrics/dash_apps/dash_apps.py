import dash
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Input, Output, callback, dash_table, dcc, html
from dash_iconify import DashIconify
from django_plotly_dash import DjangoDash

c1 = "#d8f3dc"
c2 = "#eceff1"
c3 = "#189A35"

dashboard_name1 = 'dash_example_1'
dash_example1 = DjangoDash(name=dashboard_name1,
                           serve_locally=True,
                           # app_name=app_name
                          )


dash_example1.layout = dmc.Container(
    [
        dmc.Center(
            dmc.Text(
                "Field Of Illumination Dashboard",
                color="#189A35",
                mb=30,
                style={"margin-top": "20px", "fontSize": 40},
            )
        ),
        dmc.Grid(
            [
                dmc.Col(
                    dmc.Stack(
                        [
                            dmc.Text("Microscope", size="sm", weight=700),
                            dcc.Dropdown(["Microscope L", "Microscope B", "Microscope G"]),
                            dmc.Text("Type of Analysis", size="sm", weight=700),
                            dcc.Dropdown(["Field Of Illumination"]),
                            dmc.Text("Analysis", size="sm", weight=700),
                            dcc.Dropdown(["L", "B", "G"]),
                        ]
                    ),
                    span=2,
                    style={
                        "background-color": c2,
                        "margin-right": "10px",
                        "border-radius": "0.5rem",
                    },
                ),
                dmc.Col(
                    [
                        dmc.Stack(
                            [
                                dmc.Grid(
                                    [
                                        dmc.Col(
                                            [
                                                html.H3("Select Category"),
                                                dcc.Dropdown(
                                                    valueWAs, value="channel", id="key_dpd"
                                                ),
                                            ],
                                            span="auto",
                                            style={"background-color": c2, "margin-right": "10px"},
                                        ),
                                        dmc.Col(
                                            [
                                                html.H3("Select Date"),
                                                dcc.DatePickerRange(
                                                    id="date_filter",
                                                    start_date_placeholder_text="Start Period",
                                                    end_date_placeholder_text="End Period",
                                                    start_date=data_g["Date Processed"].min(),
                                                    end_date=data_g["Date Processed"].max(),
                                                    min_date_allowed=data_g["Date Processed"].min(),
                                                    max_date_allowed=data_g["Date Processed"].max(),
                                                ),
                                            ],
                                            span="auto",
                                        ),
                                    ],
                                ),
                                dmc.Title(
                                    "Key Measurments for FOI", color="#189A35", size="h3", mb=10
                                ),
                                dash_table.DataTable(
                                    id="table",
                                    data=data_g.to_dict("records"),
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
                        "background-color": c2,
                        "margin-right": "10px",
                        "border-radius": "0.5rem",
                    },
                ),
                dmc.Col(
                    [
                        dmc.Title("Plot Over Time", color="#189A35", size="h3", mb=10),
                        dcc.Graph(id="graph_line", figure={}),
                    ],
                    span="auto",
                    style={"background-color": "#eceff1", "border-radius": "5px"},
                ),
            ],
            justify="space-between",
            align="stretch",
            gutter="xl",
            style={
                "margin-top": "20px",
            },
        ),
        dmc.Grid(
            id="grido",
            justify="space-between",
            align="stretch",
            gutter="xl",
            style={
                "margin-top": "20px",
            },
        ),
        dmc.Grid(
            id="grido1",
            justify="space-between",
            align="stretch",
            gutter="xl",
            style={
                "margin-top": "20px",
                "margin-bottom": "10px",
            },
        ),
    ],
    fluid=True,
)


@dash_example1.expanded_callback(
    dash.dependencies.Output("grido", "children"),
    dash.dependencies.Output("grido1", "children"),
    # Input("cell-selection-double-click-callback", "selectedRows"),
    dash.dependencies.Input("graph_line", "clickData"),
    prevent_initial_call=True,
)
def display_cell_double_clicked_on(point):
    # print(type(c[0]['pointIndex']))
    global ima
    global var
    ID = point["points"][0]["pointIndex"]
    style = {"background-color": c2, "border-radius": "0.5rem"}
    var = list_data[ID]["unprocessed_analysis"].output
    ima = get_intensity_map_data(var)
    # image = ima[0, 0, :, :, 0]
    data = get_key_values(var)
    # data_IP = get_intensity_profiles(var)

    channel_list_obj = [f"Channel {i}" for i in range(ima.shape[4])]
    # fig = px.imshow(image, zmin=0, zmax=1, color_continuous_scale="gray")
    row_map = []
    row_map.append(dmc.Title("Intensity Map", color="#189A35", size="h3"))
    row_map.append(
        dmc.Grid(
            [
                dmc.Col(
                    [dcc.Dropdown(channel_list_obj, value=channel_list_obj[0], id="channel-obj")],
                    span="auto",
                ),
                dmc.Col(
                    [
                        dcc.RadioItems(
                            options=["Raw Image", "ROIS Image"],
                            value="Raw Image",
                            inline=True,
                            id="rois-radio-obj",
                        )
                    ],
                    span="auto",
                ),
            ]
        )
    )
    row_map.append(
        html.Div(
            dcc.Slider(
                0,
                ima.shape[1],
                step=None,
                id="crossfilter-time--slider",
                value=0,
                marks={str(i): str(i) for i in range(ima.shape[1])},
            ),
            style={"width": "49%", "padding": "0px 20px 20px 20px"},
        )
    )

    row_map.append(dcc.Graph(figure={}, id="rois-graph-map"))

    t1 = []
    t1.append(dmc.Title("Key value Pairs", color="#189A35", size="h3"))
    t1.append(
        dash_table.DataTable(
            id="table-multicol-sorting",
            columns=[{"name": i, "id": i} for i in sorted(data.columns)],
            data=data.to_dict("records"),
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
    )
    children1 = [
        dmc.Col(
            id="object_info1",
            children=[dmc.Stack(id="map_image1", children=row_map)],
            span=4,
            style={"background-color": c2, "border-radius": "0.5rem", "margin-right": "10px"},
        ),
        dmc.Col(
            id="object_info2",
            children=[dmc.Stack(id="map_image2", children=t1)],
            span="auto",
            style=style,
        ),
    ]
    children2 = [
        dmc.Col(
            [
                dmc.Title("Intensity Profiles", color="#189A35", size="h3"),
                dcc.Graph(figure={}, id="intensity-profiles"),
            ],
            span=6,
            style={"background-color": c2, "border-radius": "0.5rem", "margin-right": "10px"},
        )
    ]
    return children1, children2


@dash_example1.expanded_callback(
    dash.dependencies.Output("graph_line", "figure"),
    dash.dependencies.Output("table", "data"),
    dash.dependencies.Input("date_filter", "start_date"),
    dash.dependencies.Input("date_filter", "end_date"),
    dash.dependencies.Input("key_dpd", "value"),
)
def update_line(start_date, end_date, key_dpd):
    data_fd = data_all_cols[
        (data_all_cols["Date Processed"] >= start_date)
        & (data_all_cols["Date Processed"] <= end_date)
    ]
    data_col = data_fd[["ID", "Object", "Channels", "Date Processed", key_dpd]].copy()
    v = [i[0] for i in data_col[key_dpd].to_list()]
    f = data_col["Date Processed"].to_list()
    line_graph = px.line(
        x=f, y=v, title=f"{key_dpd} by Date Processed", markers=True
    ).update_layout(clickmode="event+select")
    data_col[key_dpd] = data_col[key_dpd].astype(str)
    return line_graph, data_col.to_dict("records")


@dash_example1.expanded_callback(
    dash.dependencies.Output("rois-graph-map", "figure"),
    dash.dependencies.Output("intensity-profiles", "figure"),
    dash.dependencies.Input("channel-obj", "value"),
    dash.dependencies.Input("rois-radio-obj", "value"),
    dash.dependencies.Input("crossfilter-time--slider", "value"),
)
def update_graph(channel, value, slide_value):
    image1 = ima[0, slide_value, :, :, int(channel[-1])]
    roi_df = get_corner_rois(var)
    profile_rois_df = get_profile_rois(var)
    fig = px.imshow(image1)
    data_IP = get_intensity_profiles(var)
    df_profile = data_IP[
        data_IP.columns[data_IP.columns.str.startswith("ch0" + channel[-1])]
    ].copy()
    int_graph = px.line(df_profile)
    if value == "ROIS Image":
        fig1 = add_rois(go.Figure(fig), roi_df)
        fig1 = add_profile_rois(go.Figure(fig1), profile_rois_df)
        return fig1, int_graph
    else:
        return fig, int_graph
