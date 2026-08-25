import logging

import dash
import dash_mantine_components as dmc
import numpy as np
import plotly.express as px
from dash import dcc
from django_plotly_dash import DjangoDash

import omero_metrics.dash_apps.dataset_image.dataset_shared_components as dsc
import omero_metrics.dash_apps.utils.omero_metrics_components as my_components
from omero_metrics.dash_apps.dataset_image.dash_psf_beads.dash_image_psf_beads import (
    fig_bead,
)
from omero_metrics.styles import MANTINE_THEME, THEME
from omero_metrics.tools import load
from omero_metrics.tools.serializers import deserialize

logger = logging.getLogger(__name__)
dashboard_name = "omero_image_average_bead"

omero_image_average_bead = DjangoDash(name=dashboard_name, serve_locally=True)

omero_image_average_bead.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dsc.image_header(
            "PSF Beads Analysis",
            "Advanced Microscopy Image Analysis",
            "PSF beads Analysis",
            load_buttons=False,
        ),
        # Main Content
        dmc.Container(
            [
                dsc.blank_input(),
                dmc.Grid(
                    children=[
                        dmc.GridCol(
                            [
                                dmc.Paper(
                                    [
                                        dmc.Group(
                                            [
                                                dmc.Text(
                                                    "Average Bead Image",
                                                    size="lg",
                                                    fw=500,
                                                    c=THEME["primary"],
                                                ),
                                                dmc.Tooltip(
                                                    label="Average bead image max intensity projections and profiles",
                                                    children=[
                                                        my_components.get_icon(
                                                            "material-symbols:info",
                                                            color=THEME["primary"],
                                                        )
                                                    ],
                                                ),
                                            ],
                                            justify="space-between",
                                        ),
                                        dcc.Graph(
                                            figure={},
                                            style={"height": "400px"},
                                            id="average-image-graph",
                                        ),
                                    ],
                                    p="md",
                                    radius="md",
                                    withBorder=True,
                                    shadow="sm",
                                    h="100%",
                                ),
                            ],
                            span=8,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Paper(
                                    h="100%",
                                    shadow="xs",
                                    p="md",
                                    radius="md",
                                    children=[
                                        dmc.Stack(
                                            [
                                                dmc.Text(
                                                    "Visualization Controls",
                                                    size="lg",
                                                    fw=500,
                                                    c=THEME["primary"],
                                                ),
                                                dmc.Divider(
                                                    label="Channel Selection",
                                                    labelPosition="center",
                                                ),
                                                dmc.Select(
                                                    id="channel-selector-average-image",
                                                    label="Channel",
                                                    w="100%",
                                                    allowDeselect=False,
                                                    leftSection=my_components.get_icon(
                                                        "material-symbols:layers"
                                                    ),
                                                    rightSection=my_components.get_icon(
                                                        "radix-icons:chevron-down"
                                                    ),
                                                ),
                                                dmc.Divider(
                                                    label="Display Options",
                                                    labelPosition="center",
                                                    mt="md",
                                                ),
                                                dmc.Stack(
                                                    [],
                                                    gap="xs",
                                                ),
                                                dmc.Divider(
                                                    label="Color Settings",
                                                    labelPosition="center",
                                                    mt="md",
                                                ),
                                                dmc.Select(
                                                    id="color-selector-average-image",
                                                    label="Color Scheme",
                                                    allowDeselect=False,
                                                    data=[
                                                        {
                                                            "value": "Hot",
                                                            "label": "Hot",
                                                        },
                                                        {
                                                            "value": "Blackbody",
                                                            "label": "Blackbody",
                                                        },
                                                        {
                                                            "value": "Viridis",
                                                            "label": "Viridis",
                                                        },
                                                        {
                                                            "value": "Inferno",
                                                            "label": "Inferno",
                                                        },
                                                    ],
                                                    value="Blackbody",
                                                    leftSection=my_components.get_icon(
                                                        "material-symbols:palette"
                                                    ),
                                                    rightSection=my_components.get_icon(
                                                        "radix-icons:chevron-down"
                                                    ),
                                                ),
                                                dmc.Switch(
                                                    id="color-switch-average-image",
                                                    label="Invert Colors",
                                                    checked=False,
                                                    size="md",
                                                    color=THEME["primary"],
                                                ),
                                            ],
                                            gap="sm",
                                        ),
                                    ],
                                ),
                            ],
                            span=4,
                        ),
                    ],
                ),
            ],
            size="xl",
            p="md",
            style={"backgroundColor": THEME["surface"]},
        ),
    ],
)


