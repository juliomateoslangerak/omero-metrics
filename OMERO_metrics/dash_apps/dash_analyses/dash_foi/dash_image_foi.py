import dash
from dash import dcc, html
from dash_iconify import DashIconify
from django_plotly_dash import DjangoDash
from plotly.express.imshow_utils import rescale_intensity

from OMERO_metrics.tools.data_preperation import *
import dash_mantine_components as dmc


stylesheets = [
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
]
primary_color = "#63aa47"

dashboard_name = "omero_image_dash"
dash_app_image = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=stylesheets,
)

dash_app_image.layout = dmc.MantineProvider(
    [
        dmc.Container(
            id="main",
            children=[
                dmc.Center(
                    [
                        dmc.Group(
                            [
                                html.Img(
                                    src="/static/OMERO_metrics/images/metrics_logo.png",
                                    style={"width": "100px"},
                                ),
                                dmc.Title(
                                    "Intensity Map",
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
                dmc.Grid(
                    children=[
                        dmc.GridCol(
                            [
                                dcc.Graph(
                                    figure={},
                                    id="rois-graph",
                                    style={
                                        "margin": "10px",
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
                                                    id="my-dropdown1",
                                                    label="Select Channel",
                                                    w="auto",
                                                    value="0",
                                                    clearable=False,
                                                    leftSection=DashIconify(
                                                        icon="radix-icons:magnifying-glass"
                                                    ),
                                                    rightSection=DashIconify(
                                                        icon="radix-icons:chevron-down"
                                                    ),
                                                    mb=10,
                                                ),
                                                dmc.Text(
                                                    "Select ROI",
                                                    size="sm",
                                                    fw=500,
                                                ),
                                                dmc.SegmentedControl(
                                                    id="segmented",
                                                    value="All",
                                                    data=[
                                                        {
                                                            "value": "Center",
                                                            "label": "Center",
                                                        },
                                                        {
                                                            "value": "Line",
                                                            "label": "Line",
                                                        },
                                                        {
                                                            "value": "Square",
                                                            "label": "Square",
                                                        },
                                                        {
                                                            "value": "All",
                                                            "label": "All",
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
                                            id="checkbox-state",
                                            label="Contour Image",
                                            checked=False,
                                            mb=10,
                                        ),
                                        dmc.Switch(
                                            id="switch-invert-colors",
                                            label="Invert Color",
                                            checked=False,
                                        ),
                                        dmc.Select(
                                            id="my-dropdown2",
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
                                            clearable=False,
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
                        "padding": "10px",
                    },
                    mt=10,
                ),
                html.Div(id="blank-input"),
                html.Div(
                    [
                        dmc.Center(
                            [
                                dmc.Title(
                                    "Intensity Profiles",
                                    c="#189A35",
                                    size="h3",
                                    mb=10,
                                    mt=5,
                                )
                            ],
                            style={
                                "background-color": "white",
                                "border-top-radius": "0.5rem",
                                "padding": "10px",
                            },
                        ),
                        dmc.LineChart(
                            id="intensity_profile",
                            h=400,
                            dataKey="Pixel",
                            data={},
                            series=[
                                {
                                    "name": "Lefttop To Rightbottom",
                                    "color": "violet.9",
                                },
                                {
                                    "name": "Leftbottom To Righttop",
                                    "color": "blue.9",
                                },
                                {
                                    "name": "Center Horizontal",
                                    "color": "pink.9",
                                },
                                {
                                    "name": "Center Vertical",
                                    "color": "teal.9",
                                },
                            ],
                            xAxisLabel="Pixel",
                            yAxisLabel="Pixel Intensity",
                            tickLine="y",
                            gridAxis="x",
                            withXAxis=False,
                            withYAxis=True,
                            withLegend=True,
                            strokeWidth=3,
                            withDots=False,
                            curveType="natural",
                            style={
                                "background-color": "white",
                                "padding": "20px",
                                "border-radius": "0.5rem",
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


@dash_app_image.expanded_callback(
    dash.dependencies.Output("my-dropdown1", "data"),
    [dash.dependencies.Input("blank-input", "children")],
)
def callback_channel(*args, **kwargs):
    channel_names = kwargs["session_state"]["context"]["channel_names"]
    channel_list = [
        {"label": c.name, "value": f"{i}"}
        for i, c in enumerate(channel_names.channels)
    ]
    data = channel_list
    return data


@dash_app_image.expanded_callback(
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
    imaaa = image_omero[0, 0, :, :, int(args[0])]
    imaaa = rescale_intensity(
        imaaa, in_range=(0, imaaa.max()), out_range=(0.0, 1.0)
    )
    df_rects = kwargs["session_state"]["context"]["df_rects"]
    df_lines = kwargs["session_state"]["context"]["df_lines"]
    df_points = kwargs["session_state"]["context"]["df_points"]
    df_point_channel = df_points[df_points["C"] == int(args[0])].copy()

    fig = px.imshow(
        imaaa,
        zmin=imaaa.min(),
        zmax=imaaa.max(),
        color_continuous_scale="Hot",
    )
    fig.add_trace(
        go.Scatter(
            x=df_point_channel.X,
            y=df_point_channel.Y,
            mode="markers",
            customdata=df_point_channel.ROI_NAME.str.replace(" ROIs", ""),
            hovertemplate="%{customdata}<extra></extra>",
        )
    )
    if checked_contour:
        fig.plotly_restyle({"type": "contour"}, 0)
        fig.update_yaxes(autorange="reversed")

    # Add dropdowns
    fig.update_layout(
        autosize=False,
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
                width=3,
            ),
        )
        for i, row in df_rects.iterrows()
    ]
    lines = [
        dict(
            type="line",
            name=str(row.NAME),
            showlegend=True,
            editable=True,
            x0=row.X1,
            y0=row.Y1,
            x1=row.X2,
            y1=row.Y2,
            xref="x",
            yref="y",
            line=dict(
                color="RoyalBlue",
                width=1,
                dash="dot",
            ),
        )
        for i, row in df_lines.iterrows()
    ]
    # fig.update_layout(coloraxis_colorbar_x=-0.15)
    fig.update_layout(coloraxis={"colorscale": color})
    if roi == "All":
        fig.update_layout(shapes=corners + lines)
        fig.plotly_restyle(
            {
                "visible": True,
            },
            1,
        )
    elif roi == "Line":
        fig.update_layout(shapes=lines)
        fig.plotly_restyle(
            {
                "visible": False,
            },
            1,
        )
    elif roi == "Square":
        fig.update_layout(shapes=corners)
        fig.plotly_restyle(
            {
                "visible": False,
            },
            1,
        )
    elif roi == "Center":
        fig.update_layout(shapes=None)
        fig.plotly_restyle(
            {
                "visible": True,
            },
            1,
        )
    elif roi == "None":
        fig.update_layout(shapes=None)
        fig.plotly_restyle(
            {
                "visible": False,
            },
            1,
        )
    fig.update_layout(margin=dict(l=10, r=10, b=10, t=10))
    return fig


@dash_app_image.expanded_callback(
    dash.dependencies.Output("intensity_profile", "data"),
    [dash.dependencies.Input("my-dropdown1", "value")],
)
def update_intensity_profiles(*args, **kwargs):
    df_intensity_profiles = kwargs["session_state"]["context"][
        "df_intensity_profiles"
    ]
    ch = "ch0" + args[0]
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

    return df_profile.to_dict("records")
