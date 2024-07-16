import dash
from dash import dcc, html
from django_plotly_dash import DjangoDash
from ..tools.data_preperation import *
import dash_mantine_components as dmc


dashboard_name = "omero_image_dash"
dash_app_image = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)

dash_app_image.layout = dmc.MantineProvider(
    [
        dmc.Container(
            id="main",
            children=[
                dmc.Center(
                    dmc.Title("Dashboard For Image", c="#63aa47", size="h3")
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
                                    id="my-dropdown1",
                                    options={},
                                    value="channel 0",
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
                dcc.Graph(
                    figure={},
                    id="rois-graph",
                    style={
                        "margin-top": "20px",
                        "margin-bottom": "20px",
                        "border-radius": "0.5rem",
                    },
                ),
                html.Div(
                    [
                        dmc.Title(
                            "Intensity Profiles", c="#63aa47", size="h3"
                        ),
                        dcc.Graph(
                            id="intensity_profiles",
                            figure={},
                            style={
                                "margin-top": "20px",
                                "margin-bottom": "20px",
                                "border-radius": "0.5rem",
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
    dash.dependencies.Output("rois-graph", "figure"),
    dash.dependencies.Output("my-dropdown1", "options"),
    [
        dash.dependencies.Input("my-dropdown1", "value"),
    ],
)
def callback_test4(*args, **kwargs):
    image_omero = kwargs["session_state"]["context"]["image"]
    imaaa = image_omero[0, 0, :, :, int(args[0][-1])] / 255
    df_rects = kwargs["session_state"]["context"]["df_rects"]
    df_lines = kwargs["session_state"]["context"]["df_lines"]
    df_points = kwargs["session_state"]["context"]["df_points"]
    df_point_channel = df_points[df_points["C"] == int(args[0][-1])].copy()
    channel_names = kwargs["session_state"]["context"]["channel_names"]
    channel_list = [
        {"label": c.name, "value": f"channel {i}"}
        for i, c in enumerate(channel_names.channels)
    ]
    fig = go.Figure()
    fig.add_trace(go.Surface(z=imaaa.tolist(), colorscale="hot"))
    fig.update_scenes(aspectratio=dict(x=1, y=1, z=0.7), aspectmode="manual")
    # Add dropdowns
    fig.update_layout(
        height=imaaa.shape[0] + 150,
        autosize=False,
        margin=dict(t=30, b=30, l=0, r=0),
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
                color="Green",
                width=1,
                dash="dot",
            ),
        )
        for i, row in df_lines.iterrows()
    ]
    button_layer_1_height = 1.08
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=list(
                    [
                        dict(
                            args=["colorscale", "Hot"],
                            label="Hot",
                            method="restyle",
                        ),
                        dict(
                            args=["colorscale", "Viridis"],
                            label="Viridis",
                            method="restyle",
                        ),
                        dict(
                            args=["colorscale", "Cividis"],
                            label="Cividis",
                            method="restyle",
                        ),
                        dict(
                            args=["colorscale", "Blues"],
                            label="Blues",
                            method="restyle",
                        ),
                        dict(
                            args=["colorscale", "Greens"],
                            label="Greens",
                            method="restyle",
                        ),
                    ]
                ),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top",
            ),
            dict(
                buttons=list(
                    [
                        dict(
                            args=["reversescale", False],
                            label="False",
                            method="restyle",
                        ),
                        dict(
                            args=["reversescale", True],
                            label="True",
                            method="restyle",
                        ),
                    ]
                ),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.30,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top",
            ),
            dict(
                buttons=list(
                    [
                        dict(
                            args=[
                                {
                                    "contours.showlines": False,
                                    "type": "contour",
                                }
                            ],
                            label="Hide lines",
                            method="restyle",
                        ),
                        dict(
                            args=[
                                {
                                    "contours.showlines": True,
                                    "type": "contour",
                                    "contours.showlabels": True,
                                    "contours.labelfont.size": 12,
                                    "contours.labelfont.color": "white",
                                }
                            ],
                            label="Show lines",
                            method="restyle",
                        ),
                        dict(
                            args=[{"type": "heatmap"}],
                            label="Heatmap",
                            method="restyle",
                        ),
                    ]
                ),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.50,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top",
            ),
            dict(
                buttons=list(
                    [
                        dict(
                            label="None",
                            method="relayout",
                            args=["shapes", []],
                        ),
                        dict(
                            label="Corners",
                            method="relayout",
                            args=["shapes", corners],
                        ),
                        dict(
                            label="Lines",
                            method="relayout",
                            args=["shapes", lines],
                        ),
                        dict(
                            label="All",
                            method="relayout",
                            args=["shapes", corners + lines],
                        ),
                    ]
                ),
                direction="down",
                pad={
                    "r": 10,
                    "t": 10,
                },
                showactive=True,
                x=0.70,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top",
            ),
            dict(
                buttons=list(
                    [
                        dict(
                            args=["type", "heatmap"],
                            label="Heatmap",
                            method="restyle",
                        ),
                        dict(
                            args=["type", "surface"],
                            label="3D Surface",
                            method="restyle",
                        ),
                    ]
                ),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.87,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top",
            ),
        ]
    )
    fig.update_layout(
        annotations=[
            dict(
                text="colorscale",
                x=0,
                xref="paper",
                y=1.06,
                yref="paper",
                align="left",
                showarrow=False,
            ),
            dict(
                text="Reverse<br>Colorscale",
                x=0.23,
                xref="paper",
                y=1.07,
                yref="paper",
                showarrow=False,
            ),
            dict(
                text="Lines",
                x=0.46,
                xref="paper",
                y=1.06,
                yref="paper",
                showarrow=False,
            ),
            dict(
                text="Shapes",
                x=0.64,
                xref="paper",
                y=1.06,
                yref="paper",
                showarrow=False,
            ),
            dict(
                text="Type",
                x=0.85,
                xref="paper",
                y=1.06,
                yref="paper",
                showarrow=False,
            ),
        ]
    )

    return fig, channel_list


@dash_app_image.expanded_callback(
    dash.dependencies.Output("intensity_profiles", "figure"),
    [dash.dependencies.Input("my-dropdown1", "value")],
)
def callback_test5(*args, **kwargs):
    df_intensity_profiles = kwargs["session_state"]["context"][
        "df_intensity_profiles"
    ]
    ch = "ch0" + args[0][-1]
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
    fig = px.line(df_profile)
    return fig
