import dash_mantine_components as dmc
from django_plotly_dash import DjangoDash

from omero_metrics.dash_apps.dataset_image import dataset_shared_components as dsc
from omero_metrics.styles import CONTAINER_STYLE, MANTINE_THEME

dashboard_name = "omero_dataset_stage_drift"

omero_dataset_stage_drift = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)


omero_dataset_stage_drift.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dsc.notifications_container(),
        dsc.confirm_delete_modal(),
        dsc.dataset_header(
            "Stage Drift",
            "Stage Drift Analysis Dashboard",
            "Stage Drift Analysis",
        ),
        dmc.Container(
            children=[
                dsc.blank_input(),
                dsc.dataset_table_paper(),
            ],
            style=CONTAINER_STYLE,
        ),
    ],
)


# Register shared callbacks
dsc.register_delete_dataset_callback(omero_dataset_stage_drift)
dsc.register_download_datasets_callback(omero_dataset_stage_drift)
dsc.register_update_kkm_table_callback(omero_dataset_stage_drift)
dsc.register_download_table_callback(omero_dataset_stage_drift)
dsc.register_delete_button_loading_callback(omero_dataset_stage_drift)
