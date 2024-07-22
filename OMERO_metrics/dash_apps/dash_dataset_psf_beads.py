import dash
from dash import dcc, html, dash_table
from django_plotly_dash import DjangoDash
import plotly.express as px
import dash_mantine_components as dmc
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from ..tools.data_preperation import crop_bead_index, mip_graphs, fig_mip

app = DjangoDash("PSF_Beads")

app.layout = dmc.MantineProvider(
    [
        dmc.Container(
            [
                dmc.Center(
                    dmc.Text(
                        "PSF Beads Dashboard",
                        c="#189A35",
                        style={"fontSize": 20},
                    )
                ),
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                html.H3(
                                    "Select Channel",
                                    style={"color": "#63aa47"},
                                ),
                                dcc.Dropdown(
                                    id="channel_psf",
                                    value="channel 0",
                                    clearable=False,
                                ),
                            ],
                            span="auto",
                        ),
                    ],
                    style={
                        "margin-top": "20px",
                        "margin-bottom": "20px",
                        "border": "1px solid #63aa47",
                        "padding": "10px",
                        "border-radius": "0.5rem",
                        "background-color": "white",
                    },
                ),
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Title(
                                    "Image View", c="#189A35", size="h3", mb=10
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
                            ],
                            span="6",
                        ),
                        dmc.GridCol(
                            [
                                dmc.Title(
                                    "Key Measurements",
                                    c="#189A35",
                                    size="h3",
                                    mb=10,
                                ),
                                dash_table.DataTable(
                                    id="key_values_psf",
                                    page_size=10,
                                    sort_action="native",
                                    sort_mode="multi",
                                    sort_as_null=["", "No"],
                                    sort_by=[
                                        {
                                            "column_id": "pop",
                                            "direction": "asc",
                                        }
                                    ],
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
                                    style_table={"overflowX": "auto"},
                                ),
                            ],
                            span="6",
                        ),
                    ]
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
                                    id="mip",
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
                                    "Chart", c="#189A35", size="h3", mb=10
                                ),
                                dcc.Dropdown(
                                    value="Axis: X", id="axis_ddm_psf"
                                ),
                                dcc.Graph(
                                    id="mip_chart",
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
                html.Div(
                    id="test_point",
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
    dash.dependencies.Output("channel_psf", "options"),
    dash.dependencies.Output("key_values_psf", "data"),
    [dash.dependencies.Input("channel_psf", "value")],
)
def func_psf_callback(*args, **kwargs):
    channel_index = int(args[0].split(" ")[-1])
    image_o = kwargs["session_state"]["context"]["image"]
    km = kwargs["session_state"]["context"]["bead_km_df"]
    km = km.sort_values(by="channel_nr", ascending=True).reset_index(drop=True)
    km = km.pivot_table(columns="channel_name")
    km = km.reset_index(drop=False, names="Measurement")

    channel_names = kwargs["session_state"]["context"]["channel_names"]
    channel_list_psf = [
        {"label": c.name, "value": f"channel {i}"}
        for i, c in enumerate(channel_names.channels)
    ]
    stack_z = np.max(image_o[0, :, :, :, channel_index], axis=0)
    bead_properties_df = kwargs["session_state"]["context"][
        "bead_properties_df"
    ]
    channel_name = channel_names.channels[channel_index].name
    if channel_name in km.columns:
        km = km[["Measurement", channel_name]]
    df_properties_channel = bead_properties_df[
        bead_properties_df["channel_nr"] == channel_index
    ].copy()
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
    df_beads_location["considered_axial_edge"] = df_beads_location[
        "considered_axial_edge"
    ].map({0: "No", 1: "Yes"})
    stack_z = stack_z / stack_z.max()
    fig_image_z = px.imshow(
        stack_z,
        zmin=stack_z.min(),
        zmax=stack_z.max(),
        color_continuous_scale="gray",
    )
    color_map = {"Yes": "red", "No": "yellow"}
    fig_image_z.add_trace(
        go.Scatter(
            y=df_beads_location["center_y"],
            x=df_beads_location["center_x"],
            mode="markers",
            marker=dict(
                size=10,
                color=df_beads_location["considered_axial_edge"].map(
                    color_map
                ),
                opacity=0.3,
            ),
            text=df_beads_location["channel_nr"],
            customdata=np.stack(
                (
                    df_beads_location["bead_id"],
                    df_beads_location["considered_axial_edge"],
                ),
                axis=-1,
            ),
            hovertemplate="<b>Bead Number:</b>  %{customdata[0]} <br>"
            + "<b>Channel Number:</b>  %{text} <br>"
            + "<b>Considered Axial Edge:</b> %{customdata[1]} <br><extra></extra>",
        )
    )
    return (
        fig_image_z,
        channel_list_psf,
        km.to_dict("records"),
    )


@app.expanded_callback(
    dash.dependencies.Output("mip", "figure"),
    dash.dependencies.Output("mip_chart", "figure"),
    dash.dependencies.Output("axis_ddm_psf", "options"),
    [
        dash.dependencies.Input("image", "clickData"),
        dash.dependencies.Input("axis_ddm_psf", "value"),
        dash.dependencies.Input("channel_psf", "value"),
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
    min_dist = kwargs["session_state"]["context"]["min_distance"]
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
