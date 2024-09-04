import dash
import pandas as pd
from dash import dcc, html, dash_table
from django_plotly_dash import DjangoDash
import plotly.express as px
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from datetime import datetime
import plotly.graph_objects as go
from skimage.exposure import rescale_intensity

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
dashboard_name = "omero_dataset_metrics"
dash_app_dataset = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=stylesheets,
    external_scripts=external_scripts,
)

dash_app_dataset.layout = dmc.MantineProvider(
    [
        dmc.Container(
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
                dmc.Grid(
                    id="group_image",
                    justify="space-between",
                    align="center",
                    style={
                        "margin-top": "10px",
                        "background-color": "white",
                        "border-radius": "0.5rem",
                        "padding": "10px",
                    },
                    children=[
                        dmc.GridCol(
                            [

                                dmc.Select(
                                    id="channel_dropdown_foi",
                                    label="Select Channel",
                                    w="300",
                                    value="channel 0",
                                    leftSection=DashIconify(
                                        icon="radix-icons:magnifying-glass"
                                    ),
                                    rightSection=DashIconify(
                                        icon="radix-icons:chevron-down"
                                    ),
                                ),

                                dcc.Graph(
                                    id="intensity_map",
                                    style={
                                        "display": "inline-block",
                                        "width": "100%",
                                        "height": "100%",
                                    },
                                ),
                            ],
                            span="6",
                        ),
                        dmc.GridCol(
                            [
                                dmc.Center(
                                    [
                                        dmc.Text(
                                            "Key Measurements",
                                            size="md",
                                            c="#63aa47",
                                            style={
                                                "margin-bottom": "30px",
                                                "margin-left": "20px",
                                            },
                                        )
                                    ]
                                ),
                                dmc.Table(
                                    id="km_table",
                                    striped=True,
                                    highlightOnHover=True,
                                    className="table table-striped table-bordered",
                                ),
                            ],
                            span="6",
                        ),
                    ],
                ),
                html.Div(id="blank-input"),
                dmc.Stack(
                    id="table",
                    children=[
                        dmc.Center(
                            dmc.Text(
                                "Intensity Profiles",
                                size="md",
                                c="#63aa47",
                            )
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
                    ],
                    style={
                        "margin-top": "10px",
                        "background-color": "white",
                        "border-radius": "0.5rem",
                        "padding": "10px",
                    },
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


@dash_app_dataset.expanded_callback(
    dash.dependencies.Output("channel_dropdown_foi", "data"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_dropdow_menu(*args, **kwargs):
    channel = kwargs["session_state"]["context"]["channel_names"]

    channel_list = [
        {"label": c.name, "value": f"channel {i}"}
        for i, c in enumerate(channel.channels)
    ]
    data = [{"group": "Channels", "items": channel_list}]
    return data


@dash_app_dataset.expanded_callback(
    dash.dependencies.Output("km_table", "data"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_km_table(*args, **kwargs):
    table = kwargs["session_state"]["context"]["key_values_df"]
    table_kkm = table[
        [
            "channel_name",
            "image_name",
            "center_region_intensity_fraction",
            "center_region_area_fraction",
            "max_intensity",
        ]
    ].copy()
    table_kkm = table_kkm.round(3)
    table_kkm.columns = table_kkm.columns.str.replace("_", " ").str.title()
    data = {
        "head": table_kkm.columns.tolist(),
        "body": table_kkm.values.tolist(),
        "caption": "Key Measurements for the selected dataset",
    }
    return data


@dash_app_dataset.expanded_callback(
    dash.dependencies.Output("intensity_map", "figure"),
    dash.dependencies.Output("intensity_profile", "data"),
    [dash.dependencies.Input("channel_dropdown_foi", "value")],
)
def dataset_callback_intensity_map(*args, **kwargs):
    images = kwargs["session_state"]["context"]["image"]
    df_intensity_profiles = kwargs["session_state"]["context"][
        "intensity_profiles"
    ]
    channel = int(args[0][-1])
    image_channel = images[0, 0, :, :, channel]
    image_channel = rescale_intensity(image_channel, in_range='image', out_range=(0.0, 1.0))
    channel_regx = "Ch0" + str(channel)
    df_profile = df_intensity_profiles[
        df_intensity_profiles.columns[
            df_intensity_profiles.columns.str.startswith(channel_regx)
        ]
    ].copy()
    df_profile.columns = df_profile.columns.str.replace(
        "Ch\d{2}_", "", regex=True
    )
    df_profile = restyle_dataframe(df_profile, "columns")
    df_new = df_profile.reset_index()
    fig = px.imshow(
        image_channel,
        zmin=image_channel.min(),
        zmax=image_channel.max(),
        color_continuous_scale="hot",
    )
    fig.update_layout(
        xaxis_title="X",
        yaxis_title="Y",
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        xaxis_zeroline=False,
        yaxis_zeroline=False,
    )
    fig.update_layout(title={'text':"Intensity Map", 'x': 0.5, 'xanchor': 'center',
                             'font': {"family" :"Arial", "size": 18, 'color': '#63aa47'}})
    return (fig, df_new.to_dict("records"))


def restyle_dataframe(df: pd.DataFrame, col: str) -> pd.DataFrame:
    value = getattr(df, col).str.replace("_", " ", regex=True).str.title()
    setattr(
        df, col, value
    )  # TODO: replace setattr with df.loc[:, col] = value
    return df


# dmc.GridCol([dmc.Center([dmc.Text("Key Measurements", size="md")]),
#                          table2, dmc.Center([dmc.Text("Key Measurements for Field of Illumination", c="dimmed",
#                         size="sm")])]

#
# table2 = dash_table.DataTable(
#     data=table_kkm.to_dict('records'),
#     columns=[{"name": i, "id": i} for i in table_kkm.columns],
#     style_table={"overflowX": "auto",
#                  "padding": "10px",
#                  "background": "white",
#                  "border": "thin, white, solid",
#
#                  },
#     page_size=10,
#     editable=False,
#     style_cell={
#         "textAlign": "center",
#         "fontSize": 10,
#         "font-family": "Roboto",
#         "border": "thin, white, solid",
#         "border-bottom": 'thin #dee2e6 solid'
#
#     },
#     style_header={
#         "fontWeight": "bold",
#         "font-family": "Roboto",
#
#         "fontSize": 12,
#         "textAlign": "center",
#         "border": "thin, white, solid",
#         "border-bottom": 'thin #dee2e6 solid'
#     },
#
# )
