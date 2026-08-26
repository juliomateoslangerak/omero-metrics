import dash
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from django_plotly_dash import DjangoDash
from skimage.transform import resize

import omero_metrics.dash_apps.dataset_image.dash_foi.foi_shared_components as fsc
import omero_metrics.dash_apps.utils.omero_metrics_components as my_components
from omero_metrics.dash_apps.dataset_image import dataset_shared_components as dsc
from omero_metrics.styles import (
    MANTINE_THEME,
    THEME,
)
from omero_metrics.tools import load
from omero_metrics.tools.serializers import deserialize

dashboard_name = "omero_image_foi"
omero_image_foi = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)

# The display controls beside this chart change nothing the server has to
# recompute, so they are applied in the browser to the figure that is already
# there rather than by rebuilding it. That only works if every element they
# touch keeps a fixed address, so: the traces are always added in the order
# below whether or not they are shown, and layout.shapes always holds the
# rectangles first and the lines after. The addresses travel with the figure in
# layout.meta -- see _display_meta -- so the JavaScript holds no second copy.
IMAGE_TRACES = dict(image=0, contour=1, points=2)

# What each option of the segmented control shows, in the order they appear in
# it. Kept here rather than in the JavaScript so the options, their order and
# their effect stay in one place.
ROI_VIEWS = {
    "Center": dict(corners=False, lines=False, points=True),
    "Line": dict(corners=False, lines=True, points=False),
    "Square": dict(corners=True, lines=False, points=False),
    "All": dict(corners=True, lines=True, points=True),
    "None": dict(corners=False, lines=False, points=False),
}

# Contour lines are traced through a coarsened copy of the image rather than the
# image itself. Doing it at full resolution is what made this view lock up the
# page, and the lines it produced followed the pixel noise rather than the
# illumination. The copy is anti-aliased on the way down, so what is left is the
# shape of the field.
CONTOUR_GRID_SIZE = 128


def create_control_panel():
    return dmc.Paper(
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
                        id="channel_dropdown",
                        label="Channel",
                        w="100%",
                        allowDeselect=False,
                        leftSection=my_components.get_icon(
                            "material-symbols:layers"
                        ),
                        rightSection=my_components.get_icon(
                            "radix-icons:chevron-down"
                        ),
                        styles={
                            "rightSection": {"pointerEvents": "none"},
                            "item": {"fontSize": "14px"},
                            "input": {"borderColor": THEME["primary"]},
                        },
                    ),
                    dmc.Divider(
                        label="Display Options",
                        labelPosition="center",
                        mt="md",
                    ),
                    dmc.SegmentedControl(
                        id="segmented",
                        value="All",
                        data=[{"value": view, "label": view} for view in ROI_VIEWS],
                        color=THEME["primary"],
                        fullWidth=True,
                    ),
                    dmc.Switch(
                        id="show-contours-switch",
                        label="Show contours",
                        checked=False,
                        size="md",
                        color=THEME["primary"],
                    ),
                    dmc.Divider(
                        label="Color Settings",
                        labelPosition="center",
                        mt="md",
                    ),
                    dmc.Select(
                        id="color_select",
                        label="Color Scheme",
                        allowDeselect=False,
                        data=[
                            {"value": value, "label": label}
                            for value, label in dsc.INTENSITY_COLORSCALES
                        ],
                        value="Hot",
                        leftSection=my_components.get_icon(
                            "material-symbols:palette"
                        ),
                        styles={
                            "rightSection": {"pointerEvents": "none"},
                            "item": {"fontSize": "14px"},
                            "input": {"borderColor": THEME["primary"]},
                        },
                    ),
                    dmc.Switch(
                        id="switch-invert-colors",
                        label="Invert Colors",
                        checked=False,
                        size="md",
                        color=THEME["primary"],
                    ),
                    dcc.Store(
                        id="foi-colorscale-store",
                        data=dsc.INTENSITY_COLORSCALE_DATA,
                    ),
                ],
                gap="sm",
            ),
        ],
    )