@omero_image_average_bead.expanded_callback(
    dash.dependencies.Output("average-image-graph", "figure"),
    [
        dash.dependencies.Input("channel-selector-average-image", "value"),
        dash.dependencies.Input("color-selector-average-image", "value"),
        dash.dependencies.Input("color-switch-average-image", "checked"),
    ],
)
def update_single_bead_image(channel_index, color, invert_color, *, session_state):
    try:
        context = deserialize(session_state["context"])
        mm_image = context["mm_image"]
        channel_index = int(channel_index)

        mips = {
            "z": context["mips"]["z"][..., channel_index],
            "y": context["mips"]["y"][..., channel_index],
            "x": context["mips"]["x"][..., channel_index],
        }
        mips = {a: np.sqrt(mip) for a, mip in mips.items()}

        mm_dataset = context["mm_dataset"]
        profiles = get_average_bead_profiles(
            bead_index=0,
            channel_index=channel_index,
            image_id=0,
            mm_dataset=mm_dataset,
        )
        voxel_size = {
            "x": mm_image.voxel_size_x_micron,
            "y": mm_image.voxel_size_y_micron,
            "z": mm_image.voxel_size_z_micron,
        }

        kkm_values = [k.value for k in context["assay_config"].kkm_configuration]

        table_km = load.get_km_mm_metrics_dataset(
            mm_dataset=deserialize(context["mm_dataset"])
        )

        if all(list(voxel_size.values())):
            fwhms = {
                "x": table_km.loc[
                    table_km["channel_nr"] == channel_index,
                    "average_bead_fwhm_micron_x",
                ].iloc[0],
                "y": table_km.loc[
                    table_km["channel_nr"] == channel_index,
                    "average_bead_fwhm_micron_y",
                ].iloc[0],
                "z": table_km.loc[
                    table_km["channel_nr"] == channel_index,
                    "average_bead_fwhm_micron_z",
                ].iloc[0],
            }
        else:
            fwhms = {
                "x": table_km.loc[
                    table_km["channel_nr"] == channel_index,
                    "average_bead_fwhm_pixel_x",
                ].iloc[0],
                "y": table_km.loc[
                    table_km["channel_nr"] == channel_index,
                    "average_bead_fwhm_pixel_y",
                ].iloc[0],
                "z": table_km.loc[
                    table_km["channel_nr"] == channel_index,
                    "average_bead_fwhm_pixel_z",
                ].iloc[0],
            }
        r_sq = {
            "x": table_km.loc[
                table_km["channel_nr"] == channel_index,
                "average_bead_fit_gaussian_r2_x",
            ].iloc[0],
            "y": table_km.loc[
                table_km["channel_nr"] == channel_index,
                "average_bead_fit_gaussian_r2_y",
            ].iloc[0],
            "z": table_km.loc[
                table_km["channel_nr"] == channel_index,
                "average_bead_fit_gaussian_r2_z",
            ].iloc[0],
        }

        fig_mip_go = fig_bead(
            mips=mips,
            color=color,
            invert=invert_color,
            profiles=profiles,
            fwhms=fwhms,
            r_sq=r_sq,
            voxel_size=voxel_size,
        )

        return fig_mip_go

    except Exception as e:
        logger.error(f"Error updating image: {str(e)}")
        return px.imshow([[0]], title="Error loading image")


@omero_image_average_bead.expanded_callback(
    dash.dependencies.Output("channel-selector-average-image", "data"),
    dash.dependencies.Output("channel-selector-average-image", "value"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_channels_average_image(_blank_input, *, session_state):
    context = deserialize(session_state["context"])
    channel_series = context["mm_image"].channel_series
    return [
        {"label": c.name, "value": str(i)}
        for i, c in enumerate(channel_series.channels)
    ], "0"


def get_average_bead_profiles(bead_index, channel_index, image_id, mm_dataset):
    # bead_index and image_is are not used.
    profiles = {
        axis: load.load_table_mm_metrics(mm_dataset.output[f"bead_profiles_{axis}"])
        for axis in ("x", "y", "z")
    }
    # TODO: we have chosen to show the gaussian fit but once the airy fit is fixed, we should add the option to
    #  choose between gaussian and airy
    profiles = {
        axis: df.loc[
            :,
            [
                f"{channel_index}_{axis}_raw",
                f"{channel_index}_{axis}_fitted_gaussian",
            ],
        ].rename(
            columns={
                f"{channel_index}_{axis}_raw": "raw",
                f"{channel_index}_{axis}_fitted_gaussian": "fitted",
            }
        )
        for axis, df in profiles.items()
    }
    # We flip the values of the profiles in the y-axis
    profiles["y"] = profiles["y"].iloc[::-1].reset_index(drop=True)

    return profiles
