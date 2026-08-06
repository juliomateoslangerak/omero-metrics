from django_plotly_dash import DjangoDash

from omero_metrics.dash_apps.dataset_image import dataset_shared_components as dsc

dashboard_name = "omero_dataset_psf_beads"

omero_dataset_psf_beads = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)

omero_dataset_psf_beads.layout = dsc.contour_dashboard_layout(
    "PSF Beads",
    "PSF Beads Analysis Dashboard",
    "PSF Beads Analysis",
)


# Register shared callbacks
dsc.register_delete_dataset_callback(omero_dataset_psf_beads)
dsc.register_download_datasets_callback(omero_dataset_psf_beads)
dsc.register_update_kkm_table_callback(omero_dataset_psf_beads)
dsc.register_download_table_callback(omero_dataset_psf_beads)
dsc.register_delete_button_loading_callback(omero_dataset_psf_beads)
dsc.register_contour_callbacks(omero_dataset_psf_beads, "psf_beads_images")
