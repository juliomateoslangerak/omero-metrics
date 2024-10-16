import dash
from dash import dcc, html, dash_table
from django_plotly_dash import DjangoDash
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
content = dmc.Card(
    children=[
        dmc.Group(
            [
                dmc.Badge("Filled badge", variant="filled", color="lime"),
                dmc.Text("Total Number of Beads", fw=800),
            ],
            justify="space-between",
            mt="md",
            mb="xs",
        ),
        dmc.Center(dmc.Badge(1, size="xl", circle=True)),
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    w="auto",
)
app = DjangoDash(
    "PSF_Beads",
    external_stylesheets=stylesheets,
)


app.layout = dmc.MantineProvider(
    [
        dmc.Container(
            [
                dmc.Center(
                    [
                        dmc.Group(
                            [
                                html.Img(
                                    src="./assets/images/logo.png",
                                    style={"width": "100px"},
                                ),
                                dmc.Title(
                                    "PSF Beads Dashboard",
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
                html.Div(
                    [
                        dmc.Stack(
                            [
                                dmc.Divider(variant="solid"),
                                dmc.Center(
                                    [
                                        dmc.Title(
                                            "Key Measurements",
                                            c="#189A35",
                                            size="h3",
                                            mb=10,
                                        ),
                                    ]
                                ),
                                dmc.ScrollArea(
                                    [
                                        dmc.Table(
                                            id="key_values_psf",
                                            striped=True,
                                            highlightOnHover=True,
                                            className="table table-striped table-bordered",
                                            styles={
                                                "background-color": "white",
                                                "width": "auto",
                                                "height": "auto",
                                                "overflow-X": "auto",
                                            },
                                        )
                                    ]
                                ),
                            ]
                        )
                    ],
                    style={
                        "background-color": "white",
                        "border-radius": "0.5rem",
                        "padding": "10px",
                    },
                ),
                dmc.Divider(variant="solid"),
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


@app.expanded_callback(
    dash.dependencies.Output("key_values_psf", "data"),
    [
        dash.dependencies.Input("blank-input", "children"),
    ],
)
def func_psf_callback(*args, **kwargs):
    table_km = kwargs["session_state"]["context"]["bead_km_df"]
    kkm = [
        "channel_name",
        "considered_valid_count",
        "intensity_max_median",
        "intensity_max_std",
        "intensity_min_mean",
        "intensity_min_median",
        "intensity_min_std",
        "intensity_std_mean",
        "intensity_std_median",
        "intensity_std_std",
    ]
    table_kkm = table_km[kkm].copy()
    table_kkm = table_kkm.round(3)
    table_kkm.columns = table_kkm.columns.str.replace("_", " ").str.title()
    data = {
        "head": table_kkm.columns.tolist(),
        "body": table_kkm.values.tolist(),
        "caption": "Key Measurements for the selected dataset",
    }
    return data
