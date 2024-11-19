import dash
from dash import dcc, html
from dash_iconify import DashIconify
from django_plotly_dash import DjangoDash
from plotly.express.imshow_utils import rescale_intensity
import dash_mantine_components as dmc
import plotly.express as px
import plotly.graph_objects as go
from OMERO_metrics.styles import (
    THEME,
    MANTINE_THEME,
    LINE_CHART_SERIES,
    HEADER_PAPER_STYLE,
)


def get_icon(icon, size=20, color=None):
    return DashIconify(icon=icon, height=size, color=color)


dashboard_name = "omero_image_foi"
omero_image_foi = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=dmc.styles.ALL,
)


def create_header():
    return dmc.Paper(
        children=[
            dmc.Group(
                [
                    dmc.Group(
                        [
                            html.Img(
                                src="/static/OMERO_metrics/images/metrics_logo.png",
                                style={
                                    "width": "120px",
                                    "height": "auto",
                                },
                            ),
                            dmc.Stack(
                                [
                                    dmc.Title(
                                        "OMERO Image Analysis",
                                        c=THEME["primary"],
                                        size="h2",
                                    ),
                                    dmc.Text(
                                        "Interactive analysis of image data",
                                        c=THEME["text"]["secondary"],
                                        size="sm",
                                    ),
                                ],
                                gap="xs",
                            ),
                        ],
                    ),
                    dmc.Badge(
                        "FOI Analysis",
                        color=THEME["primary"],
                        variant="dot",
                        size="lg",
                    ),
                ],
                justify="space-between",
            ),
        ],
        **HEADER_PAPER_STYLE,
    )


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
                        id="my-dropdown1",
                        label="Channel",
                        w="100%",
                        value="0",
                        allowDeselect=False,
                        leftSection=get_icon("material-symbols:layers"),
                        rightSection=get_icon("radix-icons:chevron-down"),
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
                        data=[
                            {"value": "Center", "label": "Center"},
                            {"value": "Line", "label": "Line"},
                            {"value": "Square", "label": "Square"},
                            {"value": "All", "label": "All"},
                            {"value": "None", "label": "None"},
                        ],
                        color=THEME["primary"],
                        fullWidth=True,
                    ),
                    dmc.Stack(
                        [
                            dmc.Checkbox(
                                id="checkbox-state",
                                label="Enable Contour View",
                                checked=False,
                                color=THEME["primary"],
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
                        id="my-dropdown2",
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
                        leftSection=get_icon("material-symbols:palette"),
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
                ],
                gap="sm",
            ),
        ],
    )


def create_intensity_profile():
    return dmc.Paper(
        h="100%",
        children=[
            dmc.Stack(
                [
                    dmc.Group(
                        [
                            dmc.Text(
                                "Intensity Profiles",
                                size="lg",
                                fw=500,
                                c=THEME["primary"],
                            ),
                            dmc.Badge(
                                "Microscope-Metrics Analysis",
                                color="blue",
                                variant="light",
                                size="sm",
                            ),
                        ],
                        justify="space-between",
                    ),
                    dmc.LineChart(
                        id="intensity_profile",
                        h=250,
                        dataKey="Pixel",
                        data={},
                        series=LINE_CHART_SERIES,
                        xAxisLabel="Position (pixels)",
                        yAxisLabel="Intensity",
                        gridAxis="x",
                        withXAxis=True,
                        withYAxis=True,
                        withLegend=True,
                        strokeWidth=2,
                        withDots=False,
                        curveType="natural",
                    ),
                ],
                gap="md",
            ),
        ],
        p="md",
        radius="md",
        withBorder=True,
        shadow="sm",
    )


