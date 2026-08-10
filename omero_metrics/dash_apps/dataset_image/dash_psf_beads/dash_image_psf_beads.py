import logging

import dash
import dash_mantine_components as dmc
import numpy as np
import plotly.graph_objs as go
from dash import dcc
from django_plotly_dash import DjangoDash
from plotly.subplots import make_subplots

import omero_metrics.dash_apps.utils.omero_metrics_components as my_components
from omero_metrics.dash_apps.dataset_image import dataset_shared_components as dsc
from omero_metrics.styles import MANTINE_THEME, THEME
from omero_metrics.tools import load
from omero_metrics.tools.serializers import deserialize

logger = logging.getLogger(__name__)
dashboard_name = "omero_image_psf_beads"

omero_image_psf_beads = DjangoDash(name=dashboard_name, serve_locally=True)

omero_image_psf_beads.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        # Header Section
        my_components.header_component(
            "PSF Beads Analysis",
            "Advanced Microscopy Image Analysis",
            "PSF beads Analysis",
            load_buttons=False,
        ),
        # Main Content
        dmc.Container(
            [
                dsc.blank_input(),
                dmc.Stack(
                    [
                        dsc.intensity_chart(),
                        dmc.Paper(
                            id="bead-image-paper",
                            shadow="sm",
                            p="md",
                            radius="md",
                            children=[
                                dmc.Group(
                                    [
                                        dmc.Text(
                                            id="bead-image-title",
                                            children="Bead image (select bead to view)",
                                            size="lg",
                                            fw=500,
                                            c=THEME["primary"],
                                        ),
                                    ],
                                    justify="space-between",
                                ),
                                dcc.Graph(
                                    id="bead-image-graph",
                                    figure={},
                                    style={"height": "800px"},
                                ),
                            ],
                        ),
                    ],
                    gap="md",
                ),
            ],
            size="xl",
            p="md",
            style={"backgroundColor": THEME["surface"]},
        ),
    ],
)


dsc.register_intensity_chart_callbacks(omero_image_psf_beads, "psf_beads_images")


