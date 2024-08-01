import dash
import pandas as pd
from dash import dcc, html, dash_table
from django_plotly_dash import DjangoDash
import plotly.express as px
import dash_mantine_components as dmc
from datetime import datetime
import plotly.graph_objects as go

stylesheets = [
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "./assets/omero_metrics.css",
]
primary_color = "#63aa47"
dashboard_name = "omero_dataset_metrics"
dash_app_dataset = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=stylesheets,
)

dash_app_dataset.layout = dmc.MantineProvider(
    [dmc.Container(
            [
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
                dmc.Grid(id="group_image",
                         justify="space-between",
                         align="center",
                         style={"margin-top": "10px", "background-color": "white",
                                "border-radius": "0.5rem", "padding": "10px", }

                         ),
                html.Div(id="blank-input"),

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



@dash_app_dataset.expanded_callback(
    dash.dependencies.Output("group_image", "children"),
    [dash.dependencies.Input("blank-input", "children")],
)
def dataset_callback_intensity_map(*args, **kwargs):
    table = kwargs["session_state"]["context"]["key_values_df"]
    images = kwargs["session_state"]["context"]["image"]
    df_intensity_profiles = kwargs["session_state"]["context"][
        "intensity_profiles"
    ]
    channel_names = kwargs["session_state"]["context"]["channel_names"]
    channel_list = [
        {"label": c.name, "value": f"channel {i}"}
        for i, c in enumerate(channel_names.channels)
    ]
    #int(args[0][-1])
    image_channel = images[0, 0, :, :, 0]
    image_channel = 255 * image_channel / image_channel.max()
    #fig = go.Figure()
    #fig.add_trace(go.Heatmap(z=image_channel.tolist(), colorscale="Hot"))

    fig = px.imshow(
        image_channel,
        zmin=image_channel.min(),
        zmax=image_channel.max(),
        color_continuous_scale="hot",
    )
    fig.update_layout(
        title="Intensity map",
        xaxis_title="X",
        yaxis_title="Y",
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        xaxis_zeroline=False,
        yaxis_zeroline=False,

    )
    graph = dcc.Graph(figure=fig, style={"display": "inline-block", "width": "100%", "height": "100%"})
    table_kkm = table[[
        "channel_name",
        "image_name",
        "center_region_intensity_fraction",
        "center_region_area_fraction",
        "max_intensity"
    ]].copy()
    table_kkm = table_kkm.round(3)
    table_kkm.columns = table_kkm.columns.str.replace("_", " ").str.title()
    table_object = dmc.Table(
        striped=True,
        highlightOnHover=True,
        data={
            "caption": "Key Measurements for the selected dataset",
            "head": table_kkm.columns.tolist(),
            "body": table_kkm.values.tolist(),
        },
    )
    table2 = dash_table.DataTable(
        table_kkm.to_dict('records'),
        [{"name": i, "id": i} for i in table_kkm.columns],
        style_table={"overflowX": "auto",
                     "padding": "10px",
                     "background": "white",
                     "border": "thin, white, solid",

                     },
        page_size=10,
        editable=False,
        style_cell={
            "textAlign": "center",
            "fontSize": 10,
            "font-family": "Roboto",
            "border" : "thin, white, solid",
            "border-bottom":'thin #dee2e6 solid'

        },
        style_header={
            "fontWeight": "bold",
            "font-family": "Roboto",

            "fontSize": 12,
            "textAlign": "center",
            "border": "thin, white, solid",
            "border-bottom":'thin #dee2e6 solid'
        },

    )

    return [dmc.GridCol(graph, span="6",
                        ),
            dmc.GridCol([dmc.Center([dmc.Text("Key Measurements", size="md")]),
                         table2, dmc.Center([dmc.Text("Key Measurements for Field of Illumination", c="dimmed",
                        size="sm")])], span="6",
                        )]



