from microscopemetrics.analyses import field_illumination, psf_beads

DATASET_TYPES = ["FieldIlluminationDataset", "PSFBeadsDataset"]

INPUT_IMAGES_MAPPING = {
    "FieldIlluminationDataset": "field_illumination_images",
    "PSFBeadsDataset": "psf_beads_images",
}


DATASET_IMAGES = {
    "FieldIlluminationDataset": {
        "input_data": ["field_illumination_images"],
        "output": [],
    },
    "PSFBeadsDataset": {
        "input_data": ["psf_beads_images"],
        "output": ["average_bead"],
    },
}

DATA_TYPE = {
    "FieldIlluminationInputParameters": [
        "FieldIlluminationDataset",
        "FieldIlluminationInputData",
        "field_illumination_images",
        field_illumination.analyse_field_illumination,
    ],
    "PSFBeadsInputParameters": [
        "PSFBeadsDataset",
        "PSFBeadsInputData",
        "psf_beads_images",
        psf_beads.analyse_psf_beads,
    ],
}

# All the selected kkm should be numerical.

KKM_MAPPINGS = {
    "FieldIlluminationDataset": [
        "max_intensity",
        "center_region_intensity_fraction",
        "center_region_area_fraction",
    ],
    "PSFBeadsDataset": [
        "considered_valid_count",
        "total_bead_count",
        "fwhm_micron_x_mean",
        "fwhm_micron_y_mean",
        "fwhm_micron_z_mean",
        "fwhm_micron_x_std",
        "fwhm_micron_y_std",
        "fwhm_micron_z_std",
        "fwhm_lateral_asymmetry_ratio_mean",
        "fwhm_lateral_asymmetry_ratio_std",
        "fit_airy_r2_z_mean",
        "fit_airy_r2_y_mean",
        "fit_airy_r2_x_mean",
        "fit_gaussian_r2_z_mean",
        "fit_gaussian_r2_y_mean",
        "fit_gaussian_r2_x_mean",
        "average_bead_fit_airy_r2_z",
        "average_bead_fit_airy_r2_y",
        "average_bead_fit_airy_r2_x",
        "average_bead_fit_gaussian_r2_z",
        "average_bead_fit_gaussian_r2_y",
        "average_bead_fit_gaussian_r2_x",
        "average_bead_fwhm_micron_z",
        "average_bead_fwhm_micron_y",
        "average_bead_fwhm_micron_x",
        "average_bead_fwhm_lateral_asymmetry_ratio",
    ],
}

TEMPLATE_MAPPINGS_DATASET = {
    "FieldIlluminationDataset": "omero_dataset_foi",
    "PSFBeadsDataset": "omero_dataset_psf_beads",
}

TEMPLATE_MAPPINGS_IMAGE = {
    "FieldIlluminationDataset": {
        "input_data": "omero_image_foi",
    },
    "PSFBeadsDataset": {
        "input_data": "omero_image_psf_beads",
        "output": "WarningApp",
    },
}
