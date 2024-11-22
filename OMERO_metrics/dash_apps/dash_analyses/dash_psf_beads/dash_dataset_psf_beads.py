import dash
from dash import dcc, html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from linkml_runtime.dumpers import YAMLDumper
from OMERO_metrics.styles import THEME, HEADER_PAPER_STYLE, MANTINE_THEME
from OMERO_metrics import views
from time import sleep
import math
from OMERO_metrics.styles import TABLE_MANTINE_STYLE


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
        dmc.NotificationProvider(position="top-center"),
        html.Div(id="notifications-container"),
        dmc.Modal(
            title="Confirm Delete",
            id="confirm_delete",
            children=[
                dmc.Text(
                    "Are you sure you want to delete this dataset outputs?"
                ),
                dmc.Space(h=20),
                dmc.Group(
                    [
                        dmc.Button(
                            "Submit",
                            id="modal-submit-button",
                            color="red",
                        ),
                        dmc.Button(
                            "Close",
                            color="gray",
                            variant="outline",
                            id="modal-close-button",
                        ),
                    ],
                    justify="flex-end",
                ),
            ],
        ),
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
                                dcc.Download(id="download"),
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
                                            style=TABLE_MANTINE_STYLE,
                                        ),
                                        dmc.Group(
                                            mt="md",
                                            children=[
                                                dmc.Pagination(
                                                    id="pagination",
                                                    total=0,
                                                    value=1,
                                                    withEdges=True,
                                                )
                                            ],
                                            justify="center",
                                        ),
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
    dash.dependencies.Output("pagination", "total"),
    [
        dash.dependencies.Input("pagination", "value"),
    ],
)
def func_psf_callback(*args, **kwargs):
    table_km = kwargs["session_state"]["context"]["bead_km_df"]
    page = int(args[0])
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
    total = math.ceil(len(table_kkm) / 4)
    start_idx = (page - 1) * 4
    end_idx = start_idx + 4
    table_page = table_kkm.iloc[start_idx:end_idx]
    data = {
        "head": table_page.columns.tolist(),
        "body": table_page.values.tolist(),
        "caption": "Key Measurements for the selected dataset",
    }
    return data, total


@omero_dataset_psf_beads.expanded_callback(
    dash.dependencies.Output("confirm_delete", "opened"),
    dash.dependencies.Output("notifications-container", "children"),
    [
        dash.dependencies.Input("delete_dataset_data", "n_clicks"),
        dash.dependencies.Input("modal-submit-button", "n_clicks"),
        dash.dependencies.Input("modal-close-button", "n_clicks"),
        dash.dependencies.State("confirm_delete", "opened"),
    ],
    prevent_initial_call=True,
)
def delete_dataset(*args, **kwargs):
    triggered_button = kwargs["callback_context"].triggered[0]["prop_id"]
    dataset_id = kwargs["session_state"]["context"]["dataset_id"]
    request = kwargs["request"]
    opened = not args[3]
    if triggered_button == "modal-submit-button.n_clicks" and args[0] > 0:
        sleep(1)
        msg, color = views.delete_dataset(request, dataset_id=dataset_id)
        message = dmc.Notification(
            title="Notification!",
            id="simple-notify",
            action="show",
            message=msg,
            icon=DashIconify(
                icon=(
                    "akar-icons:circle-check"
                    if color == "green"
                    else "akar-icons:circle-x"
                )
            ),
            color=color,
        )
        return opened, message
    else:
        return opened, None


@omero_dataset_psf_beads.expanded_callback(
    dash.dependencies.Output("download", "data"),
    [dash.dependencies.Input("download_dataset_data", "n_clicks")],
    prevent_initial_call=True,
)
def download_dataset_data(*args, **kwargs):
    mm_dataset = kwargs["session_state"]["context"]["mm_dataset"]
    dumper = YAMLDumper()
    return dict(content=dumper.dumps(mm_dataset), filename="dataset.yaml")
