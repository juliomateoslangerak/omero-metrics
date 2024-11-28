import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots
from typing import Union


def fig_mip(mip_x, mip_y, mip_z):
    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[[{}, {}], [{"colspan": 2}, None]],
        subplot_titles=("MIP X axis", "MIP Y axis", "MIP Z axis"),
    )
    fig = fig.add_trace(mip_x.data[0], row=1, col=1)
    fig = fig.add_trace(mip_y.data[0], row=1, col=2)
    fig = fig.add_trace(mip_z.data[0], row=2, col=1)
    fig = fig.update_layout(
        # title_text=title,
        coloraxis=dict(colorscale="hot"),
        autosize=False,
    )
    fig.update_layout(
        {  # "margin": {"l": 10, "r": 10, "t": 10, "b": 10},
            "xaxis": {
                "visible": False,
                "automargin": False,
                "rangemode": "nonnegative",
            },
            "xaxis2": {
                "visible": False,
                "automargin": False,
                "rangemode": "nonnegative",
            },
            "xaxis3": {
                "visible": False,
                "automargin": False,
                "rangemode": "nonnegative",
            },
            "yaxis": {
                "visible": False,
                "anchor": "x",
                "scaleanchor": "x",
                "autorange": "reversed",
                "automargin": False,
            },
            "yaxis2": {
                "visible": False,
                "anchor": "x2",
                "scaleanchor": "x2",
                "autorange": "reversed",
                "automargin": False,
            },
            "yaxis3": {
                "visible": False,
                "anchor": "x3",
                "scaleanchor": "x3",
                "autorange": "reversed",
                "automargin": False,
            },
        }
    )
    # fig = fig.update_yaxes(automargin=False)
    # fig = fig.update_xaxes(automargin=False)

    return fig


def mip_graphs(
    x0: int,
    xf: int,
    y0: int,
    yf: int,
    stack: Union[np.array, list],
    do_sqrt: bool = True,
):
    image_bead = stack[:, y0:yf, x0:xf]
    image_x = np.max(image_bead, axis=2)
    image_y = np.max(image_bead, axis=1)
    image_z = np.max(image_bead, axis=0)
    if do_sqrt:
        image_x = np.sqrt(image_x)
        image_y = np.sqrt(image_y)
        image_z = np.sqrt(image_z)
    image_x = image_x / image_x.max()
    image_y = image_y / image_y.max()
    image_z = image_z / image_z.max()

    mip_x = px.imshow(
        image_x,
        zmin=image_x.min(),
        zmax=image_x.max(),
    )
    mip_y = px.imshow(
        image_y,
        zmin=image_y.min(),
        zmax=image_y.max(),
    )
    mip_z = px.imshow(
        image_z,
        zmin=image_z.min(),
        zmax=image_z.max(),
    )
    return mip_x, mip_y, mip_z


def crop_bead_index(bead, min_dist, stack):
    x = bead["center_x"].values[0]
    y = bead["center_y"].values[0]
    # z = bead["center_z"].values[0]
    x0 = max(0, x - min_dist)
    y0 = max(0, y - min_dist)
    xf = min(stack.shape[2], x + min_dist)
    yf = min(stack.shape[1], y + min_dist)
    return x0, xf, y0, yf
