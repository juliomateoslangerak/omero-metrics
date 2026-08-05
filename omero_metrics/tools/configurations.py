from typing import NamedTuple


class KKMConfig(NamedTuple):
    display_name: str
    description: str
    key: str
    value: str
    wavelength_nm: str
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
                key="channel_name",
                value="center_fitted_distance_relative",
                wavelength_nm="emission_wavelength_nm",
                error_bar=None,
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Center relative intensity",
                description="Intensity of the image center relative to the corners",
                key="channel_name",
                value="center_region_intensity_fraction",
                wavelength_nm="emission_wavelength_nm",
                error_bar=None,
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Max intensity",
                description="Max intensity of the image",
                key="channel_name",
                value="max_intensity",
                wavelength_nm="emission_wavelength_nm",
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
                key="channel_name",
                value="fwhm_micron_x_mean",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fwhm_micron_x_std",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Mean Y fwhm",
                description="Mean y resolution (FWHM) among the valid beads",
                key="channel_name",
                value="fwhm_micron_y_mean",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fwhm_micron_y_std",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Mean Z fwhm",
                description="Mean z resolution (FWHM) among the valid beads",
                key="channel_name",
                value="fwhm_micron_z_mean",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fwhm_micron_z_std",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Lateral asymmetry",
                description="Lateral FWHM asymmetry ratio",
                key="channel_name",
                value="fwhm_lateral_asymmetry_ratio_mean",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fwhm_lateral_asymmetry_ratio_std",
                display_in_group_level=False,
            ),
            # TODO: need to implement this in microscopemetrics
            # KKMConfig(
            #     display_name="Axial asymmetry",
            #     description="Axial FWHM asymmetry ratio",
            #     key="channel_name",
            #     value="fwhm_axial_asymmetry_ratio_mean",
            #     wavelength_nm = "emission_wavelength_nm",
            #     error_bar="fwhm_axial_asymmetry_ratio_std",
            #     display_in_group_level=False,
            # ),
            KKMConfig(
                display_name="X gaussian fit",
                description="Gaussian fit R&#178; in the X axis",
                key="channel_name",
                value="fit_gaussian_r2_x_mean",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fit_gaussian_r2_x_std",
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Y gaussian fit",
                description="Gaussian fit R&#178; in the Y axis",
                key="channel_name",
                value="fit_gaussian_r2_y_mean",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fit_gaussian_r2_y_std",
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Z gaussian fit",
                description="Gaussian fit R&#178; in the Z axis",
                key="channel_name",
                value="fit_gaussian_r2_z_mean",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fit_gaussian_r2_z_std",
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Total beads nb",
                description="Total number of beads found",
                key="channel_name",
                value="total_bead_count",
                wavelength_nm="emission_wavelength_nm",
                error_bar=None,
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Valid beads nb",
                description="Number of beads considered valid",
                key="channel_name",
                value="considered_valid_count",
                wavelength_nm="emission_wavelength_nm",
                error_bar=None,
                display_in_group_level=False,
            ),
        ],
    ),
    "CoRegistrationDataset": AssayConfiguration(
        display_name="Co-Registration",
        description="Channel co-registration assay",
        assay_app_name="omero_dataset_coregistration",
        image_app_name={"input_data": "omero_image_coregistration"},
        kkm_configuration=[
            KKMConfig(
                display_name="Distance 3D Mean Micron",
                description="Mean 3D distance measured in microns",
                key="channel_name",
                value="distance_mean_micron_3d",
                wavelength_nm="emission_wavelength_nm",
                error_bar=None,
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Rotation Z Mean",
                description="Rotation along the z axis",
                key="channel_name",
                value="rotation_z_mean",
                wavelength_nm="emission_wavelength_nm",
                error_bar=None,
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Translation Abs Mean Pixel X",
                description="Mean absolute translation in the x axis measured in pixels",
                key="channel_name",
                value="translation_abs_mean_pixel_x",
                wavelength_nm="emission_wavelength_nm",
                error_bar=None,
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Translation Abs Mean Pixel Y",
                description="Mean absolute translation in the y axis measured in pixels",
                key="channel_name",
                value="translation_abs_mean_pixel_y",
                wavelength_nm="emission_wavelength_nm",
                error_bar=None,
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Translation Abs Mean Pixel Z",
                description="Mean absolute translation in the z axis measured in pixels",
                key="channel_name",
                value="translation_abs_mean_pixel_z",
                wavelength_nm="emission_wavelength_nm",
                error_bar=None,
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Translation Abs Mean Micron X",
                description="Mean absolute translation in the x axis measured in microns",
                key="channel_name",
                value="translation_abs_mean_micron_x",
                wavelength_nm="emission_wavelength_nm",
                error_bar=None,
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Translation Abs Mean Micron Y",
                description="Mean absolute translation in the y axis measured in microns",
                key="channel_name",
                value="translation_abs_mean_micron_y",
                wavelength_nm="emission_wavelength_nm",
                error_bar=None,
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Translation Abs Mean Micron Z",
                description="Mean absolute translation in the z axis measured in microns",
                key="channel_name",
                value="translation_abs_mean_micron_z",
                wavelength_nm="emission_wavelength_nm",
                error_bar=None,
                display_in_group_level=False,
            ),
            KKMConfig(
                display_name="Valid beads nb",
                description="Number of beads considered valid",
                key="channel_name",
                value="considered_valid_count",
                wavelength_nm="emission_wavelength_nm",
                error_bar=None,
                display_in_group_level=False,
            ),
        ],
    ),
}
