from typing import NamedTuple


class KKMConfig(NamedTuple):
    display_name: str
    description: str
    key: str | None
    value: str
    display_in_group_level: bool = False
    units: str | None = None
    wavelength_nm: str | None = None
    error_bar: str | None = None


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
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Intensity ratio",
                description="min to max intensity ratio (uniformity)",
                key="channel_name",
                value="max_min_intensity_ratio",
                wavelength_nm="emission_wavelength_nm",
            ),
            KKMConfig(
                display_name="Corner intensity ratio",
                description="The ratio of the maximum intensity and the least intense corner",
                key="channel_name",
                value="min_corner_intensity_ratio",
                wavelength_nm="emission_wavelength_nm",
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
                units="microns",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fwhm_micron_x_std",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Median X fwhm",
                description="Median x resolution (FWHM) among the valid beads",
                key="channel_name",
                value="fwhm_micron_x_median",
                units="microns",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fwhm_micron_x_std",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Mean Y fwhm",
                description="Mean y resolution (FWHM) among the valid beads",
                key="channel_name",
                value="fwhm_micron_y_mean",
                units="microns",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fwhm_micron_y_std",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Median Y fwhm",
                description="Median y resolution (FWHM) among the valid beads",
                key="channel_name",
                value="fwhm_micron_y_median",
                units="microns",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fwhm_micron_y_std",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Mean Z fwhm",
                description="Mean z resolution (FWHM) among the valid beads",
                key="channel_name",
                value="fwhm_micron_z_mean",
                units="microns",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fwhm_micron_z_std",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Median Z fwhm",
                description="Median z resolution (FWHM) among the valid beads",
                key="channel_name",
                value="fwhm_micron_z_median",
                units="microns",
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
            ),
            KKMConfig(
                display_name="Axial asymmetry",
                description="Axial FWHM asymmetry ratio",
                key="channel_name",
                value="fwhm_axial_asymmetry_ratio_mean",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fwhm_axial_asymmetry_ratio_std",
            ),
            KKMConfig(
                display_name="X gaussian fit R&#178;",
                description="Gaussian fit R&#178; in the X axis",
                key="channel_name",
                value="fit_gaussian_r2_x_mean",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fit_gaussian_r2_x_std",
            ),
            KKMConfig(
                display_name="Y gaussian fit R&#178;",
                description="Gaussian fit R&#178; in the Y axis",
                key="channel_name",
                value="fit_gaussian_r2_y_mean",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fit_gaussian_r2_y_std",
            ),
            KKMConfig(
                display_name="Z gaussian fit R&#178;",
                description="Gaussian fit R&#178; in the Z axis",
                key="channel_name",
                value="fit_gaussian_r2_z_mean",
                wavelength_nm="emission_wavelength_nm",
                error_bar="fit_gaussian_r2_z_std",
            ),
            KKMConfig(
                display_name="Total beads nb",
                description="Total number of beads found",
                key="channel_name",
                value="total_bead_count",
                wavelength_nm="emission_wavelength_nm",
            ),
            KKMConfig(
                display_name="Valid beads nb",
                description="Number of beads considered valid",
                key="channel_name",
                value="considered_valid_count",
                wavelength_nm="emission_wavelength_nm",
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
                display_name="Mean abs distance 3D",
                description="Mean 3D distance measured in microns",
                key="channel_name",
                value="distance_mean_micron_3d",
                units="microns",
                wavelength_nm="emission_wavelength_nm",
                error_bar="distance_std_micron_3d",
            ),
            KKMConfig(
                display_name="Median abs distance 3D",
                description="Median 3D distance measured in microns",
                key="channel_name",
                value="distance_median_micron_3d",
                units="microns",
                wavelength_nm="emission_wavelength_nm",
                error_bar="distance_std_micron_3d",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="Mean abs translation in X",
                description="Mean absolute translation in the x axis measured in pixels",
                key="channel_name",
                value="translation_abs_mean_pixel_x",
                units="pixels",
                wavelength_nm="emission_wavelength_nm",
                error_bar="translation_abs_std_pixel_x",
            ),
            KKMConfig(
                display_name="Median abs translation in X",
                description="Median absolute translation in the x axis measured in pixels",
                key="channel_name",
                value="translation_abs_mean_pixel_x",
                units="pixels",
                wavelength_nm="emission_wavelength_nm",
                error_bar="translation_abs_std_pixel_x",
            ),
            KKMConfig(
                display_name="Mean abs translation in Y",
                description="Mean absolute translation in the y axis measured in pixels",
                key="channel_name",
                value="translation_abs_mean_pixel_y",
                units="pixels",
                wavelength_nm="emission_wavelength_nm",
                error_bar="translation_abs_std_pixel_y",
            ),
            KKMConfig(
                display_name="Median abs translation in Y",
                description="Median absolute translation in the y axis measured in pixels",
                key="channel_name",
                value="translation_abs_mean_pixel_y",
                units="pixels",
                wavelength_nm="emission_wavelength_nm",
                error_bar="translation_abs_std_pixel_y",
            ),
            KKMConfig(
                display_name="Mean abs translation in Z",
                description="Mean absolute translation in the z axis measured in pixels",
                key="channel_name",
                value="translation_abs_mean_pixel_z",
                units="pixels",
                wavelength_nm="emission_wavelength_nm",
                error_bar="translation_abs_std_pixel_z",
            ),
            KKMConfig(
                display_name="Median abs translation in Z",
                description="Median absolute translation in the z axis measured in pixels",
                key="channel_name",
                value="translation_abs_mean_pixel_z",
                units="pixels",
                wavelength_nm="emission_wavelength_nm",
                error_bar="translation_abs_std_pixel_z",
            ),
            KKMConfig(
                display_name="Valid beads nb",
                description="Number of beads considered valid",
                key="channel_name",
                value="considered_valid_count",
                wavelength_nm="emission_wavelength_nm",
            ),
        ],
    ),
    "StageDriftDataset": AssayConfiguration(
        display_name="Stage drift",
        description="Stage drift assay",
        assay_app_name="omero_dataset_stage_drift",
        image_app_name={"input_data": "omero_image_stage_drift"},
        kkm_configuration=[
            KKMConfig(
                display_name="Mean displacement X",
                description="Mean of all single frame displacements in X measured in microns",
                key=None,
                value="displacement_micron_x_median",
                units="microns",
                error_bar="displacement_micron_x_std",
            ),
            KKMConfig(
                display_name="Mean displacement Y",
                description="Mean of all single frame displacements in Y measured in microns",
                key=None,
                value="displacement_micron_y_mean",
                units="microns",
                error_bar="displacement_micron_y_std",
            ),
            KKMConfig(
                display_name="Mean displacement Z",
                description="Mean of all single frame displacements in Z measured in microns",
                key=None,
                value="displacement_micron_z_mean",
                units="microns",
                error_bar="displacement_micron_z_std",
            ),
            KKMConfig(
                display_name="Mean displacement 3D",
                description="Mean of all single frame displacements in X measured in microns",
                key=None,
                value="displacement_micron_3d_mean",
                units="microns",
                error_bar="displacement_micron_x_std",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="MSD slope",
                description="Slope of the linear fit on the Mean Square Displacement in 3D",
                key=None,
                value="msd_slope_micron_3d",
                units="microns per second",
                display_in_group_level=True,
            ),
            KKMConfig(
                display_name="MSD intercept",
                description="Intercept point of the linear fit on the Mean Square Displacement in 3D",
                key=None,
                value="msd_intercept_micron_3d",
                units="seconds",
                display_in_group_level=True,
            ),
        ],
    ),
}
