from django_plotly_dash import DjangoDash

from omero_metrics.dash_apps.dataset_image import dataset_shared_components as dsc

dashboard_name = "omero_dataset_coregistration"

omero_dataset_coregistration = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)

omero_dataset_coregistration.layout = dsc.contour_dashboard_layout(
    "Co-Registration",
    "Co-Registration Analysis Dashboard",
    "Co-Registration Analysis",
)


# Register shared callbacks
dsc.register_delete_dataset_callback(omero_dataset_coregistration)
dsc.register_download_datasets_callback(omero_dataset_coregistration)
dsc.register_update_kkm_table_callback(omero_dataset_coregistration)
dsc.register_download_table_callback(omero_dataset_coregistration)
dsc.register_delete_button_loading_callback(omero_dataset_coregistration)
dsc.register_contour_callbacks(
    omero_dataset_coregistration, "multiwavelength_beads_images"
)
