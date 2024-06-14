import dash
import dash_mantine_components as dmc
import plotly.express as px
from dash import dcc, html
from django_plotly_dash import (
    DjangoDash,
)

from ..tools.data_preperation import (
    crop_bead_index,
    image_3d_chart,
)

app = DjangoDash("PSF_Beads_image")

app.layout = dmc.MantineProvider(
    children=[
        dmc.Container(
            [
                html.Div(
                    id="blank-input",
                    children=[],
                ),
                dmc.Stack(
                    [
                        dmc.Center(
                            dmc.Text(
                                "PSF Beads Dashboard for Image",
                                mb=30,
                                style={
                                    "margin-top": "20px",
                                    "fontSize": 40,
                                },
                            ),
                        ),
                        dcc.Dropdown(
                            value="Channel 0",
                            id="channel_ddm_psf",
                        ),
                        dcc.Dropdown(
                            value="Bead 0",
                            id="bead_ddm_psf",
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
                        dcc.Graph(
                            id="projection_graph",
                            figure={},
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
    dash.dependencies.Output("bead_ddm_psf", "options"),
    [
        dash.dependencies.Input("channel_ddm_psf", "value"),
        dash.dependencies.Input("bead_ddm_psf", "value"),
    ],
)
def update_image(*args, **kwargs):
    global image_bead
    image_omero = kwargs["session_state"]["context"]["image"]
    channel_index = int(args[0].split(" ")[-1])
    channel_options = [
        {
            "label": f"Channel {i}",
            "value": f"Channel {i}",
        }
        for i in range(image_omero.shape[4])
    ]
    bead_index = int(args[1].split(" ")[-1])
    bead_properties_df = kwargs["session_state"]["context"][
        "bead_properties_df"
    ]
    df_beads_location = bead_properties_df[
        bead_properties_df["channel_nr"] == channel_index
    ][
        [
            "channel_nr",
            "bead_nr",
            "considered_axial_edge",
            "z_centroid",
            "y_centroid",
            "x_centroid",
        ]
    ].copy()
    bead_options = [
        {
            "label": f"Bead {i}",
            "value": f"Bead {i}",
        }
        for i in df_beads_location["bead_nr"]
    ]
    bead = df_beads_location[df_beads_location["bead_nr"] == bead_index].copy()
    stack = image_omero[0, :, :, :, channel_index]
    x0, xf, y0, yf, _ = crop_bead_index(bead, 20, stack)
    image_bead = stack[:, y0:yf, x0:xf]
    fig = image_3d_chart(image_bead)
    fig = fig.update_layout(scene=dict(xaxis_showspikes=False))
    return (
        fig,
        channel_options,
        bead_options,
    )


@app.expanded_callback(
    dash.dependencies.Output("projection_graph", "figure"),
    [
        dash.dependencies.Input("image", "clickData"),
    ],
    prevent_initial_call=True,
)
def projection_callback(*args, **kwargs):
    points = args[0]["points"][0]
    proj_click = px.imshow(
        image_bead[
            int(points["x"]),
            : int(points["y"]),
            : int(points["z"]),
        ]
    )
    return proj_click
