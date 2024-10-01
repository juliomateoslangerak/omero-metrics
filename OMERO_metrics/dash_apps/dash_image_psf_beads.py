import dash
from dash import dcc, html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
import logging
import pandas as pd
from matplotlib.pyplot import autoscale

from OMERO_metrics.tools.data_preperation import (
    crop_bead_index,
    mip_graphs,
    fig_mip,
)
from dash_iconify import DashIconify

logger = logging.getLogger(__name__)
primary_color = "#63aa47"
app = DjangoDash("PSF_Beads_image")

app.layout = dmc.MantineProvider(
    children=[
        dmc.Container(
            [
                dmc.Center(
                    [
                        dmc.Group(
                            [
                                html.Img(
                                    src="./assets/images/logo.png",
                                    style={"width": "100px"},
                                ),
                                dmc.Title(
                                    "Intensity Map of Beads",
                                    c="#189A35",
                                    size="h3",
                                    mb=10,
                                    mt=5,
                                ),
                            ]
                        ),
                    ],
                    style={
                        "background-color": "white",
                        "border-radius": "0.5rem",
                        "padding": "10px",
                    },
                ),
                html.Div(id="blank-input"),
                dmc.Stack(
                    [
                        dmc.Grid(
                            children=[
                                dmc.GridCol(
                                    [
                                        dcc.Graph(
                                            figure={},
                                            id="psf_image_graph",
                                            style={
                                                "margin-top": "0px",
                                                "margin-bottom": "0px",
                                            },
                                        ),
                                    ],
                                    span=6,
                                ),
                                dmc.GridCol(
                                    [
                                        dmc.Stack(
                                            [
                                                html.Div(
                                                    [
                                                        dmc.Select(
                                                            id="channel_selector_psf_image",
                                                            label="Select Channel",
                                                            w="auto",
                                                            value="0",
                                                            leftSection=DashIconify(
                                                                icon="radix-icons:magnifying-glass"
                                                            ),
                                                            rightSection=DashIconify(
                                                                icon="radix-icons:chevron-down"
                                                            ),
                                                            mb=10,
                                                        ),
                                                        dmc.Text(
                                                            "Select Beads Location",
                                                            size="sm",
                                                            fw=500,
                                                        ),
                                                        dmc.SegmentedControl(
                                                            id="beads_info_segmented",
                                                            value="beads_info",
                                                            data=[
                                                                {
                                                                    "value": "beads_info",
                                                                    "label": "Beads Info",
                                                                },
                                                                {
                                                                    "value": "None",
                                                                    "label": "None",
                                                                },
                                                            ],
                                                            mb=10,
                                                        ),
                                                    ]
                                                ),
                                                dmc.Checkbox(
                                                    id="contour_checkbox_psf_image",
                                                    label="Contour Image",
                                                    checked=False,
                                                    mb=10,
                                                ),
                                                dmc.Checkbox(
                                                    id="roi_checkbox_psf_image",
                                                    label="Add ROI",
                                                    checked=False,
                                                    mb=10,
                                                ),
                                                dmc.Switch(
                                                    id="color_switch_psf_image",
                                                    label="Invert Color",
                                                    checked=False,
                                                    mb=10,
                                                ),
                                                dmc.Select(
                                                    id="color_selector_psf_image",
                                                    label="Select Color",
                                                    data=[
                                                        {
                                                            "value": "Hot",
                                                            "label": "Hot",
                                                        },
                                                        {
                                                            "value": "Viridis",
                                                            "label": "Viridis",
                                                        },
                                                        {
                                                            "value": "Inferno",
                                                            "label": "Inferno",
                                                        },
                                                    ],
                                                    w="auto",
                                                    value="Hot",
                                                    leftSection=DashIconify(
                                                        icon="radix-icons:color-wheel"
                                                    ),
                                                    rightSection=DashIconify(
                                                        icon="radix-icons:chevron-down"
                                                    ),
                                                ),
                                            ],
                                        ),
                                    ],
                                    span="content",
                                ),
                            ],
                            # gap={"base": "sm", "sm": "lg"},
                            justify="space-around",
                            align="center",
                            style={
                                "margin-top": "10px",
                                "margin-bottom": "10px",
                                "background-color": "white",
                                "border-radius": "0.5rem",
                            },
                        ),
                        dmc.Divider(variant="solid"),
                        dmc.Grid(
                            [
                                dmc.GridCol(
                                    [
                                        dmc.Title(
                                            "Maximum Intensity Projection",
                                            c="#189A35",
                                            size="h3",
                                            mb=10,
                                            mt=5,
                                        )
                                    ],
                                    span=6,
                                ),
                                dmc.GridCol(
                                    [
                                        dmc.Title(
                                            "Intensity Profiles Chart",
                                            c="#189A35",
                                            size="h3",
                                            mb=10,
                                            mt=5,
                                        )
                                    ],
                                    span=6,
                                ),
                            ],
                            align="flex-start",
                            style={
                                "background-color": "white",
                                "border-radius": "0.5rem",
                                "padding": "10px",
                            },
                        ),
                        dmc.Grid(
                            [
                                dmc.GridCol(
                                    [
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
                                        dmc.Select(
                                            data=[
                                                {
                                                    "label": "Axis X",
                                                    "value": "x",
                                                },
                                                {
                                                    "label": "Axis Y",
                                                    "value": "y",
                                                },
                                                {
                                                    "label": "Axis Z",
                                                    "value": "z",
                                                },
                                            ],
                                            value="x",
                                            id="axis_image_psf",
                                            w="auto",
                                            leftSection=DashIconify(
                                                icon="radix-icons:magnifying-glass"
                                            ),
                                            rightSection=DashIconify(
                                                icon="radix-icons:chevron-down"
                                            ),
                                            mb=10,
                                            mt=10,
                                        ),
                                        dcc.Graph(
                                            id="mip_chart_image",
                                            figure={},
                                        ),
                                    ],
                                    span="6",
                                ),
                            ],
                            align="flex-end",
                            style={
                                "background-color": "white",
                                "border-radius": "0.5rem",
                                "padding": "10px",
                            },
                        ),
                    ]
                ),
            ],
            fluid=True,
            style={
                "background-color": "#eceff1",
                "margin": "10px",
                "border-radius": "0.5rem",
                "padding": "10px",
            },
        )
    ]
)


