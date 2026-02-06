import dash
import dash_mantine_components as dmc
from django_plotly_dash import DjangoDash

from omero_metrics.dash_apps.dash_analyses import dataset_shared_components as dsc
from omero_metrics.styles import (
    CONTAINER_STYLE,
    MANTINE_THEME,
)

dashboard_name = "omero_dataset_psf_beads"

omero_dataset_psf_beads = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)


omero_dataset_psf_beads.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dsc.notification_provider(),
        dsc.notifications_container(),
        dsc.confirm_delete_modal(),
        dsc.dataset_header_paper(
            "PSF Beads", "PSF Beads Analysis Dashboard", "PSF Beads Analysis"
        ),
        dmc.Container(
            children=[
                dsc.dataset_table_paper(),
            ],
            style=CONTAINER_STYLE,
        ),
    ],
)


# Register shared callbacks
dsc.register_delete_dataset_callback(omero_dataset_psf_beads)
dsc.register_download_datasets_callback(omero_dataset_psf_beads)
dsc.register_update_kkm_table_callback(omero_dataset_psf_beads)
dsc.register_download_table_callback(omero_dataset_psf_beads)


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
