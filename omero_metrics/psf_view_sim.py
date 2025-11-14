import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

mip_z = np.zeros((25, 25))  # (X,Y)
mip_y = np.zeros((31, 25))  # (X,Z)
mip_x = np.zeros((25, 31))  # (Y,Z)
mip_x[10, 10] = mip_y[10, 10] = mip_z[10, 10] = 1
mips = {
    "x": mip_x,
    "y": mip_y,
    "z": mip_z,
}
profiles_z = pd.DataFrame({"raw": mip_x[10, :], "fitted": mip_x[10, :] - 0.2})
profiles_y = pd.DataFrame({"raw": mip_z[:, 10], "fitted": mip_z[:, 10] - 0.2})
profiles_x = pd.DataFrame({"raw": mip_z[10, :], "fitted": mip_z[10, :] - 0.2})
profiles = {
    "x": profiles_x,
    "y": profiles_y,
    "z": profiles_z,
}


def fig_bead(
    mips,
    profiles,
    fwhms,
    r_sq,
    voxel_size=None,
):
    axis_lengths = {
        "x": mips["z"].shape[1],
        "y": mips["z"].shape[0],
        "z": mips["x"].shape[1],
    }
    if voxel_size is not None:
        voxel_size_ratio = voxel_size["z"] / voxel_size["x"]
        physical_unit = "µ"
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
            go.Heatmap(z=mips[proj_axis], colorscale="hot", showscale=False),
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
        if voxel_size is not None:
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
        fig.add_annotation(
            text=f"R^2<br><b>{r_sq[axis]}<b>",
            align="right" if rotate else "left",
            xanchor="left" if rotate else "right",
            row=row,
            col=col,
            **{
                plot_x_axis: int(
                    np.quantile(range(profiles[axis]["fitted"].shape[0]), 0.4)
                ),
                plot_y_axis: profiles_x["fitted"][
                    int(np.quantile(range(profiles[axis]["fitted"].shape[0]), 0.4))
                ],
            },
        )

        # Adapt Axis
        if rotate:
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


if __name__ == "__main__":
    fig = fig_mip(
        mips,
        profiles,
        fwhms={
            "x": 0.250,
            "y": 0.260,
            "z": 0.722,
        },
        r_sq={
            "x": 0.86,
            "y": 0.88,
            "z": 0.79,
        },
        voxel_size={
            "x": 0.1,
            "y": 0.1,
            "z": 0.25,
        },
    )
    fig.show()
