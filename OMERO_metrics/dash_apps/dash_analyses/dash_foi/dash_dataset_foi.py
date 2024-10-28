import dash
import pandas as pd
from dash import dcc, html
from django_plotly_dash import DjangoDash
import plotly.express as px
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from skimage.exposure import rescale_intensity


stylesheets = [
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
]
primary_color = "#63aa47"
dashboard_name = "omero_dataset_metrics"
dash_app_dataset = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=stylesheets,
)

dash_app_dataset.layout = dmc.MantineProvider(
    [
        dmc.Container(
            [
                dmc.Center(
                    [
                        dmc.Group(
                            [
                                html.Img(
                                    src="/static/OMERO_metrics/images/metrics_logo.png",
                                    style={"width": "100px"},
                                ),
                                dmc.Title(
                                    "Field Of Illumination Dashboard",
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
                                    clearable=False,
                                    w="300",
                                    value="0",
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
                                dmc.ScrollArea(
                                    [
                                        dmc.Table(
                                            id="km_table",
                                            striped=True,
                                            highlightOnHover=True,
                                            className="table table-striped table-bordered",
                                            styles={
                                                "background-color": "white",
                                                "width": "auto",
                                                "height": "auto",
                                            },
                                        )
                                    ]
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
def update_dropdown_menu(*args, **kwargs):
    channel = kwargs["session_state"]["context"]["channel_names"]

    channel_list = [
        {"label": channel_name, "value": f"{i}"}
        for i, channel_name in enumerate(channel)
    ]
    data = channel_list
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
            # "image_name",
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
    channel = int(args[0])
    image = images[channel]
    image_channel = image[0, 0, :, :]
    image_channel = rescale_intensity(
        image_channel, in_range=(0, image_channel.max()), out_range=(0.0, 1.0)
    )
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
    fig.update_layout(
        title={
            "text": "Intensity Map",
            "x": 0.5,
            "xanchor": "center",
            "font": {"family": "Arial", "size": 18, "color": "#63aa47"},
        }
    )
    return fig, df_new.to_dict("records")


def restyle_dataframe(df: pd.DataFrame, col: str) -> pd.DataFrame:
    value = getattr(df, col).str.replace("_", " ", regex=True).str.title()
    setattr(
        df, col, value
    )  # TODO: replace setattr with df.loc[:, col] = value
    return df
