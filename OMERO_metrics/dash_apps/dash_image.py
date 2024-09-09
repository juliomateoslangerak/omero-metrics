import dash
from dash import dcc, html
from dash_iconify import DashIconify
from django_plotly_dash import DjangoDash
from plotly.express.imshow_utils import rescale_intensity

from ..tools.data_preperation import *
import dash_mantine_components as dmc


external_scripts = [
    # add the tailwind cdn url hosting the files with the utility classes
    {"src": "https://cdn.tailwindcss.com"}
]
stylesheets = [
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
    "./assets/omero_metrics.css",
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
                dmc.Text(
                    "Intensity Map", c=primary_color, style={"fontSize": 30}
                ),
                dmc.Flex(
                    children=[
                        dcc.Graph(
                            figure={},
                            id="rois-graph",
                            style={
                                "margin-top": "20px",
                                "margin-bottom": "20px",
                                "border-radius": "0.5rem",
                                "padding": "20px",
                                "background-color": "white",
                            },
                        ),
                        dmc.Stack(
                            [
                                html.Div(
                                    [
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
                                dmc.Switch(
                                    id="switch-invert-colors",
                                    label="Invert Color",
                                    checked=False,
                                ),
                            ],
                        ),
                    ],
                    direction={"base": "column", "sm": "row"},
                    gap={"base": "sm", "sm": "lg"},
                    justify={"sm": "space-between"},
                    align={"sm": "center"},
                    style={
                        "margin-top": "10px",
                        "margin-bottom": "10px",
                        "background-color": "white",
                    },
                ),
                html.Div(id="blank-input"),
                html.Div(
                    [
                        dmc.Title(
                            "Intensity Profiles", c="#63aa47", size="h3"
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
                            },
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
    imaaa = image_omero[0, 0, :, :, int(args[0][-1])]
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
            name=str(row.ROI),
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
    fig.update_layout(coloraxis_colorbar_x=-0.15)
    fig.update_layout(coloraxis={"colorscale": color})
    if roi == "All":
        fig2 = go.Figure(fig)
        fig2.update_layout(shapes=corners + lines)
        fig2.add_trace(
            go.Scatter(x=df_points.X, y=df_points.Y, mode="markers")
        )

    elif roi == "Line":
        fig2 = go.Figure(fig)
        fig2.update_layout(shapes=lines)
    elif roi == "Square":
        fig2 = go.Figure(fig)
        fig2.update_layout(shapes=corners)
    elif roi == "Center":
        fig2 = go.Figure(fig)
        fig2.add_trace(
            go.Scatter(x=df_points.X, y=df_points.Y, mode="markers")
        )
    fig = fig2
    return fig


@dash_app_image.expanded_callback(
    dash.dependencies.Output("intensity_profile", "data"),
    [dash.dependencies.Input("my-dropdown1", "value")],
)
def callback_test5(*args, **kwargs):
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
