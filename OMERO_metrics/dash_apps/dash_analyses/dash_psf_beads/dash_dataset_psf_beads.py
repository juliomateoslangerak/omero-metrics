import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from OMERO_metrics.styles import THEME, HEADER_PAPER_STYLE, MANTINE_THEME


def get_icon(icon, size=20, color=None):
    return DashIconify(icon=icon, height=size, color=color)


dashboard_name = "omero_dataset_psf_beads"

omero_dataset_psf_beads = DjangoDash(
    name=dashboard_name,
    external_stylesheets=dmc.styles.ALL,
)


omero_dataset_psf_beads.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dmc.Paper(
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
                                            c=THEME["text"]["secondary"],
                                            size="sm",
                                        ),
                                    ],
                                    gap="xs",
                                ),
                            ],
                        ),
                        dmc.Group(
                            [
                                dmc.Button(
                                    id="download_dataset_data",
                                    children="Download",
                                    color="blue",
                                    variant="filled",
                                    leftSection=DashIconify(
                                        icon="ic:round-cloud-download"
                                    ),
                                ),
                                dmc.Button(
                                    id="delete_dataset_data",
                                    children="Delete",
                                    color="red",
                                    variant="filled",
                                    leftSection=DashIconify(
                                        icon="ic:round-delete-forever"
                                    ),
                                ),
                                dmc.Badge(
                                    "PSF Beads Analysis",
                                    color=THEME["primary"],
                                    variant="dot",
                                    size="lg",
                                ),
                            ]
                        ),
                    ],
                    justify="space-between",
                ),
            ],
            **HEADER_PAPER_STYLE,
        ),
        dmc.Container(
            [
                html.Div(id="blank-input"),
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


@omero_dataset_psf_beads.expanded_callback(
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
