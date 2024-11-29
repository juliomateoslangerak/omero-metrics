from microscopemetrics.analyses import field_illumination, psf_beads

DATASET_TYPES = ["FieldIlluminationDataset", "PSFBeadsDataset"]

INPUT_IMAGES_MAPPING = {
    "FieldIlluminationDataset": "field_illumination_image",
    "PSFBeadsDataset": "psf_beads_images",
}


DATASET_IMAGES = {
    "FieldIlluminationDataset": {
        "input_data": ["field_illumination_image"],
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
        "field_illumination_image",
        field_illumination.analyse_field_illumination,
    ],
    "PSFBeadsInputParameters": [
        "PSFBeadsDataset",
        "PSFBeadsInputData",
        "psf_beads_images",
        psf_beads.analyse_psf_beads,
    ],
}
KKM_MAPPINGS = {
    "FieldIlluminationDataset": [
        "max_intensity",
        "center_region_intensity_fraction",
        "center_region_area_fraction",
    ],
    "PSFBeadsDataset": [
        "intensity_max_median",
        "intensity_max_std",
        "intensity_min_mean",
        "intensity_min_median",
        "intensity_min_std",
        "intensity_std_mean",
        "intensity_std_median",
        "intensity_std_std",
    ],
}

TEMPLATE_MAPPINGS_DATASET = {
    "FieldIlluminationDataset": "omero_dataset_foi",
    "PSFBeadsDataset": "omero_dataset_psf_beads",
}

TEMPLATE_MAPPINGS_IMAGE = {
    "FieldIlluminationDataset": {
        "input_data": "omero_image_foi",
        "output": "WarningApp",
    },
    "PSFBeadsDataset": {
        "input_data": "omero_image_psf_beads",
        "output": "WarningApp",
    },
}
