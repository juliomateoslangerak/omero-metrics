import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from OMERO_metrics.styles import THEME, MANTINE_THEME


def get_icon(icon, size=20, color=None):
    return DashIconify(icon=icon, height=size, color=color)


app = DjangoDash(
    "PSF_Beads",
    external_stylesheets=dmc.styles.ALL,
)


app.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dmc.Container(
            [
                html.Div(id="blank-input"),
                # Header Section
                dmc.Paper(
                    shadow="sm",
                    p="md",
                    radius="lg",
                    mb="md",
                    children=[
                        dmc.Group(
                            [
                                dmc.Group(
                                    [
                                        html.Img(
                                            src="/static/OMERO_metrics/images/metrics_logo.png",
                                            style={
                                                "width": "120px",
                                                "height": "auto",
                                            },
                                        ),
                                        dmc.Stack(
                                            [
                                                dmc.Title(
                                                    "PSF Beads Analysis",
                                                    c=THEME["primary"],
                                                    size="h2",
                                                ),
                                                dmc.Text(
                                                    "PSF Beads Analysis Dashboard",
                                                    c=THEME["text"][
                                                        "secondary"
                                                    ],
                                                    size="sm",
                                                ),
                                            ],
                                            gap="xs",
                                        ),
                                    ],
                                ),
                                dmc.Badge(
                                    "PSF Beads Analysis",
                                    color="green",
                                    variant="dot",
                                    size="lg",
                                ),
                            ],
                            justify="space-between",
                        ),
                    ],
                ),
                dmc.Paper(
                    shadow="xs",
                    p="md",
                    radius="md",
                    mt="md",
                    children=[
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        dmc.Text(
                                            "Key Measurements",
                                            fw=500,
                                            size="lg",
                                        ),
                                        dmc.Tooltip(
                                            label="Statistical measurements for all the channels presented in the dataset",
                                            children=[
                                                get_icon(
                                                    "material-symbols:info-outline",
                                                    color=THEME["primary"],
                                                )
                                            ],
                                        ),
                                    ],
                                    justify="space-between",
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
                            ],
                            gap="xl",
                        ),
                    ],
                ),
            ],
            size="xl",
            p="md",
            style={"backgroundColor": THEME["surface"]},
        ),
    ],
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