@omero_image_psf_beads.expanded_callback(
    dash.dependencies.Output("bead-image-graph", "figure"),
    dash.dependencies.Output("bead-image-title", "children"),
    [
        dash.dependencies.Input("intensity-chart", "clickData"),
        dash.dependencies.Input("intensity-chart-channel-select", "value"),
        dash.dependencies.Input("intensity-chart-color-select", "value"),
        dash.dependencies.Input("invert-color-switch", "checked"),
    ],
    prevent_initial_call=True,
)
def update_single_bead_image(
    points, channel_index, color, invert_color, *, session_state
):
    point = points["points"][0]  # FIXME: point is None at initial call
    if point["curveNumber"] != 1:
        return dash.no_update

    context = deserialize(session_state["context"])
    bead_index = point["pointNumber"]
    mm_image = context["mm_image"]
    image_id = mm_image.data_reference.omero_object_id
    channel_index = int(channel_index)
    beads_properties_df = context["beads_properties"]
    bead_df = beads_properties_df.loc[
        (beads_properties_df["image_id"] == image_id)
        & (beads_properties_df["channel_nr"] == channel_index)
        & (beads_properties_df["bead_id"] == bead_index),
        :,
    ]
    beads_array = context["beads_array"]

    bead_array = beads_array[bead_index, :, :, :, channel_index]

    mips = {
        "x": np.flipud(np.transpose(np.max(bead_array, axis=2))),
        "y": np.max(bead_array, axis=1),
        "z": np.flipud(np.max(bead_array, axis=0)),
    }
    mips = {a: np.sqrt(mip) for a, mip in mips.items()}

    mm_dataset = context["mm_dataset"]
    profiles = get_bead_profiles(
        bead_index=bead_index,
        channel_index=channel_index,
        image_id=image_id,
        mm_dataset=mm_dataset,
    )
    voxel_size = {
        "x": mm_image.voxel_size_x_micron,
        "y": mm_image.voxel_size_y_micron,
        "z": mm_image.voxel_size_z_micron,
    }
    if all(list(voxel_size.values())):
        fwhms = {
            "x": bead_df["fwhm_micron_x"].values[0],
            "y": bead_df["fwhm_micron_y"].values[0],
            "z": bead_df["fwhm_micron_z"].values[0],
        }
    else:
        fwhms = {
            "x": bead_df["fwhm_pixel_x"].values[0],
            "y": bead_df["fwhm_pixel_y"].values[0],
            "z": bead_df["fwhm_pixel_z"].values[0],
        }
    r_sq = {
        "x": bead_df["fit_gaussian_r2_x"].values[0],
        "y": bead_df["fit_gaussian_r2_y"].values[0],
        "z": bead_df["fit_gaussian_r2_z"].values[0],
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
    channel_name = mm_image.channel_series.channels[
        channel_index
    ].name  # TODO: rename channel_names to channels

    title = f"Channel {channel_name}: Bead number {bead_index}"
    return (
        fig_mip_go,
        title,
    )


def fig_bead(
    mips,
    color,
    invert,
    profiles,
    fwhms,
    r_sq,
    voxel_size={"x": None, "y": None, "z": None},
):
    axis_lengths = {
        "x": mips["z"].shape[1],
        "y": mips["z"].shape[0],
        "z": mips["x"].shape[1],
    }
    if all(list(voxel_size.values())):
        voxel_size_ratio = voxel_size["z"] / voxel_size["x"]
        physical_unit = "µm"
    else:
        voxel_size_ratio = 1
        physical_unit = "px"
    if invert:
        color = f"{color}_r"

    fig = make_subplots(
        rows=3,
        cols=3,
        column_widths=[
            axis_lengths["x"] * 1.2,
            axis_lengths["x"],
            axis_lengths["z"] * voxel_size_ratio,
        ],
        row_heights=[
            axis_lengths["z"] * voxel_size_ratio,
            axis_lengths["y"],
            axis_lengths["x"] * 1.2,
        ],
        shared_xaxes=True,
        shared_yaxes=True,
        specs=[
            [None, {"type": "heatmap"}, None],
            [{"type": "xy"}, {"type": "heatmap"}, {"type": "heatmap"}],
            [None, {"type": "xy"}, {"type": "xy"}],
        ],
        horizontal_spacing=0.02,
        vertical_spacing=0.02,
    )

    # Add MIP image
    for proj_axis, h_axis, v_axis, row, col, rotate in zip(
        ("x", "y", "z"),
        ("z", "x", "x"),
        ("y", "z", "y"),
        (2, 1, 2),
        (3, 2, 2),
        (False, True, False),
    ):
        fig.add_trace(
            go.Heatmap(z=mips[proj_axis], colorscale=color, showscale=False),
            row=row,
            col=col,
        )
        fig.update_xaxes(
            range=[0, axis_lengths[h_axis]],
            constrain="domain",
            scaleanchor="y2",
            scaleratio=voxel_size_ratio if h_axis == "z" else 1,
            row=row,
            col=col,
        )
        fig.update_yaxes(
            range=[0, axis_lengths[v_axis]],
            constrain="domain",
            scaleanchor="y2",
            scaleratio=voxel_size_ratio if v_axis == "z" else 1,
            row=row,
            col=col,
        )

    # Add profiles
    for axis, row, col, rotate in zip(
        ("x", "y", "z"), (3, 2, 3), (2, 1, 3), (False, True, False)
    ):
        # We want to find the quartiles of the x, y and z axes to plot some pretty tick marks
        quartiles = np.quantile(
            range(axis_lengths[axis]), [0.0, 0.25, 0.5, 0.75, 1.0]
        )

        # We normalize the quartiles to place the 0 in the center of the axis, and we stringify it
        if all(list(voxel_size.values())):
            quartiles_norm = [
                f"{q:.2f}" for q in (quartiles - quartiles[2]) * voxel_size[axis]
            ]
        else:
            quartiles_norm = quartiles - quartiles[2]

        if rotate:
            plot_x_axis = "y"
            plot_y_axis = "x"
        else:
            plot_x_axis = "x"
            plot_y_axis = "y"

        # Add traces
        fig.add_trace(
            go.Scatter(
                name=f"{axis.upper()} raw profile",
                mode="lines",
                line=dict(color="red"),
                **{plot_y_axis: profiles[axis]["raw"]},
            ),
            row=row,
            col=col,
        )
        fig.add_trace(
            go.Scatter(
                name=f"{axis.upper()} fitted profile",
                mode="lines",
                line=dict(color="blue", dash="dot"),
                **{plot_y_axis: profiles[axis]["fitted"]},
            ),
            row=row,
            col=col,
        )
        if rotate:
            fig.add_vline(
                x=0.5,
                line_color="gray",
                line_dash="dash",
                annotation_text=f"FWHM<br><b>{fwhms[axis]:.3f}{physical_unit}<b>",
                annotation_align="right",
                annotation_position="bottom right",
                row=row,
                col=col,
            )
            fig.update_xaxes(
                range=[-0.25, 1.25], constrain="domain", row=row, col=col
            )
            fig.update_yaxes(
                title_text=f"{axis.upper()}-axis ({physical_unit})",
                constrain="domain",
                scaleanchor="y2",
                scaleratio=voxel_size_ratio if axis == "z" else 1,
                title_font_size=18,
                ticktext=quartiles_norm,
                tickvals=quartiles,
                row=row,
                col=col,
            )
        else:
            fig.add_hline(
                y=0.5,
                line_color="gray",
                line_dash="dash",
                annotation_text=f"FWHM<br><b>{fwhms[axis]:.3f}{physical_unit}<b>",
                annotation_align="right",
                annotation_position="top right",
                row=row,
                col=col,
            )
            fig.update_xaxes(
                title_text=f"{axis.upper()}-axis ({physical_unit})",
                constrain="domain",
                scaleanchor="y2",
                scaleratio=voxel_size_ratio if axis == "z" else 1,
                title_font_size=18,
                ticktext=quartiles_norm,
                tickvals=quartiles,
                row=row,
                col=col,
            )
            fig.update_yaxes(
                range=[-0.25, 1.25], constrain="domain", row=row, col=col
            )
        fig.add_annotation(
            text=f"R&#178;<br><b>{r_sq[axis]:.3f}<b>",
            align="right" if rotate else "left",
            xanchor="left" if rotate else "right",
            ax=20 if rotate else -40,
            ay=-40 if rotate else -20,
            row=row,
            col=col,
            **{
                plot_x_axis: int(
                    np.quantile(range(profiles[axis]["fitted"].shape[0]), 0.48)
                ),
                plot_y_axis: profiles[axis]["fitted"][
                    int(np.quantile(range(profiles[axis]["fitted"].shape[0]), 0.48))
                ],
            },
        )

    # Force identical physical domains (prevents doubled Z)
    fig.update_layout(
        grid=dict(
            rows=3,
            columns=3,
            pattern="independent",
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        width=800,
        height=800,
        autosize=False,
        margin=dict(l=10, r=10, t=10, b=10),
    )

    return fig


def get_bead_profiles(bead_index, channel_index, image_id, mm_dataset):
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
                f"{image_id}_{channel_index}_{bead_index}_{axis}_raw",
                f"{image_id}_{channel_index}_{bead_index}_{axis}_fitted_gaussian",
            ],
        ].rename(
            columns={
                f"{image_id}_{channel_index}_{bead_index}_{axis}_raw": "raw",
                f"{image_id}_{channel_index}_{bead_index}_{axis}_fitted_gaussian": "fitted",
            }
        )
        for axis, df in profiles.items()
    }
    # We flip the values of the profiles in the y-axis
    profiles["y"] = profiles["y"].iloc[::-1].reset_index(drop=True)

    return profiles
