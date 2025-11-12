import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

mip_z = np.zeros((25, 25))  # (X,Y)
mip_y = np.zeros((31, 25))  # (X,Z)
mip_x = np.zeros((25, 31))  # (Y,Z)
mip_x[10, 10] = mip_y[10, 10] = mip_z[10, 10] = 1
profiles_z = pd.DataFrame({"raw": mip_x[10, :], "fitted": mip_x[10, :] - 0.2})
profiles_y = pd.DataFrame({"raw": mip_z[:, 10], "fitted": mip_z[:, 10] - 0.2})
profiles_x = pd.DataFrame({"raw": mip_z[10, :], "fitted": mip_z[10, :] - 0.2})


def fig_mip(
    mip_x,
    mip_y,
    mip_z,
    profiles_x,
    profiles_y,
    profiles_z,
    fwhm_x,
    fwhm_y,
    fwhm_z,
    voxel_size=None,
):
    voxel_size_ratio = voxel_size[0] / voxel_size[2] if voxel_size is not None else 1

    fig = make_subplots(
        rows=3,
        cols=3,
        column_widths=[
            mip_x.shape[1] * voxel_size_ratio,
            mip_z.shape[1],
            mip_y.shape[0] * voxel_size_ratio,
        ],
        row_heights=[
            mip_x.shape[1] * voxel_size_ratio,
            mip_z.shape[0],
            mip_x.shape[1] * voxel_size_ratio,
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

    # Add traces
    fig.add_trace(go.Heatmap(z=mip_y, colorscale="hot", showscale=False), row=1, col=2)
    fig.add_trace(go.Heatmap(z=mip_z, colorscale="hot", showscale=False), row=2, col=2)
    fig.add_trace(go.Heatmap(z=mip_x, colorscale="hot", showscale=False), row=2, col=3)
    fig.add_trace(
        go.Scatter(
            y=profiles_x["raw"],
            name="raw X profile",
            mode="lines",
            line=dict(color="red"),
        ),
        row=3,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            y=profiles_x["fitted"],
            name="fitted X profile",
            mode="lines",
            line=dict(color="blue", dash="dot"),
        ),
        row=3,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=profiles_y["raw"],
            name="raw Y profile",
            mode="lines",
            line=dict(color="red"),
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=profiles_y["fitted"],
            name="fitted Y profile",
            mode="lines",
            line=dict(color="blue", dash="dot"),
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            y=profiles_z["raw"],
            name="raw Z profile",
            mode="lines",
            line=dict(color="red"),
        ),
        row=3,
        col=3,
    )
    fig.add_trace(
        go.Scatter(
            y=profiles_z["fitted"],
            name="fitted Z profile",
            mode="lines",
            line=dict(color="blue", dash="dot"),
        ),
        row=3,
        col=3,
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

    # We want to find the quartiles of the x, y and z axes to plot some pretty tick marks
    z_axis_quartiles = np.quantile(range(mip_x.shape[1]), [0.0, 0.25, 0.5, 0.75, 1.0])
    y_axis_quartiles = np.quantile(range(mip_z.shape[0]), [0.0, 0.25, 0.5, 0.75, 1.0])
    x_axis_quartiles = np.quantile(range(mip_z.shape[1]), [0.0, 0.25, 0.5, 0.75, 1.0])

    # We normalize the quartiles to place the 0 in the center of the plot
    if voxel_size is not None:
        z_axis_quartiles_norm = (z_axis_quartiles - z_axis_quartiles[2]) * voxel_size[0]
        y_axis_quartiles_norm = (y_axis_quartiles - y_axis_quartiles[2]) * voxel_size[1]
        x_axis_quartiles_norm = (x_axis_quartiles - x_axis_quartiles[2]) * voxel_size[2]
        # We also need to stringify the quartiles to use them as tick texts
        z_axis_quartiles_norm = [f"{q:.2f}" for q in z_axis_quartiles_norm]
        y_axis_quartiles_norm = [f"{q:.2f}" for q in y_axis_quartiles_norm]
        x_axis_quartiles_norm = [f"{q:.2f}" for q in x_axis_quartiles_norm]
        physical_unit = "µ"
    else:
        z_axis_quartiles_norm = z_axis_quartiles - z_axis_quartiles[2]
        y_axis_quartiles_norm = y_axis_quartiles - y_axis_quartiles[2]
        x_axis_quartiles_norm = x_axis_quartiles - x_axis_quartiles[2]
        physical_unit = "px"

    # Fix coordinate ranges to match image dimensions
    # Z-mip: XY plane
    fig.update_xaxes(
        range=[0, mip_z.shape[1]],
        constrain="domain",
        scaleanchor="y2",
        scaleratio=1,
        row=2,
        col=2,
    )
    fig.update_yaxes(
        range=[mip_z.shape[0], 0],
        constrain="domain",
        scaleanchor="y2",
        scaleratio=1,
        row=2,
        col=2,
    )

    # Y-mip: XZ plane
    fig.update_xaxes(
        range=[0, mip_y.shape[1]],
        constrain="domain",
        scaleanchor="y2",
        scaleratio=1,
        row=1,
        col=2,
    )
    fig.update_yaxes(
        range=[0, mip_y.shape[0]],
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
        range=[0, mip_x.shape[1]],
        constrain="domain",
        scaleanchor="y2",
        scaleratio=voxel_size_ratio,
        row=2,
        col=3,
    )
    fig.update_yaxes(
        range=[
            mip_x.shape[0],
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
    fig.add_annotation(
        x=0.5,
        y=1.05,
        text="Z-profile",
        showarrow=False,
        xanchor="left",
        yanchor="top",
        row=3,
        col=3,
    )

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
        mip_x,
        mip_y,
        mip_z,
        profiles_x,
        profiles_y,
        profiles_z,
        0.250,
        0.260,
        0.722,
        (0.25, 0.1, 0.1),
    )
    fig.show()