@app.expanded_callback(
    dash.dependencies.Output("channel_selector_psf_image", "data"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_channels_psf_image(*args, **kwargs):
    channel_names = kwargs["session_state"]["context"]["channel_names"]
    channel_options = [
        {"label": c.name, "value": f"{i}"}
        for i, c in enumerate(channel_names.channels)
    ]
    return channel_options


@app.expanded_callback(
    dash.dependencies.Output("psf_image_graph", "figure"),
    [
        dash.dependencies.Input("channel_selector_psf_image", "value"),
        dash.dependencies.Input("color_selector_psf_image", "value"),
        dash.dependencies.Input("color_switch_psf_image", "checked"),
        dash.dependencies.Input("contour_checkbox_psf_image", "checked"),
        dash.dependencies.Input("roi_checkbox_psf_image", "checked"),
        dash.dependencies.Input("beads_info_segmented", "value"),
    ],
)
def update_image(*args, **kwargs):
    image_omero = kwargs["session_state"]["context"]["image"]
    channel_index = int(args[0])
    color = args[1]
    invert = args[2]
    contour = args[3]
    roi = args[4]
    beads_info = args[5]
    min_distance = kwargs["session_state"]["context"]["min_distance"]
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
    # df = df_beads_location[df_beads_location["bead_id"] == 0].copy()
    # df = df.reset_index(drop=True)
    # print(df)
    beads, roi_rect = get_beads_info(df_beads_location, min_distance)
    if invert:
        color = color + "_r"
    stack = image_omero[0, :, :, :, channel_index]
    mip_z = np.max(stack, axis=0)
    fig = px.imshow(mip_z, zmin=mip_z.min(), zmax=mip_z.max())
    fig.add_trace(beads)
    if roi:
        fig.update_layout(shapes=roi_rect)
    else:
        fig.update_layout(shapes=None)

    if contour:
        fig.plotly_restyle({"type": "contour"}, 0)

    if beads_info == "beads_info":
        fig.plotly_restyle(
            {
                "visible": True,
            },
            1,
        )
    else:
        fig.plotly_restyle({"visible": False}, 1)
    fig.update_layout(
        coloraxis={"colorscale": color},
        margin={"l": 0, "r": 0, "t": 10, "b": 10},
    )
    # fig = fig.update_yaxes(automargin=False)
    # fig.update_xaxes(range=[0, mip_z.shape[1]], scaleanchor="y", anchor='y',automargin=False)
    # fig.update_yaxes(range=[mip_z.shape[0]+20, -40],automargin=False)
    # fig.update_layout(autosize=True)
    return fig


@app.expanded_callback(
    dash.dependencies.Output("mip_image", "figure"),
    dash.dependencies.Output("mip_chart_image", "figure"),
    [
        dash.dependencies.Input("psf_image_graph", "clickData"),
        dash.dependencies.Input("axis_image_psf", "value"),
        dash.dependencies.Input("channel_selector_psf_image", "value"),
    ],
    prevent_initial_call=True,
)
def callback_mip(*args, **kwargs):
    point = args[0]["points"][0]
    axis = args[1].lower()
    channel_index = int(args[2])
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
        x0, xf, y0, yf = crop_bead_index(bead, min_dist, stack)
        mip_x, mip_y, mip_z = mip_graphs(x0, xf, y0, yf, stack)
        fig_mip_go = fig_mip(mip_x, mip_y, mip_z, title)
        # print(
        #     f"-----------------------------------GRAPH MIP {fig_mip_go}----------------------------------------"
        # )
        return (
            fig_mip_go,
            line_graph_axis(bead_index, channel_index, axis, kwargs),
        )
    else:
        return dash.no_update


def line_graph_axis(bead_index, channel_index, axis, kwargs):
    df_axis = kwargs["session_state"]["context"][f"bead_{axis}_profiles_df"]
    image_id = kwargs["session_state"]["context"]["image_id"]
    df_axis_3d = df_axis[
        df_axis.columns[df_axis.columns.str.startswith(str(image_id))]
    ]
    # 81_0_0_y_fitted image_id_channel_nr_bead_id_axis_fitted
    df_meta_x = pd.DataFrame(
        data=[
            [
                int(col.split("_")[-3]),
                int(col.split("_")[-4]),
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


def get_beads_info(df, min_distance):
    color_map = {"Yes": "green", "No": "red"}
    df["considered_axial_edge"] = df["considered_axial_edge"].map(
        {0: "No", 1: "Yes"}
    )
    df["considered_valid"] = df["considered_valid"].map({0: "No", 1: "Yes"})
    df["considered_self_proximity"] = df["considered_self_proximity"].map(
        {0: "No", 1: "Yes"}
    )
    df["considered_lateral_edge"] = df["considered_lateral_edge"].map(
        {0: "No", 1: "Yes"}
    )
    df["considered_intensity_outlier"] = df[
        "considered_intensity_outlier"
    ].map({0: "No", 1: "Yes"})
    beads_location_plot = go.Scatter(
        y=df["center_y"],
        x=df["center_x"],
        mode="markers",
        name="Beads Locations",
        marker=dict(
            size=10, opacity=0.3, color=df["considered_valid"].map(color_map)
        ),
        text=df["channel_nr"],
        customdata=np.stack(
            (
                df["bead_id"],
                df["considered_axial_edge"],
                df["considered_valid"],
                df["considered_self_proximity"],
                df["considered_lateral_edge"],
                df["considered_intensity_outlier"],
            ),
            axis=-1,
        ),
        hovertemplate="<b>Bead Number:</b>  %{customdata[0]} <br>"
        + "<b>Channel Number:</b>  %{text} <br>"
        + "<b>Considered valid:</b>  %{customdata[2]}<br>"
        + "<b>Considered self proximity:</b>  %{customdata[3]}<br>"
        + "<b>Considered lateral edge:</b>  %{customdata[4]}<br>"
        + "<b>Considered intensity outlier:</b>  %{customdata[5]}<br>"
        + "<b>Considered Axial Edge:</b> %{customdata[1]} <br><extra></extra>",
    )
    corners = [
        dict(
            type="rect",
            x0=row.center_x - min_distance,
            y0=row.center_y - min_distance,
            x1=row.center_x + min_distance,
            y1=row.center_y + min_distance,
            xref="x",
            yref="y",
            line=dict(
                color="RoyalBlue",
                width=3,
            ),
        )
        for i, row in df.iterrows()
    ]
    return beads_location_plot, corners
