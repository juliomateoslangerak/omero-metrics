import dash
from dash import dcc, html
from django_plotly_dash import DjangoDash
from ..tools.data_preperation import *
import dash_mantine_components as dmc

colorscales = px.colors.named_colorscales()

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
                        dmc.GridCol(
                            [
                                html.H3(
                                    "Select The Color Scale",
                                    style={"color": "#63aa47"},
                                ),
                                dcc.Dropdown(
                                    id="dropdownColorScale",
                                    options=colorscales,
                                    value="hot",
                                ),
                            ],
                            span="auto",
                        ),
                        dmc.GridCol(
                            [
                                html.H3(
                                    "Add Rois", style={"color": "#63aa47"}
                                ),
                                dcc.RadioItems(
                                    options=["Raw Image", "ROIS Image"],
                                    value="Raw Image",
                                    inline=True,
                                    id="rois-radio",
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
        dash.dependencies.Input("rois-radio", "value"),
        dash.dependencies.Input("dropdownColorScale", "value"),
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
    fig = px.imshow(imaaa, zmin=0, zmax=255, color_continuous_scale=args[2])
    fig1 = px.imshow(imaaa, zmin=0, zmax=255, color_continuous_scale=args[2])
    fig1 = add_rect_rois(go.Figure(fig1), df_rects)
    fig1 = add_line_rois(go.Figure(fig1), df_lines)
    fig1 = add_point_rois(go.Figure(fig1), df_point_channel)
    if args[1] == "Raw Image":
        return fig, channel_list
    elif args[1] == "ROIS Image":
        return fig1, channel_list
    else:
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
