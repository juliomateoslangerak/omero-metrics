"""Helpers to build a plotly quiver (arrow) figure from chromatic-shift outputs.

The local distortion field produced by the chromatic-shift analysis is stored as
`local_distortion_vectors`: a list of ROIs, one per non-reference channel and per
image, each holding `Line` shapes that go from a grid point to that point plus the
local displacement (scaled for visibility). Here we turn those lines back into a
quiver plot with arrowheads.
"""

import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go


def get_output_vectors(mm_dataset):
    """Return the list of local-distortion-vector ROIs, robust to access style."""
    output = mm_dataset.output
    vectors = getattr(output, "local_distortion_vectors", None)
    if vectors is None:
        try:
            vectors = output["local_distortion_vectors"]
        except Exception:
            vectors = []
    return vectors or []


def lines_to_uv(lines):
    """Convert a list of mm_schema.Line into quiver components (x, y, u, v)."""
    x, y, u, v = [], [], [], []
    for ln in lines:
        x.append(float(ln.x1))
        y.append(float(ln.y1))
        u.append(float(ln.x2) - float(ln.x1))
        v.append(float(ln.y2) - float(ln.y1))
    return np.array(x), np.array(y), np.array(u), np.array(v)


def build_quiver_figure(
    lines,
    background=None,
    title="Local distortion",
    colorscale="Greys",
    arrow_color="#00b0ff",
):
    """Build a plotly figure with an optional heatmap background and a quiver.

    ``lines`` is a list of mm_schema.Line; ``background`` is an optional 2D array
    (e.g. a channel MIP) drawn underneath the arrows.
    """
    fig = go.Figure()

    if background is not None:
        fig.add_trace(
            go.Heatmap(z=background, colorscale=colorscale, showscale=False)
        )

    if lines:
        x, y, u, v = lines_to_uv(lines)
        quiver = ff.create_quiver(
            x,
            y,
            u,
            v,
            scale=1.0,
            arrow_scale=0.3,
            line=dict(color=arrow_color, width=1.5),
            name="distortion",
        )
        for trace in quiver.data:
            fig.add_trace(trace)
    else:
        fig.add_annotation(
            text="No local distortion field available "
            "(run with local alignment enabled).",
            showarrow=False,
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
        )

    # Image convention: y increases downward, keep pixels square.
    fig.update_yaxes(
        autorange="reversed",
        scaleanchor="x",
        scaleratio=1,
        showgrid=False,
        zeroline=False,
        visible=False,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_layout(
        title=title,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
