from functools import lru_cache
from typing import NamedTuple, get_args, get_type_hints

from microscopemetrics.analyses import field_illumination, psf_beads
from microscopemetrics_schema.datamodel import microscopemetrics_schema as mm_schema
from microscopemetrics_schema.datamodel.microscopemetrics_schema import Image


@lru_cache(maxsize=None)
def get_image_fields(dataset_class) -> dict[str, list[str]]:
    """Introspect a dataset class to find Image-typed fields per location.

    Returns a dict mapping location names ('input_data', 'output') to lists
    of field names that are typed as Image or list[Image].
    """
    result = {}
    hints = get_type_hints(dataset_class)
    for location in ("input_data", "output"):
        location_hint = hints.get(location)
        if location_hint is None:
            result[location] = []
            continue
        # Resolve Union/Optional to find the actual sub-class (not dict/NoneType)
        sub_cls = None
        for arg in get_args(location_hint):
            if arg is not dict and arg is not type(None):
                sub_cls = arg
                break
        if sub_cls is None:
            result[location] = []
            continue
        # Find fields whose type includes Image
        image_fields = []
        for field_name, field_type in get_type_hints(sub_cls).items():
            all_args = get_args(field_type) or (field_type,)
            if any(a is Image or Image in get_args(a) for a in all_args):
                image_fields.append(field_name)
        result[location] = image_fields
    return result


@lru_cache(maxsize=None)
def get_dataset_class(input_parameters_class):
    """Find the MetricsDataset subclass whose input_parameters field is typed as the given class."""
    for subclass in mm_schema.MetricsDataset.__subclasses__():
        for arg in get_args(
            get_type_hints(subclass).get("input_parameters", None) or ()
        ):
            if arg is input_parameters_class:
                return subclass
    raise ValueError(
        f"No Dataset class found for input parameters class {input_parameters_class}"
    )


@lru_cache(maxsize=None)
def get_input_data_class(dataset_class):
    """Resolve the InputData class from a dataset class's input_data type hint."""
    for arg in get_args(get_type_hints(dataset_class).get("input_data")):
        if arg is not dict and arg is not type(None):
            return arg
    raise ValueError(f"No InputData class found for {dataset_class}")


ANALYSIS_FUNCTIONS = {
    "FieldIlluminationInputParameters": field_illumination.analyse_field_illumination,
    "PSFBeadsInputParameters": psf_beads.analyse_psf_beads,
}


class KKMConfig(NamedTuple):
    display_name: str
    description: str
    value: str
    error_bar: str | None
    display_in_group_level: bool


class AssayConfiguration(NamedTuple):
    display_name: str
    description: str
    assay_app_name: str
    image_app_name: dict
    kkm_configuration: list[KKMConfig]


ASSAY_CONFIGURATIONS = {
    "FieldIlluminationDataset": AssayConfiguration(
        display_name="Field illumination",
        description="Field illumination assay",
        assay_app_name="omero_dataset_foi",
        image_app_name={
            "input_data": "omero_image_foi",
        },
        kkm_configuration=[
            KKMConfig(
                display_name="Center relative position",
                description="Relative position of the center of intensity",
                value="center_fitted_distance_relative",
                error_bar=None,
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Center relative intensity",
                description="Intensity of the image center relative to the corners",
                value="center_region_intensity_fraction",
                error_bar=None,
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Max intensity",
                description="Max intensity of the image",
                value="max_intensity",
                error_bar=None,
                display_in_group_level=False,
            ),
        ],
    ),
    "PSFBeadsDataset": AssayConfiguration(
        display_name="PSF beads",
        description="PSF beads assay",
        assay_app_name="omero_dataset_psf_beads",
        image_app_name={
            "input_data": "omero_image_psf_beads",
            "output": "omero_image_average_bead",
        },
        kkm_configuration=[
            KKMConfig(
                display_name="Mean X fwhm",
                description="Mean x resolution (FWHM) among the valid beads",
                value="fwhm_micron_x_mean",
                error_bar="fwhm_micron_x_std",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Mean Y fwhm",
                description="Mean y resolution (FWHM) among the valid beads",
                value="fwhm_micron_y_mean",
                error_bar="fwhm_micron_y_std",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Mean Z fwhm",
                description="Mean z resolution (FWHM) among the valid beads",
                value="fwhm_micron_z_mean",
                error_bar="fwhm_micron_z_std",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Lateral asymmetry",
                description="Lateral FWHM asymmetry ratio",
                value="fwhm_lateral_asymmetry_ratio_mean",
                error_bar="fwhm_lateral_asymmetry_ratio_std",
                display_in_group_level=False,
            ),
            # TODO: need to implement this in microscopemetrics
            # KKMConfig(
            #     display_name="Axial asymmetry",
            #     description="Axial FWHM asymmetry ratio",
            #     value="fwhm_axial_asymmetry_ratio_mean",
            #     error_bar="fwhm_axial_asymmetry_ratio_std",
            #     display_in_group_level=False,
            # ),
            KKMConfig(
                display_name="X gaussian fit",
                description="Gaussian fit R&#178; in the X axis",
                value="fit_gaussian_r2_x_mean",
                error_bar="fit_gaussian_r2_x_std",
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Y gaussian fit",
                description="Gaussian fit R&#178; in the Y axis",
                value="fit_gaussian_r2_y_mean",
                error_bar="fit_gaussian_r2_y_std",
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Z gaussian fit",
                description="Gaussian fit R&#178; in the Z axis",
                value="fit_gaussian_r2_z_mean",
                error_bar="fit_gaussian_r2_z_std",
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Total beads nb",
                description="Total number of beads found",
                value="total_bead_count",
                error_bar=None,
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Valid beads nb",
                description="Number of beads considered valid",
                value="considered_valid_count",
                error_bar=None,
                display_in_group_level=False,
            ),
        ],
    ),
}
