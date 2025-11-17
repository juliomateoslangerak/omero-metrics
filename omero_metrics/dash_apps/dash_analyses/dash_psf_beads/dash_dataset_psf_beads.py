import dash
from dash import dcc, html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from omero_metrics.styles import THEME, MANTINE_THEME
from omero_metrics import views
from time import sleep
import math
from omero_metrics.styles import TABLE_MANTINE_STYLE
import omero_metrics.dash_apps.dash_utils.omero_metrics_components as my_components
from omero_metrics.tools import load

from omero_metrics.dash_apps.dash_analyses import dataset_shared_components as dsc

dashboard_name = "omero_dataset_psf_beads"

omero_dataset_psf_beads = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)


omero_dataset_psf_beads.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        # TODO: this headers can be shared across datasets
        dsc.notification_provider(),
        dsc.notifications_container(),
        dsc.confirm_delete_modal(),
        dsc.dataset_header_paper(
            "PSF Beads", "PSF Beads Analysis Dashboard", "PSF Beads Analysis"
        ),
        dmc.Container(
            [
                html.Div(id="blank-input"),
                # TODO: key-measurements should be shared across dataset interfaces
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
                                        dmc.Group(
                                            [
                                                my_components.download_table,
                                                dmc.Tooltip(
                                                    label="Statistical measurements for all the channels presented in the dataset",
                                                    children=[
                                                        my_components.get_icon(
                                                            icon="material-symbols:info-outline",
                                                            color=THEME["primary"],
                                                        )
                                                    ],
                                                ),
                                            ]
                                        ),
                                    ],
                                    justify="space-between",
                                ),
                                dmc.ScrollArea(
                                    [
                                        dmc.Table(
                                            id="key_measurements_psf",
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


# Register shared callbacks
dsc.register_delete_datasets_callback(omero_dataset_psf_beads)
dsc.register_download_datasets_callback(omero_dataset_psf_beads)


@omero_dataset_psf_beads.expanded_callback(
    dash.dependencies.Output("key_measurements_psf", "data"),
    dash.dependencies.Output("pagination", "total"),
    [
        dash.dependencies.Input("pagination", "value"),
    ],
)
def func_psf_callback(pagination_value, **kwargs):
    table_km = load.get_km_mm_metrics_dataset(
        mm_dataset=kwargs["session_state"]["context"]["mm_dataset"],
        table_name="key_measurements",
    )
    kkm = kwargs["session_state"]["context"]["kkm"]
    page = int(pagination_value)
    table_kkm = table_km.filter(["channel_name", *kkm])
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


# TODO: can be shared across dataset interfaces
@omero_dataset_psf_beads.expanded_callback(
    dash.dependencies.Output("table-download", "data"),
    [
        dash.dependencies.Input("table-download-csv", "n_clicks"),
        dash.dependencies.Input("table-download-xlsx", "n_clicks"),
        dash.dependencies.Input("table-download-json", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def download_table_data(*args, **kwargs):
    if not kwargs["callback_context"].triggered:
        raise dash.no_update

    triggered_id = kwargs["callback_context"].triggered[0]["prop_id"].split(".")[0]
    table_km = load.get_km_mm_metrics_dataset(
        mm_dataset=kwargs["session_state"]["context"]["mm_dataset"],
        table_name="key_measurements",
    )
    kkm = kwargs["session_state"]["context"]["kkm"]
    table_kkm = table_km.filter(["channel_name", *kkm])
    table_kkm = table_kkm.round(3)
    table_kkm.columns = table_kkm.columns.str.replace("_", " ").str.title()
    if triggered_id == "table-download-csv":
        return dcc.send_data_frame(table_kkm.to_csv, "km_table.csv")
    elif triggered_id == "table-download-xlsx":
        return dcc.send_data_frame(table_kkm.to_excel, "km_table.xlsx")
    elif triggered_id == "table-download-json":
        return dcc.send_data_frame(table_kkm.to_json, "km_table.json")
    raise dash.no_update


omero_dataset_psf_beads.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            return true;
        }
        return false;
    }
    """,
    dash.dependencies.Output(
        "confirm-delete-button", "loading", allow_duplicate=True
    ),
    dash.dependencies.Input("confirm-delete-button", "n_clicks"),
    prevent_initial_call=True,
)
