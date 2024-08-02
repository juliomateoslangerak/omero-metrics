import dash
from dash import dcc, html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from ..tools.data_preperation import crop_bead_index, image_3d_chart
import plotly.express as px
from .utilities.dash_utilities import image_heatmap_setup
from .utilities.dash_layout_utility import layout_utility
import numpy as np
import logging
import json
import pandas as pd
from ..tools.data_preperation import crop_bead_index, mip_graphs, fig_mip

logger = logging.getLogger(__name__)
primary_color = "#63aa47"
app = DjangoDash("PSF_Beads_image")

app.layout = dmc.MantineProvider(
    children=[
        dmc.Container(
            [
                dmc.Center(
                    [
                        dmc.Text(
                            id="title",
                            c=primary_color,
                            style={"fontSize": 30},
                        ),
                        dmc.Group(
                            [
                                html.Img(
                                    src="./assets/images/logo.png",
                                    style={"width": "100px"},
                                ),
                                dmc.Text(
                                    "OMERO Metrics Dashboard",
                                    c=primary_color,
                                    style={"fontSize": 15},
                                ),
                            ]
                        ),
                    ]
                ),
                dmc.Divider(variant="solid"),
                html.Div(id="blank-input"),
                dmc.Stack(
                    [
                        dcc.Dropdown(
                            value="channel 0",
                            id="channel_ddm_psf",
                            clearable=False,
                        ),
                        dcc.Graph(
                            id="image",
                            figure={},
                            style={
                                "display": "inline-block",
                                "width": "100%",
                                "height": "100%;",
                            },
                        ),
                        dmc.Grid(
                            [
                                dmc.GridCol(
                                    [
                                        dmc.Title(
                                            "Maximum Intensity Projection",
                                            c="#189A35",
                                            size="h3",
                                            mb=10,
                                        ),
                                        dcc.Graph(
                                            id="mip_image",
                                            figure={},
                                            style={
                                                "display": "inline-block",
                                                "width": "100%",
                                                "height": "100%;",
                                            },
                                        ),
                                    ],
                                    span="6",
                                ),
                                dmc.GridCol(
                                    [
                                        dmc.Title(
                                            "Chart",
                                            c="#189A35",
                                            size="h3",
                                            mb=10,
                                        ),
                                        dcc.Dropdown(
                                            value="Axis: X",
                                            id="axis_image_psf",
                                        ),
                                        dcc.Graph(
                                            id="mip_chart_image",
                                            figure={},
                                            style={
                                                "display": "inline-block",
                                                "width": "100%",
                                                "height": "100%;",
                                            },
                                        ),
                                    ],
                                    span="6",
                                ),
                            ]
                        ),
                    ]
                ),
            ],
            fluid=True,
            style={
                "background-color": "#eceff1",
                "margin": "20px",
                "border-radius": "0.5rem",
                "padding": "10px",
            },
        )
    ]
)


@app.expanded_callback(
    dash.dependencies.Output("image", "figure"),
    dash.dependencies.Output("channel_ddm_psf", "options"),
    [
        dash.dependencies.Input("channel_ddm_psf", "value"),
    ],
)
def update_image(*args, **kwargs):
    image_omero = kwargs["session_state"]["context"]["image"]
    channel_index = int(args[0].split(" ")[-1])
    min_distance = kwargs["session_state"]["context"]["min_distance"]
    channel_names = kwargs["session_state"]["context"]["channel_names"]
    channel_options = [
        {"label": c.name, "value": f"channel {i}"}
        for i, c in enumerate(channel_names.channels)
    ]
    bead_properties_df = kwargs["session_state"]["context"][
        "bead_properties_df"
    ]
    df_beads_location = bead_properties_df[
        bead_properties_df["channel_nr"] == channel_index
        ][
        [
            "channel_nr",
            "bead_id",
            "considered_axial_edge",
            "considered_valid",
            "considered_self_proximity",
            "considered_lateral_edge",
            "considered_intensity_outlier",
            "center_z",
            "center_y",
            "center_x",
        ]
    ].copy()
    ima = image_omero[0, :, :, :, :]
    list_chan = [c.name for c in channel_names.channels]
    stack = image_omero[0, :, :, :, channel_index]
    stack_z = np.max(stack, axis=0)
    # stack_z = 255*stack_z / np.max(stack_z)
    fig = layout_utility(
        list_chan, stack_z, df_beads_location, min_distance=min_distance
    )
    return fig, channel_options


@app.expanded_callback(
    dash.dependencies.Output("mip_image", "figure"),
    dash.dependencies.Output("mip_chart_image", "figure"),
    dash.dependencies.Output("axis_image_psf", "options"),
    [
        dash.dependencies.Input("image", "clickData"),
        dash.dependencies.Input("axis_image_psf", "value"),
        dash.dependencies.Input("channel_ddm_psf", "value"),
    ],
    prevent_initial_call=True,
)
def callback_mip(*args, **kwargs):
    point = args[0]["points"][0]
    axis = args[1].split(" ")[-1].lower()
    channel_index = int(args[2].split(" ")[-1])
    options = ["Axis: X", "Axis: Y", "Axis: Z"]
    stack = kwargs["session_state"]["context"]["image"][
            0, :, :, :, channel_index
            ]
    bead_properties_df = kwargs["session_state"]["context"][
        "bead_properties_df"
    ]
    df_beads_location = bead_properties_df[
        bead_properties_df["channel_nr"] == channel_index
        ][
        [
            "channel_nr",
            "bead_id",
            "considered_axial_edge",
            "center_z",
            "center_x",
            "center_y",
        ]
    ].copy()
    min_dist = int(kwargs["session_state"]["context"]["min_distance"])
    if point["curveNumber"] == 1:
        bead_index = point["pointNumber"]
        title = (
            f"MIP for bead number: {bead_index} in channel: {channel_index}"
        )
        bead = df_beads_location[
            df_beads_location["bead_id"] == bead_index
            ].copy()
        x0, xf, y0, yf, z = crop_bead_index(bead, min_dist, stack)
        mip_x, mip_y, mip_z = mip_graphs(x0, xf, y0, yf, z, stack)
        return (
            fig_mip(mip_x, mip_y, mip_z, title),
            line_graph_axis(bead_index, channel_index, axis, kwargs),
            options,
        )
    else:
        return dash.no_update


def line_graph_axis(bead_index, channel_index, axis, kwargs):
    df_axis = kwargs["session_state"]["context"][f"bead_{axis}_profiles_df"]
    image_id = kwargs["session_state"]["context"]["image_id"]
    df_axis_3d = df_axis[
        df_axis.columns[df_axis.columns.str.startswith(str(image_id))]
    ]
    df_meta_x = pd.DataFrame(
        data=[
            [
                int(col.split("_")[-4]),
                int(col.split("_")[-5]),
                col.split("_")[-1],
                col,
            ]
            for col in df_axis_3d.columns
        ],
        columns=["bead_id", "channel_nr", "type", "name"],
    )
    cols_x = df_meta_x[
        (
                (df_meta_x["bead_id"] == bead_index)
                & (df_meta_x["channel_nr"] == channel_index)
        )
    ]["name"].values
    df_x = df_axis_3d[cols_x].copy()
    df_x.columns = df_x.columns.str.split("_").str[-1]
    fig_ip_x = px.line(df_x)
    fig_ip_x.update_traces(
        patch={"line": {"dash": "dot"}}, selector={"name": "fitted"}
    )
    return fig_ip_x