omero_image_foi.layout = dmc.MantineProvider(
    [
        my_components.header_component(
            "OMERO Image Analysis",
            "Interactive analysis of image data",
            "FOI Analysis",
            load_buttons=False,
        ),
        dmc.Container(
            [
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Paper(
                                    [
                                        dmc.Text(
                                            "Intensity Map",
                                            size="lg",
                                            fw=500,
                                            c=THEME["primary"],
                                            mb="md",
                                        ),
                                        dcc.Graph(
                                            id="rois-graph",
                                            figure={},
                                            style={"height": "400px"},
                                        ),
                                    ],
                                    p="md",
                                    radius="md",
                                    withBorder=True,
                                    shadow="sm",
                                ),
                            ],
                            span=8,
                        ),
                        dmc.GridCol(
                            create_control_panel(),
                            span=4,
                        ),
                    ],
                    gutter="md",
                ),
                dmc.Space(h="md"),
                fsc.intensity_profile_paper(),
                html.Div(id="blank-input", style={"display": "none"}),
            ],
            size="xl",
            px="md",
            py="md",
            style={"backgroundColor": THEME["background"]},
        ),
    ],
    theme=MANTINE_THEME,
)


@omero_image_foi.expanded_callback(
    dash.dependencies.Output("channel_dropdown", "data"),
    dash.dependencies.Output("channel_dropdown", "value"),
    [dash.dependencies.Input("blank-input", "children")],
)
def callback_channel(_blank_input, *, session_state):
    mm_image = deserialize(session_state["context"]["mm_image"])
    return [
        {"label": c.name, "value": str(i), "description": f"Channel {i+1}"}
        for i, c in enumerate(mm_image.channel_series.channels)
    ], "0"


def _contour_trace(image, visible):
    """An iso-intensity overlay for ``image``, traced on a coarsened grid.

    Added to the figure whether or not it is shown, so the switch that reveals
    it has a trace to flip. See ``CONTOUR_GRID_SIZE`` for why it is coarsened.
    """
    height, width = image.shape
    shape = (min(CONTOUR_GRID_SIZE, height), min(CONTOUR_GRID_SIZE, width))
    coarse = resize(image, shape, anti_aliasing=True, preserve_range=True)
    # resize covers the same extent as the image, so each coarse sample sits at
    # the centre of the block of pixels it averaged rather than on its corner.
    return go.Contour(
        x=(np.arange(shape[1]) + 0.5) * (width / shape[1]) - 0.5,
        y=(np.arange(shape[0]) + 0.5) * (height / shape[0]) - 0.5,
        z=coarse,
        contours=dict(coloring="lines", showlabels=True),
        line=dict(width=1),
        colorscale=[[0, "white"], [1, "white"]],
        showscale=False,
        hoverinfo="skip",
        visible=visible,
    )


def _display_meta(corner_count, line_count):
    """Tell the clientside display controls where the elements they flip live.

    Carried in ``layout.meta``, which is inert as far as plotly is concerned but
    reaches the browser with the figure.
    """
    return dict(
        contour_trace=IMAGE_TRACES["contour"],
        points_trace=IMAGE_TRACES["points"],
        corner_count=corner_count,
        line_count=line_count,
        roi_views=ROI_VIEWS,
    )


# Applied in the browser to the figure already rendered there. Reading the
# figure back costs nothing -- it is a State, so plotly's own copy is handed
# straight to this function -- whereas rebuilding it re-reads the image.
_JS_DISPLAY = """
function(color, invert, showContours, roiView, fig, colorscales) {
    const meta = (fig && fig.layout && fig.layout.meta) || null;
    // No meta means the figure is not one of ours to adjust: either the empty
    // initial figure or nothing at all yet.
    if (!fig || !fig.data || !fig.data.length || !meta) {
        return window.dash_clientside.no_update;
    }
    const data = fig.data.map((trace) => ({...trace}));
    const layout = {...fig.layout};
    const view = (meta.roi_views || {})[roiView] || {};

    data[meta.contour_trace].visible = showContours;
    data[meta.points_trace].visible = !!view.points;

    // The rectangles lead layout.shapes and the lines follow, so the two
    // groups can be flipped independently from their counts alone.
    layout.shapes = (layout.shapes || []).map((shape, i) => {
        if (i < meta.corner_count) return {...shape, visible: !!view.corners};
        if (i < meta.corner_count + meta.line_count)
            return {...shape, visible: !!view.lines};
        return shape;
    });

    // px.imshow binds its heatmap to the layout coloraxis, so the colorscale is
    // set there rather than on the trace. The colour arrays come from the store
    // because plotly.js does not know the "_r" reversed names, which are a
    // plotly.py convention.
    const colorscale = (colorscales || {})[invert ? color + "_r" : color];
    if (colorscale) {
        layout.coloraxis = {...layout.coloraxis, colorscale: colorscale};
    }

    return {...fig, data: data, layout: layout};
}
"""


