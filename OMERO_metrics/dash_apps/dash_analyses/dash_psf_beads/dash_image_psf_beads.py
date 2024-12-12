import dash
from dash import dcc, html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
import logging
import OMERO_metrics.dash_apps.dash_utils.omero_metrics_components as my_components
from dash_iconify import DashIconify
from OMERO_metrics.styles import THEME, MANTINE_THEME
from OMERO_metrics.tools import load


def get_icon(icon, size=20, color=None):
    return DashIconify(icon=icon, height=size, color=color)


logger = logging.getLogger(__name__)
dashboard_name = "omero_image_psf_beads"

omero_image_psf_beads = DjangoDash(
    name=dashboard_name, serve_locally=True, external_scripts=dmc.styles.ALL
)

omero_image_psf_beads.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        # Header Section
        my_components.header_component(
            "PSF Beads Analysis",
            "Advanced Microscopy Image Analysis",
            "PSF beads Analysis",
            load_buttons=False,
        ),
        # Main Content
        dmc.Container(
            [
                html.Div(id="blank-input"),
                # Main Content
                dmc.Stack(
                    [
                        dmc.Grid(
                            children=[
                                dmc.GridCol(
                                    [
                                        dmc.Paper(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.Text(
                                                            "Bead Distribution Map",
                                                            size="lg",
                                                            fw=500,
                                                            c=THEME["primary"],
                                                        ),
                                                        dmc.Tooltip(
                                                            label="Click on a bead in the image to view its MIP",
                                                            children=[
                                                                get_icon(
                                                                    "material-symbols:info",
                                                                    color=THEME[
                                                                        "primary"
                                                                    ],
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                    justify="space-between",
                                                ),
                                                dcc.Graph(
                                                    figure={},
                                                    style={"height": "400px"},
                                                    id="psf_image_graph",
                                                ),
                                            ],
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                            shadow="sm",
                                            h="100%",
                                        ),
                                    ],
                                    span=8,
                                ),
                                dmc.GridCol(
                                    [
                                        dmc.Paper(
                                            h="100%",
                                            shadow="xs",
                                            p="md",
                                            radius="md",
                                            children=[
                                                dmc.Stack(
                                                    [
                                                        dmc.Text(
                                                            "Visualization Controls",
                                                            size="lg",
                                                            fw=500,
                                                            c=THEME["primary"],
                                                        ),
                                                        dmc.Divider(
                                                            label="Channel Selection",
                                                            labelPosition="center",
                                                        ),
                                                        dmc.Select(
                                                            id="channel_selector_psf_image",
                                                            label="Channel",
                                                            w="100%",
                                                            value="0",
                                                            allowDeselect=False,
                                                            leftSection=get_icon(
                                                                "material-symbols:layers"
                                                            ),
                                                            rightSection=get_icon(
                                                                "radix-icons:chevron-down"
                                                            ),
                                                        ),
                                                        dmc.Divider(
                                                            label="Display Options",
                                                            labelPosition="center",
                                                            mt="md",
                                                        ),
                                                        dmc.SegmentedControl(
                                                            id="beads_info_segmented",
                                                            value="beads_info",
                                                            data=[
                                                                {
                                                                    "value": "beads_info",
                                                                    "label": "Show Beads",
                                                                },
                                                                {
                                                                    "value": "None",
                                                                    "label": "Hide Beads",
                                                                },
                                                            ],
                                                            fullWidth=True,
                                                            color=THEME[
                                                                "primary"
                                                            ],
                                                            # w='auto'
                                                        ),
                                                        dmc.Stack(
                                                            [
                                                                dmc.Checkbox(
                                                                    id="contour_checkbox_psf_image",
                                                                    label="Enable Contour View",
                                                                    checked=False,
                                                                    color=THEME[
                                                                        "primary"
                                                                    ],
                                                                ),
                                                                dmc.Checkbox(
                                                                    id="roi_checkbox_psf_image",
                                                                    label="Show ROI Boundaries",
                                                                    checked=False,
                                                                    color=THEME[
                                                                        "primary"
                                                                    ],
                                                                ),
                                                            ],
                                                            gap="xs",
                                                        ),
                                                        dmc.Divider(
                                                            label="Color Settings",
                                                            labelPosition="center",
                                                            mt="md",
                                                        ),
                                                        dmc.Select(
                                                            id="color_selector_psf_image",
                                                            label="Color Scheme",
                                                            allowDeselect=False,
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
                                                            value="Hot",
                                                            leftSection=get_icon(
                                                                "material-symbols:palette"
                                                            ),
                                                            rightSection=get_icon(
                                                                "radix-icons:chevron-down"
                                                            ),
                                                        ),
                                                        dmc.Switch(
                                                            id="color_switch_psf_image",
                                                            label="Invert Colors",
                                                            checked=False,
                                                            size="md",
                                                            color=THEME[
                                                                "primary"
                                                            ],
                                                        ),
                                                    ],
                                                    gap="sm",
                                                ),
                                            ],
                                        ),
                                    ],
                                    span=4,
                                ),
                            ],
                        ),
                        dmc.Paper(
                            id="paper_mip",
                            shadow="sm",
                            p="md",
                            radius="md",
                            children=[
                                dmc.Grid(
                                    [
                                        # MIP Section
                                        dmc.GridCol(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.Text(
                                                            id="title_mip",
                                                            children="Maximum Intensity Projection",
                                                            size="lg",
                                                            fw=500,
                                                            c=THEME["primary"],
                                                        ),
                                                    ],
                                                    justify="space-between",
                                                ),
                                                dcc.Graph(
                                                    id="mip_image",
                                                    figure={},
                                                    style={"height": "400px"},
                                                ),
                                            ],
                                            span=6,
                                        ),
                                        dmc.GridCol(
                                            [
                                                dmc.Stack(
                                                    [
                                                        dmc.Group(
                                                            [
                                                                dmc.Text(
                                                                    "Intensity Profiles",
                                                                    size="lg",
                                                                    fw=500,
                                                                    c=THEME[
                                                                        "primary"
                                                                    ],
                                                                ),
                                                                dmc.Select(
                                                                    data=[
                                                                        {
                                                                            "label": "X Axis",
                                                                            "value": "x",
                                                                        },
                                                                        {
                                                                            "label": "Y Axis",
                                                                            "value": "y",
                                                                        },
                                                                        {
                                                                            "label": "Z Axis",
                                                                            "value": "z",
                                                                        },
                                                                    ],
                                                                    value="x",
                                                                    allowDeselect=False,
                                                                    id="axis_image_psf",
                                                                    rightSection=get_icon(
                                                                        "radix-icons:chevron-down"
                                                                    ),
                                                                    leftSection=get_icon(
                                                                        icon="mdi:axis-x-arrow"
                                                                    ),
                                                                ),
                                                            ],
                                                            justify="space-between",
                                                        ),
                                                        dcc.Graph(
                                                            id="mip_chart_image",
                                                            figure={},
                                                            style={
                                                                "height": "400px"
                                                            },
                                                        ),
                                                    ],
                                                    gap="md",
                                                ),
                                            ],
                                            span=6,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                    gap="md",
                ),
            ],
            size="xl",
            p="md",
            style={"backgroundColor": THEME["surface"]},
        ),
    ],
)


@omero_image_psf_beads.expanded_callback(
    dash.dependencies.Output("axis_image_psf", "leftSection"),
    [dash.dependencies.Input("axis_image_psf", "value")],
)
def update_icon(axis):
    icon = f"mdi:axis-{axis}-arrow"
    return get_icon(icon=icon)


@omero_image_psf_beads.expanded_callback(
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
def update_image(
    channel_index, color, invert, contour, roi, beads_info, **kwargs
):
    try:
        mm_dataset = kwargs["session_state"]["context"]["mm_dataset"]
        image_id = int(kwargs["session_state"]["context"]["image_id"])
        channel_index = int(channel_index)
        min_distance = int(
            mm_dataset.input_parameters.min_lateral_distance_factor
        )
        bead_properties_df = load.load_table_mm_metrics(
            mm_dataset.output["bead_properties"]
        )
        df_beads_location = bead_properties_df.loc[
            (bead_properties_df["image_id"] == image_id)
            & (bead_properties_df["channel_nr"] == channel_index),
            :,
        ]
        beads, roi_rect = get_beads_info(df_beads_location, min_distance)

        if invert:
            color = color + "_r"
        stack = kwargs["session_state"]["context"]["image"][
            0, :, :, :, channel_index
        ]
        mip_z = np.max(stack, axis=0)

        fig = px.imshow(
            mip_z,
            zmin=mip_z.min(),
            zmax=mip_z.max(),
            color_continuous_scale=color,
        )

        fig.add_trace(beads)

        if roi:
            fig.update_layout(shapes=roi_rect)
        else:
            fig.update_layout(shapes=None)

        if contour:
            fig.plotly_restyle({"type": "contour"}, 0)
            fig.update_yaxes(autorange="reversed")

        if beads_info == "beads_info":
            fig.update_traces(
                visible=True, selector=dict(name="Beads Locations")
            )
        else:
            fig.update_traces(
                visible=False, selector=dict(name="Beads Locations")
            )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            xaxis1=dict(showgrid=False, zeroline=False, visible=False),
            yaxis1=dict(showgrid=False, zeroline=False, visible=False),
            coloraxis_colorbar=dict(
                thickness=15,
                len=0.7,
                title=dict(text="Intensity", side="right"),
                tickfont=dict(size=10),
            ),
        )

        return fig

    except Exception as e:
        logger.error(f"Error updating image: {str(e)}")
        return px.imshow([[0]], title="Error loading image")


@omero_image_psf_beads.expanded_callback(
    dash.dependencies.Output("channel_selector_psf_image", "data"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_channels_psf_image(_, **kwargs):
    channel_names = kwargs["session_state"]["context"]["channel_names"]
    channel_options = [
        {"label": c.name, "value": f"{i}"}
        for i, c in enumerate(channel_names.channels)
    ]
    return channel_options


@omero_image_psf_beads.expanded_callback(
    dash.dependencies.Output("mip_image", "figure"),
    dash.dependencies.Output("mip_chart_image", "figure"),
    dash.dependencies.Output("title_mip", "children"),
    [
        dash.dependencies.Input("psf_image_graph", "clickData"),
        dash.dependencies.Input("axis_image_psf", "value"),
        dash.dependencies.Input("channel_selector_psf_image", "value"),
    ],
    prevent_initial_call=True,
)
def callback_mip(points, axis, channel_index, **kwargs):
    point = points["points"][0]
    axis = axis.lower()
    channel_names = kwargs["session_state"]["context"]["channel_names"]
    channels = [c.name for c in channel_names.channels]
    mm_dataset = kwargs["session_state"]["context"]["mm_dataset"]
    image_id = int(kwargs["session_state"]["context"]["image_id"])
    channel_index = int(channel_index)
    channel_name = channels[channel_index]
    bead_properties_df = load.load_table_mm_metrics(
        mm_dataset.output["bead_properties"]
    )
    df_beads_location = bead_properties_df.loc[
        (bead_properties_df["image_id"] == image_id)
        & (bead_properties_df["channel_nr"] == channel_index),
        :,
    ]
    min_dist = int(mm_dataset.input_parameters.min_lateral_distance_factor)
    if point["curveNumber"] == 1:
        bead_index = point["pointNumber"]

        bead = df_beads_location.loc[
            df_beads_location["bead_id"] == bead_index, :
        ]
        stack = kwargs["session_state"]["context"]["image"][
            0, :, :, :, channel_index
        ]
        x0, xf, y0, yf = my_components.crop_bead_index(bead, min_dist, stack)
        mip_x, mip_y, mip_z = my_components.mip_graphs(x0, xf, y0, yf, stack)
        fig_mip_go = my_components.fig_mip(mip_x, mip_y, mip_z)
        fig_mip_go.update_layout(
            coloraxis={
                "colorbar": dict(
                    thickness=15,
                    len=0.7,
                    title=dict(text="Intensity", side="right"),
                    tickfont=dict(size=10),
                ),
            },
            margin={"l": 20, "r": 20, "t": 30, "b": 20},
            plot_bgcolor=THEME["background"],
            paper_bgcolor=THEME["background"],
            font={"color": THEME["text"]["primary"]},
        )
        title = f"Maximum Intensity Projection for channel {channel_name} Bead number {bead_index}"
        return (
            fig_mip_go,
            line_graph_axis(bead_index, channel_index, axis, kwargs),
            title,
        )
    else:
        return dash.no_update


def line_graph_axis(bead_index, channel_index, axis, kwargs):
    mm_dataset = kwargs["session_state"]["context"]["mm_dataset"]
    df_axis = load.load_table_mm_metrics(
        mm_dataset.output[f"bead_profiles_{axis}"]
    )
    image_id = kwargs["session_state"]["context"]["image_id"]
    df_x = df_axis.filter(
        regex=f"^{image_id}_{channel_index}_{bead_index}_{axis}_"
    )
    df_x.columns = df_x.columns.str.split("_").str[-1]
    fig_ip_x = px.line(df_x)
    fig_ip_x.update_traces(
        patch={"line": {"dash": "dot"}}, selector={"name": "fitted"}
    )
    fig_ip_x.update_layout(
        plot_bgcolor=THEME["background"],
        paper_bgcolor=THEME["background"],
        font={"color": THEME["text"]["primary"]},
    )
    return fig_ip_x


def get_beads_info(df, min_distance):
    color_map = {"Yes": "green", "No": "red"}
    df["considered_axial_edge"] = df["considered_axial_edge"].map(
        {"False": "No", "True": "Yes"}
    )
    df["considered_valid"] = df["considered_valid"].map(
        {"False": "No", "True": "Yes"}
    )
    df["considered_self_proximity"] = df["considered_self_proximity"].map(
        {"False": "No", "True": "Yes"}
    )
    df["considered_lateral_edge"] = df["considered_lateral_edge"].map(
        {"False": "No", "True": "Yes"}
    )
    df["considered_intensity_outlier"] = df[
        "considered_intensity_outlier"
    ].map({"False": "No", "True": "Yes"})
    df["color"] = df["considered_valid"].map(color_map)
    beads_location_plot = go.Scatter(
        y=df["center_y"],
        x=df["center_x"],
        mode="markers",
        name="Beads Locations",
        marker=dict(
            size=0.001,
            opacity=0.01,
            color=df["considered_valid"].map(color_map),
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
                color=row["color"],
                width=3,
            ),
        )
        for i, row in df.iterrows()
    ]
    return beads_location_plot, corners
