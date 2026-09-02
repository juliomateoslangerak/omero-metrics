import dash_mantine_components as dmc
from django_plotly_dash import DjangoDash

from omero_metrics.dash_apps.dataset_image import dataset_shared_components as dsc
from omero_metrics.styles import CONTAINER_STYLE, MANTINE_THEME

_MEASUREMENTS = [
    {"label": "FWHM X pixels", "value": "fwhm_pixel_x"},
    {"label": "FWHM Y pixels", "value": "fwhm_pixel_y"},
    {"label": "FWHM Z pixels", "value": "fwhm_pixel_z"},
    {"label": "FWHM X microns", "value": "fwhm_micron_x"},
    {"label": "FWHM Y microns", "value": "fwhm_micron_y"},
    {"label": "FWHM X microns", "value": "fwhm_micron_z"},
    {"label": "FWHM lateral asymetry", "value": "fwhm_lateral_asymmetry_ratio"},
    {"label": "FWHM axial asymetry", "value": "fwhm_axial_asymmetry_ratio"},
    {"label": "R^2 X gaussian fit", "value": "fit_gaussian_r2_x"},
    {"label": "R^2 Y gaussian fit", "value": "fit_gaussian_r2_y"},
    {"label": "R^2 Z gaussian fit", "value": "fit_gaussian_r2_z"},
    {"label": "Integrated intensity", "value": "intensity_integrated"},
    {"label": "Max intensity", "value": "intensity_max"},
    {"label": "Min intensity", "value": "intensity_min"},
    {"label": "Std intensity", "value": "intensity_std"},
]
_DEFAULT_MEASUREMENT = "fwhm_lateral_asymmetry_ratio"


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