# Only the channel rebuilds the figure -- it is the one input that changes the
# image and the point subset. The colour and display inputs are States here so
# the first render already agrees with them, and Inputs of the clientside
# callback below, which applies them in the browser.
@omero_image_foi.expanded_callback(
    dash.dependencies.Output("rois-graph", "figure"),
    [
        dash.dependencies.Input("channel_dropdown", "value"),
        dash.dependencies.State("color_select", "value"),
        dash.dependencies.State("switch-invert-colors", "checked"),
        dash.dependencies.State("show-contours-switch", "checked"),
        dash.dependencies.State("segmented", "value"),
    ],
)
def callback_image(
    channel, color, inverted_color, show_contours, roi, *, session_state
):
    mm_dataset = deserialize(session_state["context"]["mm_dataset"])
    mm_image = deserialize(session_state["context"]["mm_image"])
    image_id = mm_image.data_reference.omero_object_id
    if inverted_color:
        color = color + "_r"
    channel_data = mm_image.array_data[0, 0, :, :, int(channel)]
    rois = load.get_rois_mm_dataset(mm_dataset)
    df_lines = pd.DataFrame(rois[image_id]["roi"]["Line"])
    df_rects = pd.DataFrame(rois[image_id]["roi"]["Rectangle"])
    df_points = pd.DataFrame(rois[image_id]["roi"]["Point"])
    df_lines.columns = df_lines.columns.str.upper()
    df_rects.columns = df_rects.columns.str.upper()
    df_points.columns = df_points.columns.str.upper()

    df_point_channel = df_points[df_points["C"] == int(channel)].copy()
    view = ROI_VIEWS[roi]

    fig = px.imshow(
        channel_data,
        zmin=0.0,
        color_continuous_scale=color,
    )
    fig.add_trace(_contour_trace(channel_data, show_contours))
    fig.add_trace(
        go.Scatter(
            x=df_point_channel.X,
            y=df_point_channel.Y,
            mode="markers",
            marker=dict(
                size=8,
                color="red",
                line=dict(width=1, color="white"),
            ),
            customdata=df_point_channel.NAME,
            hovertemplate="<b>%{customdata}</b><br>X: %{x}<br>Y: %{y}<extra></extra>",
            visible=view["points"],
        )
    )

    # Both groups are always built and always in this order, whichever the
    # segmented control is showing; each carries the visibility it starts with.
    corners = [
        dict(
            type="rect",
            x0=row.X,
            y0=row.Y,
            x1=row.X + row.W,
            y1=row.Y + row.H,
            xref="x",
            yref="y",
            visible=view["corners"],
            line=dict(
                color="RoyalBlue",
                width=2,
            ),
        )
        for i, row in df_rects.iterrows()
    ]

    lines = [
        dict(
            type="line",
            x0=row.X1,
            y0=row.Y1,
            x1=row.X2,
            y1=row.Y2,
            xref="x",
            yref="y",
            visible=view["lines"],
            line=dict(
                color="RoyalBlue",
                width=2,
                dash="dash",
            ),
        )
        for i, row in df_lines.iterrows()
    ]

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        coloraxis_colorbar=dict(
            thickness=15,
            len=0.7,
            title=dict(text="Intensity", side="right"),
            tickfont=dict(size=10),
        ),
        shapes=corners + lines,
        meta=_display_meta(len(corners), len(lines)),
    )

    return fig


omero_image_foi.clientside_callback(
    _JS_DISPLAY,
    dash.dependencies.Output("rois-graph", "figure", allow_duplicate=True),
    [
        dash.dependencies.Input("color_select", "value"),
        dash.dependencies.Input("switch-invert-colors", "checked"),
        dash.dependencies.Input("show-contours-switch", "checked"),
        dash.dependencies.Input("segmented", "value"),
    ],
    [
        dash.dependencies.State("rois-graph", "figure"),
        dash.dependencies.State("foi-colorscale-store", "data"),
    ],
    # Nothing to apply until callback_image has drawn the figure, and that
    # callback already renders these inputs' initial values itself.
    prevent_initial_call=True,
)


fsc.register_intensity_profile_callbacks(
    omero_image_foi, "channel_dropdown", per_image=True
)
