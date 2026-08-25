import dash_mantine_components as dmc
from django_plotly_dash import DjangoDash

from omero_metrics.dash_apps.dataset_image import dataset_shared_components as dsc
from omero_metrics.styles import CONTAINER_STYLE, MANTINE_THEME

dashboard_name = "omero_dataset_psf_beads"

omero_dataset_psf_beads = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)


omero_dataset_psf_beads.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dsc.notifications_container(),
        dsc.confirm_delete_modal(),
        dsc.dataset_header(
            "PSF Beads",
            "PSF Beads Analysis Dashboard",
            "PSF Beads Analysis",
        ),
        dmc.Container(
            children=[
                dsc.blank_input(),
                dsc.contour_chart(),
                dsc.dataset_table_paper(),
            ],
            style=CONTAINER_STYLE,
        ),
    ],
)

BEADS_HOVER_INFO = {
    "Image id": "image_id",
    "Bead id": "bead_id",
    "Sigma LoG": "sigma_LoG",
    "Considered valid": dsc.hover_flag("considered_valid"),
    "Considered self proximity": dsc.hover_flag("considered_self_proximity"),
    "Considered lateral edge": dsc.hover_flag("considered_lateral_edge"),
    "Considered axial edge": dsc.hover_flag("considered_axial_edge"),
    "Considered outlier": dsc.hover_flag("considered_intensity_std_outlier"),
    "Considered bad fit": dsc.hover_flag(
        "considered_bad_fit_gaussian_x",
        "considered_bad_fit_gaussian_y",
        "considered_bad_fit_gaussian_z",
    ),
}


# Register shared callbacks
dsc.register_delete_dataset_callback(omero_dataset_psf_beads)
dsc.register_download_datasets_callback(omero_dataset_psf_beads)
dsc.register_update_kkm_table_callback(omero_dataset_psf_beads)
dsc.register_download_table_callback(omero_dataset_psf_beads)
dsc.register_delete_button_loading_callback(omero_dataset_psf_beads)
dsc.register_contour_chart_callbacks(
    omero_dataset_psf_beads, "psf_beads_images", BEADS_HOVER_INFO
)
