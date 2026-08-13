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
dashboard_name = "omero_image_coregistration"

omero_image_coregistration = DjangoDash(name=dashboard_name, serve_locally=True)

omero_image_coregistration.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        # Header Section
        dsc.image_header(
            "Co-registration Analysis",
            "Analysis of channel co-registration",
            "Co-registration Analysis",
        ),
        # Main Content
        dmc.Container(
            [
                dsc.blank_input(),
                dmc.Stack(
                    [
                        dsc.intensity_chart(),
                        dmc.Paper(
                            id="coregistration-bead-paper",
                            shadow="sm",
                            p="md",
                            radius="md",
                            children=[
                                dmc.Group(
                                    [
                                        dmc.Text(
                                            id="coregistration-bead-title",
                                            children="Bead image (select bead to view)",
                                            size="lg",
                                            fw=500,
                                            c=THEME["primary"],
                                        ),
                                    ],
                                    justify="space-between",
                                ),
                                dcc.Graph(
                                    id="coregistration-bead-graph",
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

BEADS_HOVER_INFO = {
    "Bead number": "bead_id",
    "Sigma LoG": "sigma_LoG",
    "Considered valid": dsc.hover_flag("considered_valid"),
    "Considered self proximity": dsc.hover_flag("considered_self_proximity"),
    "Considered lateral edge": dsc.hover_flag("considered_lateral_edge"),
    "Considered axial edge": dsc.hover_flag("considered_axial_edge"),
    "Considered outlier": dsc.hover_flag("considered_distance_3d_micron_outlier"),
}


dsc.register_intensity_chart_callbacks(
    omero_image_coregistration,
    "multiwavelength_beads_images",
    hover_info=BEADS_HOVER_INFO,
)


@omero_image_coregistration.expanded_callback(
    dash.dependencies.Output("coregistration-bead-graph", "figure"),
    dash.dependencies.Output("coregistration-bead-title", "children"),
    [
        dash.dependencies.Input("intensity-chart", "clickData"),
        dash.dependencies.Input("intensity-chart-channel-select", "value"),
    ],
    prevent_initial_call=True,
)
def update_single_bead_image(points, channel_index, *, session_state):
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
    channel_name = bead_df["channel_name"].values[0]

    reference_channel_index = bead_df["reference_channel_nr"].values[0]
    reference_bead_array = beads_array[bead_index, :, :, :, reference_channel_index]
    reference_channel_name = bead_df["reference_channel_name"].values[0]

    mips = {
        "x": np.transpose(np.max(bead_array, axis=2)),
        "y": np.max(bead_array, axis=1),
        "z": np.max(bead_array, axis=0),
        "x_ref": np.transpose(np.max(reference_bead_array, axis=2)),
        "y_ref": np.max(reference_bead_array, axis=1),
        "z_ref": np.max(reference_bead_array, axis=0),
    }
    mips = {a: np.sqrt(mip) for a, mip in mips.items()}
    profiles = {
        "x": np.mean(bead_array, axis=(0, 1)),
        "y": np.mean(bead_array, axis=(0, 2)),
        "z": np.mean(bead_array, axis=(1, 2)),
        "x_ref": np.mean(reference_bead_array, axis=(0, 1)),
        "y_ref": np.mean(reference_bead_array, axis=(0, 2)),
        "z_ref": np.mean(reference_bead_array, axis=(1, 2)),
    }
    profiles = {
        k: (p - np.min(p)) / (np.max(p) - np.min(p)) for k, p in profiles.items()
    }

    voxel_size = {
        "x": mm_image.voxel_size_x_micron,
        "y": mm_image.voxel_size_y_micron,
        "z": mm_image.voxel_size_z_micron,
    }

    translations = {
        "x": bead_df["translation_x_px"].values[0],
        "y": bead_df["translation_y_px"].values[0],
        "z": bead_df["translation_z_px"].values[0],
    }

    fig_mip_go = fig_coregisration_bead(
        mips=mips,
        profiles=profiles,
        channel_name=channel_name,
        reference_channel_name=reference_channel_name,
        translations=translations,
        voxel_size=voxel_size,
    )

    title = f"Channel {channel_name} vs reference channel {reference_channel_name}: Bead number {bead_index}"
    return (
        fig_mip_go,
        title,
    )


def merge_mips_rgb(channel_mip, reference_mip, channel_vmax, reference_vmax):
    """Combine two MIPs into a single additive RGB raster: the channel in red,
    the reference channel in green and, where both overlap, yellow.
    Each channel is scaled by its own maximum so that both remain visible
    regardless of their relative brightness.
    """

    def _to_uint8(mip, vmax):
        if not vmax:
            return np.zeros(mip.shape, dtype=np.uint8)
        return np.clip(mip / vmax * 255.0, 0, 255).astype(np.uint8)

    rgb = np.zeros(channel_mip.shape + (3,), dtype=np.uint8)
    rgb[..., 0] = _to_uint8(channel_mip, channel_vmax)
    rgb[..., 1] = _to_uint8(reference_mip, reference_vmax)
    return rgb


def fig_coregisration_bead(
    mips,
    profiles,
    channel_name,
    reference_channel_name,
    translations,
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

    # Add MIP image: channel in red, reference channel in green, overlap in yellow
    channel_vmax = max(np.max(mips[a]) for a in ("x", "y", "z"))
    reference_vmax = max(np.max(mips[a]) for a in ("x_ref", "y_ref", "z_ref"))

    for proj_axis, proj_axis_ref, h_axis, v_axis, row, col, rotate in zip(
        ("x", "y", "z"),
        ("x_ref", "y_ref", "z_ref"),
        ("z", "x", "x"),
        ("y", "z", "y"),
        (2, 1, 2),
        (3, 2, 2),
        (False, True, False),
    ):
        fig.add_trace(
            go.Image(
                z=merge_mips_rgb(
                    mips[proj_axis],
                    mips[proj_axis_ref],
                    channel_vmax,
                    reference_vmax,
                ),
                hovertemplate=(
                    f"{channel_name}: %{{z[0]}}<br>"
                    f"{reference_channel_name}: %{{z[1]}}"
                    "<extra></extra>"
                ),
            ),
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

    # Add centers
    for axis, axis_ref, row, col, rotate in zip(
        ("x", "y", "z"),
        ("x_ref", "y_ref", "z_ref"),
        (3, 2, 3),
        (2, 1, 3),
        (False, True, False),
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
                name=f"Mean {channel_name} {axis.upper()} profile",
                mode="lines",
                line=dict(color="red"),
                **{plot_y_axis: profiles[axis]},
            ),
            row=row,
            col=col,
        )
        fig.add_trace(
            go.Scatter(
                name=f"Mean {reference_channel_name} {axis.upper()} profile",
                mode="lines",
                line=dict(color="green"),
                **{plot_y_axis: profiles[axis_ref]},
            ),
            row=row,
            col=col,
        )

        if rotate:
            fig.add_hline(
                y=len(profiles[axis]) // 2 - translations[axis],
                line_color="red",
                line_dash="dash",
                annotation_text=f"{axis} offset<br><b>{translations[axis]:.3f}vx<b>",
                annotation_align="right",
                annotation_position="bottom right",
                row=row,
                col=col,
            )
            fig.add_hline(
                y=len(profiles[axis]) // 2,
                line_color="green",
                line_dash="dash",
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
                autorange="reversed",
                title_font_size=18,
                ticktext=quartiles_norm,
                tickvals=quartiles,
                row=row,
                col=col,
            )
        else:
            fig.add_vline(
                x=len(profiles[axis]) // 2 - translations[axis],
                line_color="red",
                line_dash="dash",
                annotation_text=f"{axis} offset<br><b>{translations[axis]:.3f}vx<b>",
                annotation_align="right",
                annotation_position="top right",
                row=row,
                col=col,
            )
            fig.add_vline(
                x=len(profiles[axis]) // 2,
                line_color="green",
                line_dash="dash",
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
