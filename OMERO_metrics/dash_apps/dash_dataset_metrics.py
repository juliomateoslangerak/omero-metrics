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
    name=dashboard_name, serve_locally=True, external_stylesheets=stylesheets,
)

dash_app_dataset.layout = dmc.MantineProvider(
    [
        dmc.Container(
            [
                dmc.Center(
                    [dmc.Text(
                        id="title",
                        c=primary_color,
                        style={"fontSize": 30},
                    ),
                    dmc.Group([html.Img(src="./assets/images/logo.png", style={"width": "100px"}),
                               dmc.Text("OMERO Metrics Dashboard", c=primary_color,
                           style={"fontSize": 15},)])

                    ]
                ),
                dmc.Divider(variant="solid", mb=20),
                html.Div(id='timeline'),
                html.Div(id='input_timeline'),
                dmc.Divider(variant="solid", mb=20, mt=20),
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                html.H3(
                                    "Select Channel",
                                    style={"color": primary_color},
                                ),
                                dcc.Dropdown(
                                    id="channel_ddm",
                                    value="channel 0",
                                    clearable=False,
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
                dmc.Stack(
                    [
                        dmc.Grid(
                            [
                                dmc.GridCol(
                                    [
                                        dmc.Title(
                                            "Intensity Map",
                                            c=primary_color,
                                            size="h3",
                                            mb=10,
                                        ),
                                        dcc.Graph(
                                            id="dataset_image_graph",
                                            figure={},
                                            style={
                                                "display": "inline-block",
                                                "width": "100%",
                                                "height": "100%;",
                                            },
                                        ),
                                    ],
                                    span="6",
                                ),
                                dmc.GridCol(
                                    [
                                        dmc.Title(
                                            "Key Measurements",
                                            c=primary_color,
                                            size="h3",
                                            mb=10,
                                            mt=10,
                                        ),
                                        dash_table.DataTable(
                                            id="table",
                                            page_size=10,
                                            sort_action="native",
                                            sort_mode="multi",
                                            sort_as_null=["", "No"],
                                            sort_by=[
                                                {
                                                    "column_id": "pop",
                                                    "direction": "asc",
                                                }
                                            ],
                                            editable=False,
                                            style_cell={
                                                "textAlign": "left",
                                                "fontSize": 14,
                                                "font-family": "sans-serif",
                                            },
                                            style_header={
                                                "backgroundColor": primary_color,
                                                "fontWeight": "bold",
                                                "fontSize": 18,
                                                "textAlign": "center",
                                            },
                                            style_table={
                                                "overflowX": "auto",
                                                "border-radius": "0.5rem",
                                            },
                                        ),
                                    ],
                                    span="6",
                                ),
                            ]
                        ),
                        dmc.Divider(variant="solid"),
                        dmc.Stack(
                            [
                                dmc.Title(
                                    "Intensity Profile",
                                    c=primary_color,
                                    size="h3",
                                    mb=10,
                                ),
                                dmc.LineChart(
                                    id="intensity_profile",
                                    h=400,
                                    dataKey="Pixel",
                                    data={},
                                    series=[
                                        {
                                            "name": "Lefttop To Rightbottom",
                                            "color": "violet.6",
                                        },
                                        {
                                            "name": "Leftbottom To Righttop",
                                            "color": "blue.6",
                                        },
                                        {
                                            "name": "Center Horizontal",
                                            "color": "teal.6",
                                        },
                                        {
                                            "name": "Center Vertical",
                                            "color": "indigo.6",
                                        },
                                    ],
                                    xAxisLabel="Pixel",
                                    yAxisLabel="Pixel Intensity",
                                    tickLine="y",
                                    gridAxis="y",
                                    withXAxis=True,
                                    withYAxis=True,
                                    withLegend=True,
                                    strokeWidth=3,
                                    withDots=False,
                                    curveType="natural",
                                    style={
                                        "margin-top": "20px",
                                        "background-color": "white",
                                    },
                                ),
                            ]
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
        ),
    ],
    theme={"colorScheme": "mild"},

)


@dash_app_dataset.expanded_callback(
    dash.dependencies.Output("timeline", "children"),
    dash.dependencies.Input("input_timeline", "children"), )
def timeline_function(*args, **kwargs):
    timeline_items = kwargs["session_state"]["context"]["timeline_data"]
    table = kwargs["session_state"]["context"]["key_values_df"]
    table = table[["image_name", "channel_name","center_region_intensity_fraction" , "center_region_area_fraction"]].copy()
    timeline = dmc.Timeline(
        active=len(timeline_items),
        bulletSize=15,
        lineWidth=2,
        children=[
            dmc.TimelineItem(
                title=item['name'],
                children=[
                    dmc.Text([
                        item['description'],
                        "\n",
                        "( Acquisition date: ",
                        dmc.Anchor(datetime.strptime(item["acquisition_datetime"], "%Y-%m-%dT%H:%M:%S").date(), href="#", size="sm"), " )"],
                        c="dimmed",
                        size="sm",
                    )
                ],
               )
            for item in timeline_items
        ],
        style={"background-color": "white", "border-radius": "0.5rem", "padding": "10px"},
    )
    return [dmc.Group(
        [
            timeline,
            dcc.Graph(
                figure=go.Figure(
                    data=[
                        go.Table(
                            header=dict(values=list(table.columns)),
                            cells=dict(values=[table[col] for col in table.columns])
                        )
                    ]
                )
            )
        ],
        gap="md",
        grow=True,
        justify="space-around",
        style={"margin-top": "20px"}
    )]

@dash_app_dataset.expanded_callback(
    dash.dependencies.Output("dataset_image_graph", "figure"),
    dash.dependencies.Output("channel_ddm", "options"),
    dash.dependencies.Output("title", "children"),
    dash.dependencies.Output("table", "data"),
    dash.dependencies.Output("intensity_profile", "data"),
    [dash.dependencies.Input("channel_ddm", "value")],
)
def dataset_callback_intensity_map(*args, **kwargs):
    title = kwargs["session_state"]["context"]["title"]
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
    imaaa = images[0, 0, :, :, int(args[0][-1])] / 255
    fig = px.imshow(
        imaaa,
        zmin=imaaa.min(),
        zmax=imaaa.max(),
        color_continuous_scale="gray",
    )
    C = "Ch0" + args[0][-1]
    df_profile = df_intensity_profiles[
        df_intensity_profiles.columns[
            df_intensity_profiles.columns.str.startswith(C)
        ]
    ].copy()
    df_profile.columns = df_profile.columns.str.replace(
        "Ch\d{2}_", "", regex=True
    )
    df_profile = restyle_dataframe(df_profile, "columns")
    extracted_table_cols = channel_list[int(args[0][-1])]["label"]
    table_filtered = table[["Measurements", extracted_table_cols]]
    table_filtered = restyle_dataframe(table_filtered, "Measurements")
    fig_ip = px.line(
        df_profile,
        x=df_profile.index,
        y=df_profile.columns,
        title="Intensity Profile",
    )
    df_reset = df_profile.reset_index()
    df_reset.rename(columns={"index": "Pixel"}, inplace=True)
    return (
        fig,
        channel_list,
        title,
        table_filtered.to_dict("records"),
        df_reset.to_dict("records"),
    )


def restyle_dataframe(df: pd.DataFrame, col: str) -> pd.DataFrame:
    value = getattr(df, col).str.replace("_", " ", regex=True).str.title()
    setattr(
        df, col, value
    )  # TODO: replace setattr with df.loc[:, col] = value
    return df
