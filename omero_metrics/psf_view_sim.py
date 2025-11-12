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


def fig_mip(
    mips,
    profiles,
    fwhms,
    r_sq,
    voxel_size=None,
):
    # We want to find the quartiles of the x, y and z axes to plot some pretty tick marks
    z_axis_quartiles = np.quantile(
        range(mips["x"].shape[1]), [0.0, 0.25, 0.5, 0.75, 1.0]
    )
    y_axis_quartiles = np.quantile(
        range(mips["z"].shape[0]), [0.0, 0.25, 0.5, 0.75, 1.0]
    )
    x_axis_quartiles = np.quantile(
        range(mips["z"].shape[1]), [0.0, 0.25, 0.5, 0.75, 1.0]
    )

    # We normalize the quartiles to place the 0 in the center of the plot
    if voxel_size is not None:
        z_axis_quartiles_norm = (
            z_axis_quartiles - z_axis_quartiles[2]
        ) * voxel_size["z"]
        y_axis_quartiles_norm = (
            y_axis_quartiles - y_axis_quartiles[2]
        ) * voxel_size["y"]
        x_axis_quartiles_norm = (
            x_axis_quartiles - x_axis_quartiles[2]
        ) * voxel_size["x"]
        # We also need to stringify the quartiles to use them as tick texts
        z_axis_quartiles_norm = [f"{q:.2f}" for q in z_axis_quartiles_norm]
        y_axis_quartiles_norm = [f"{q:.2f}" for q in y_axis_quartiles_norm]
        x_axis_quartiles_norm = [f"{q:.2f}" for q in x_axis_quartiles_norm]
        voxel_size_ratio = voxel_size["z"] / voxel_size["x"]
        physical_unit = "µ"
    else:
        z_axis_quartiles_norm = z_axis_quartiles - z_axis_quartiles[2]
        y_axis_quartiles_norm = y_axis_quartiles - y_axis_quartiles[2]
        x_axis_quartiles_norm = x_axis_quartiles - x_axis_quartiles[2]
        physical_unit = "px"
        voxel_size_ratio = 1

    fig = make_subplots(
        rows=3,
        cols=3,
        column_widths=[
            mips["x"].shape[1] * voxel_size_ratio,
            mips["z"].shape[1],
            mips["y"].shape[0] * voxel_size_ratio,
        ],
        row_heights=[
            mips["x"].shape[1] * voxel_size_ratio,
            mips["z"].shape[0],
            mips["x"].shape[1] * voxel_size_ratio,
        ],
        shared_xaxes=True,
        shared_yaxes=True,
        specs=[
            [None, {"type": "heatmap"}, None],
            [{"type": "xy"}, {"type": "heatmap"}, {"type": "heatmap"}],
            [None, {"type": "xy"}, {"type": "xy"}],
        ],
        # subplot_titles=[
        #     "XZ-mip",
        #     "Y-profiles",
        #     "XY-mip",
        #     "YZ-mip",
        #     "X-profiles",
        #     "Z-profiles"
        # ],
        # column_titles=["", "X", "Z"],
        # row_titles=["Z", "Y", ""],
        horizontal_spacing=0.02,
        vertical_spacing=0.02,
    )

    # Add MIP image
    for axis, row, col, rotate in zip(
        ("x", "y", "z"),
        (2, 1, 2),
        (3, 2, 2),
        (False, True, False),
    ):
        if rotate:
            plot_x_axis = "y"
            plot_y_axis = "x"
        else:
            plot_x_axis = "x"
            plot_y_axis = "y"

        fig.add_trace(
            go.Heatmap(z=mips[axis], colorscale="hot", showscale=False),
            row=row,
            col=col,
        )

    # Add profiles
    for axis, row, col, rotate in zip(
        ("x", "y", "z"), (3, 2, 3), (2, 1, 3), (False, True, False)
    ):
        if rotate:
            plot_x_axis = "y"
            plot_y_axis = "x"
        else:
            plot_x_axis = "x"
            plot_y_axis = "y"

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

    # # X profiles
    # fig.add_trace(
    #     go.Scatter(
    #         y=profiles_x["raw"],
    #         name="X raw profile",
    #         mode="lines",
    #         line=dict(color="red"),
    #     ),
    #     row=3,
    #     col=2,
    # )
    # fig.add_trace(
    #     go.Scatter(
    #         y=profiles_x["fitted"],
    #         name="X fitted profile",
    #         mode="lines",
    #         line=dict(color="blue", dash="dot"),
    #     ),
    #     row=3,
    #     col=2,
    # )
    # fig.add_hline(
    #     y=0.5,
    #     line_color="gray",
    #     line_dash="dash",
    #     annotation_text="FWHM<br><b>0.230µ<b>",
    #     annotation_align="right",
    #     row=3, col=2,
    # )
    # fig.add_annotation(
    #     x=int(np.quantile(range(profiles_x["fitted"].shape[0]), .4)),
    #     y=profiles_x["fitted"][int(np.quantile(range(profiles_x["fitted"].shape[0]), .4))],
    #     text="R^2<br><b>0.85<b>",
    #     align="left",
    #     xanchor="right",
    #     row=3,
    #     col=2,
    # )
    #
    # # Y profiles
    # fig.add_trace(
    #     go.Scatter(
    #         x=profiles_y["raw"],
    #         name="Y raw profile",
    #         mode="lines",
    #         line=dict(color="red"),
    #     ),
    #     row=2,
    #     col=1,
    # )
    # fig.add_trace(
    #     go.Scatter(
    #         x=profiles_y["fitted"],
    #         name="Y fitted profile",
    #         mode="lines",
    #         line=dict(color="blue", dash="dot"),
    #     ),
    #     row=2,
    #     col=1,
    # )
    #
    # # Z profiles
    # fig.add_trace(
    #     go.Scatter(
    #         y=profiles_z["raw"],
    #         name="Z raw profile",
    #         mode="lines",
    #         line=dict(color="red"),
    #     ),
    #     row=3,
    #     col=3,
    # )
    # fig.add_trace(
    #     go.Scatter(
    #         y=profiles_z["fitted"],
    #         name="Z fitted profile",
    #         mode="lines",
    #         line=dict(color="blue", dash="dot"),
    #     ),
    #     row=3,
    #     col=3,
    # )

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

    # Fix coordinate ranges to match image dimensions
    # Z-mip: XY plane
    fig.update_xaxes(
        range=[0, mips["z"].shape[1]],
        constrain="domain",
        scaleanchor="y2",
        scaleratio=1,
        row=2,
        col=2,
    )
    fig.update_yaxes(
        range=[mips["z"].shape[0], 0],
        constrain="domain",
        scaleanchor="y2",
        scaleratio=1,
        row=2,
        col=2,
    )

    # Y-mip: XZ plane
    fig.update_xaxes(
        range=[0, mips["y"].shape[1]],
        constrain="domain",
        scaleanchor="y2",
        scaleratio=1,
        row=1,
        col=2,
    )
    fig.update_yaxes(
        range=[0, mips["y"].shape[0]],
        constrain="domain",
        scaleanchor="y2",
        scaleratio=voxel_size_ratio,
        # Replaces automatic tick marks with custom ones
        ticktext=z_axis_quartiles_norm,
        tickvals=z_axis_quartiles,
        row=1,
        col=2,
    )

    # X-mip: YZ plane
    fig.update_xaxes(
        range=[0, mips["x"].shape[1]],
        constrain="domain",
        scaleanchor="y2",
        scaleratio=voxel_size_ratio,
        row=2,
        col=3,
    )
    fig.update_yaxes(
        range=[
            mips["x"].shape[0],
            0,
        ],  # We reverse the Y axis here to match the image orientation
        constrain="domain",
        scaleanchor="y2",
        scaleratio=1,
        row=2,
        col=3,
    )

    # Z-profile
    fig.update_xaxes(
        title_text=f"Z-axis ({physical_unit})",
        constrain="domain",
        scaleanchor="y2",
        scaleratio=voxel_size_ratio,
        title_font_size=18,
        # Replaces automatic tick marks with custom ones
        ticktext=z_axis_quartiles_norm,
        tickvals=z_axis_quartiles,
        row=3,
        col=3,
    )
    fig.update_yaxes(range=[-0.25, 1.25], constrain="domain", row=3, col=3)

    # Y-profile
    fig.update_xaxes(range=[-0.25, 1.25], constrain="domain", row=2, col=1)
    fig.update_yaxes(
        title_text=f"Y-axis ({physical_unit})",
        constrain="domain",
        scaleanchor="y2",
        scaleratio=1,
        title_font_size=18,
        # Replaces automatic tick marks with custom ones
        ticktext=y_axis_quartiles_norm,
        tickvals=y_axis_quartiles,
        row=2,
        col=1,
    )

    # X-profile
    fig.update_xaxes(
        title_text=f"X-axis ({physical_unit})",
        constrain="domain",
        scaleanchor="y2",
        scaleratio=1,
        title_font_size=18,
        # Replaces automatic tick marks with custom ones
        ticktext=x_axis_quartiles_norm,
        tickvals=x_axis_quartiles,
        row=3,
        col=2,
    )
    fig.update_yaxes(range=[-0.25, 1.25], row=3, col=2)

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