omero_image_foi.layout = dmc.MantineProvider(
    [
        create_header(),
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
                create_intensity_profile(),
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
    dash.dependencies.Output("my-dropdown1", "data"),
    [dash.dependencies.Input("blank-input", "children")],
)
def callback_channel(*args, **kwargs):
    channel_names = kwargs["session_state"]["context"]["channel_names"]
    channel_list = [
        {"label": c.name, "value": f"{i}", "description": f"Channel {i+1}"}
        for i, c in enumerate(channel_names.channels)
    ]
    return channel_list


@omero_image_foi.expanded_callback(
    dash.dependencies.Output("rois-graph", "figure"),
    [
        dash.dependencies.Input("my-dropdown1", "value"),
        dash.dependencies.Input("my-dropdown2", "value"),
        dash.dependencies.Input("checkbox-state", "checked"),
        dash.dependencies.Input("switch-invert-colors", "checked"),
        dash.dependencies.Input("segmented", "value"),
    ],
)
def callback_image(*args, **kwargs):
    color = args[1]
    checked_contour = args[2]
    inverted_color = args[3]
    roi = args[4]

    if inverted_color:
        color = color + "_r"

    image_omero = kwargs["session_state"]["context"]["image"]
    image_data = image_omero[0, 0, :, :, int(args[0])]
    image_data = rescale_intensity(
        image_data, in_range=(0, image_data.max()), out_range=(0.0, 1.0)
    )

    df_rects = kwargs["session_state"]["context"]["df_rects"]
    df_lines = kwargs["session_state"]["context"]["df_lines"]
    df_points = kwargs["session_state"]["context"]["df_points"]
    df_point_channel = df_points[df_points["C"] == int(args[0])].copy()

    fig = px.imshow(
        image_data,
        zmin=image_data.min(),
        zmax=image_data.max(),
        color_continuous_scale=color,
    )
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
            customdata=df_point_channel.ROI_NAME.str.replace(" ROIs", ""),
            hovertemplate="<b>%{customdata}</b><br>X: %{x}<br>Y: %{y}<extra></extra>",
        )
    )
    # TODO: it can make the page unresponsive, fix the bug
    if checked_contour:
        fig.plotly_restyle({"type": "contour"}, 0)
        fig.update_yaxes(autorange="reversed")

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
    )
    corners = [
        dict(
            type="rect",
            x0=row.X,
            y0=row.Y,
            x1=row.X + row.W,
            y1=row.Y + row.H,
            xref="x",
            yref="y",
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
            line=dict(
                color="RoyalBlue",
                width=2,
                dash="dash",
            ),
        )
        for i, row in df_lines.iterrows()
    ]

    if roi == "All":
        fig.update_layout(shapes=corners + lines)
        fig.plotly_restyle({"visible": True}, 1)
    elif roi == "Line":
        fig.update_layout(shapes=lines)
        fig.plotly_restyle({"visible": False}, 1)
    elif roi == "Square":
        fig.update_layout(shapes=corners)
        fig.plotly_restyle({"visible": False}, 1)
    elif roi == "Center":
        fig.update_layout(shapes=None)
        fig.plotly_restyle({"visible": True}, 1)
    elif roi == "None":
        fig.update_layout(shapes=None)
        fig.plotly_restyle({"visible": False}, 1)

    return fig


@omero_image_foi.expanded_callback(
    dash.dependencies.Output("intensity_profile", "data"),
    [dash.dependencies.Input("my-dropdown1", "value")],
)
def update_intensity_profiles(*args, **kwargs):
    df_intensity_profiles = kwargs["session_state"]["context"][
        "df_intensity_profiles"
    ]
    ch = f"ch{int(args[0]):02d}"
    df_profile = df_intensity_profiles[
        df_intensity_profiles.columns[
            df_intensity_profiles.columns.str.startswith(ch)
        ]
    ].copy()
    df_profile.columns = df_profile.columns.str.replace(
        "ch\d{2}_", "", regex=True
    )
    df_profile.columns = df_profile.columns.str.replace("_", " ", regex=True)
    df_profile.columns = df_profile.columns.str.title()
    df_profile.columns = df_profile.columns.str.replace(
        "Lefttop To Rightbottom", "Diagonal (↘)"
    )
    df_profile.columns = df_profile.columns.str.replace(
        "Leftbottom To Righttop", "Diagonal (↗)"
    )
    df_profile.columns = df_profile.columns.str.replace(
        "Center Horizontal", "Horizontal (→)"
    )
    df_profile.columns = df_profile.columns.str.replace(
        "Center Vertical", "Vertical (↓)"
    )

    return df_profile.to_dict("records")
