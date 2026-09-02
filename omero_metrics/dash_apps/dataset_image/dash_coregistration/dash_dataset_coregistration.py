import dash_mantine_components as dmc
from django_plotly_dash import DjangoDash

from omero_metrics.dash_apps.dataset_image import dataset_shared_components as dsc
from omero_metrics.styles import CONTAINER_STYLE, MANTINE_THEME

dashboard_name = "omero_dataset_coregistration"

omero_dataset_coregistration = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)


_MEASUREMENTS = [
    {"label": "Translation X pixels", "value": "translation_x_px"},
    {"label": "Translation Y pixels", "value": "translation_y_px"},
    {"label": "Translation Z pixels", "value": "translation_z_px"},
    {"label": "Translation X microns", "value": "translation_x_micron"},
    {"label": "Translation Y microns", "value": "translation_y_micron"},
    {"label": "Translation Z microns", "value": "translation_z_micron"},
    {"label": "Lateral distance micron", "value": "distance_lateral_micron"},
    {"label": "3D distance micron", "value": "distance_3d_micron"},
    {"label": "Sigma LoG", "value": "sigma_LoG"},
    {"label": "Phase diff", "value": "phase_diff"},
    {"label": "Center X", "value": "center_x"},
    {"label": "Center Y", "value": "center_y"},
    {"label": "Center Z", "value": "center_z"},
]
_DEFAULT_MEASUREMENT = "distance_3d_micron"

omero_dataset_coregistration.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dsc.notifications_container(),
        dsc.confirm_delete_modal(),
        dsc.dataset_header(
            "Co-Registration",
            "Co-Registration Analysis Dashboard",
            "Co-Registration Analysis",
        ),
        dmc.Container(
            children=[
                dsc.blank_input(),
                dsc.contour_chart(
                    measurements=_MEASUREMENTS,
                    default_measurement=_DEFAULT_MEASUREMENT,
                ),
                dsc.dataset_table_paper(),
            ],
            style=CONTAINER_STYLE,
        ),
    ],
)

BEADS_HOVER_INFO = {
    "Image id": "image_id",
    "Bead id": "bead_id",
    "Considered valid": dsc.hover_flag("considered_valid"),
    "Considered self proximity": dsc.hover_flag("considered_self_proximity"),
    "Considered lateral edge": dsc.hover_flag("considered_lateral_edge"),
    "Considered axial edge": dsc.hover_flag("considered_axial_edge"),
    "Considered outlier": dsc.hover_flag("considered_distance_3d_micron_outlier"),
    "Considered bad fit": dsc.hover_flag("considered_bad_fit_gaussian"),
}

# Register shared callbacks
dsc.register_delete_dataset_callback(omero_dataset_coregistration)
dsc.register_download_datasets_callback(omero_dataset_coregistration)
dsc.register_update_kkm_table_callback(omero_dataset_coregistration)
dsc.register_download_table_callback(omero_dataset_coregistration)
dsc.register_delete_button_loading_callback(omero_dataset_coregistration)
dsc.register_contour_chart_callbacks(
    omero_dataset_coregistration, "multiwavelength_beads_images", BEADS_HOVER_INFO
)
