import logging

import dash
import dash_mantine_components as dmc
import numpy as np
import plotly.express as px
from dash import dcc, html
from django_plotly_dash import DjangoDash

import omero_metrics.dash_apps.utils.omero_metrics_components as my_components
from omero_metrics import views
from omero_metrics.dash_apps.dataset_image.dash_chromatic_shift._quiver import (
    build_quiver_figure,
    get_output_vectors,
)
from omero_metrics.styles import MANTINE_THEME, THEME
from omero_metrics.tools.serializers import deserialize

logger = logging.getLogger(__name__)
dashboard_name = "omero_image_chromatic_shift"

omero_image_chromatic_shift = DjangoDash(name=dashboard_name, serve_locally=True)


def _reference_index(mm_dataset, n_channels):
    """Channel used as the reference by the analysis.

    reference_channel_index is -1 when the reference was chosen automatically;
    the channel actually used is in the key measurements (reference_channel_nr).
    """
    ref = int(mm_dataset.input_parameters.reference_channel_index)
    kms = getattr(getattr(mm_dataset, "output", None), "key_measurements", None) or []
    if kms and kms[0].reference_channel_nr is not None:
        ref = int(kms[0].reference_channel_nr)
    return ref if 0 <= ref < n_channels else 0


def _norm(plane):
    plane = np.asarray(plane, dtype=float)
    mn, mx = float(plane.min()), float(plane.max())
    if mx <= mn:
        return np.zeros_like(plane)
    return (plane - mn) / (mx - mn)


def _composite_figure(ref_plane, mov_plane, title):
    """Two-colour overlay: reference channel in green, moving channel in magenta.

    Where the two coincide the pixels look white/grey; a chromatic shift shows up
    as green/magenta fringing at edges.
    """
    g = _norm(ref_plane)
    m = _norm(mov_plane)
    rgb = np.clip(np.stack([m, g, m], axis=-1), 0.0, 1.0)  # R=mov, G=ref, B=mov
    rgb = (rgb * 255).astype(np.uint8)
    fig = px.imshow(rgb)
    fig.update_layout(
        title=title,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False, scaleanchor="x")
    return fig


omero_image_chromatic_shift.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        my_components.header_component(
            "Chromatic Shift Analysis",
            "Before/after correction and local distortion",
            "Chromatic Shift Analysis",
            load_buttons=False,
        ),
        dmc.Container(
            [
                html.Div(id="cs_blank_input"),
                dmc.Paper(
                    [
                        dmc.Group(
                            [
                                dmc.Text(
                                    "Moving channel (compared to the reference channel)",
                                    fw=500,
                                    c=THEME["primary"],
                                ),
                                dmc.Group(
                                    [
                                        dmc.Switch(
                                            id="cs_mip_switch",
                                            label="Max projection (MIP)",
                                            checked=True,
                                            color=THEME["primary"],
                                        ),
                                        dmc.Select(
                                            id="cs_image_channel_selector",
                                            label="Channel",
                                            w=220,
                                            allowDeselect=False,
                                            leftSection=my_components.get_icon(
                                                "material-symbols:layers"
                                            ),
                                        ),
                                    ],
                                    gap="lg",
                                ),
                            ],
                            justify="space-between",
                        ),
                        dmc.Space(h=8),
                        dmc.Text("Z plane (used when MIP is off)", size="sm"),
                        dcc.Slider(
                            id="cs_z_slider",
                            min=0,
                            max=1,
                            step=1,
                            value=0,
                            disabled=True,
                        ),
                    ],
                    p="md",
                    radius="md",
                    withBorder=True,
                    shadow="sm",
                ),
                dmc.Space(h=12),
                dmc.Paper(
                    [
                        dmc.Text(
                            "Before / After correction "
                            "(reference = green, moving = magenta)",
                            size="lg",
                            fw=500,
                            c=THEME["primary"],
                        ),
                        dmc.Grid(
                            [
                                dmc.GridCol(
                                    dcc.Graph(
                                        id="cs_before_graph",
                                        figure={},
                                        style={"height": "500px"},
                                    ),
                                    span=6,
                                ),
                                dmc.GridCol(
                                    dcc.Graph(
                                        id="cs_after_graph",
                                        figure={},
                                        style={"height": "500px"},
                                    ),
                                    span=6,
                                ),
                            ],
                        ),
                    ],
                    p="md",
                    radius="md",
                    withBorder=True,
                    shadow="sm",
                ),
                dmc.Space(h=12),
                dmc.Paper(
                    [
                        dmc.Text(
                            "Local Distortion Quiver",
                            size="lg",
                            fw=500,
                            c=THEME["primary"],
                        ),
                        dcc.Graph(
                            id="cs_image_graph",
                            figure={},
                            style={"height": "600px"},
                        ),
                    ],
                    p="md",
                    radius="md",
                    withBorder=True,
                    shadow="sm",
                ),
            ],
            size="xl",
            p="md",
            style={"backgroundColor": THEME["surface"]},
        ),
    ],
)


@omero_image_chromatic_shift.expanded_callback(
    dash.dependencies.Output("cs_image_channel_selector", "data"),
    dash.dependencies.Output("cs_image_channel_selector", "value"),
    [dash.dependencies.Input("cs_blank_input", "children")],
)
def update_channels(_, **kwargs):
    context = deserialize(kwargs["session_state"]["context"])
    channels = context["mm_image"].channel_series.channels
    ref_idx = _reference_index(context["mm_dataset"], len(channels))
    options = [{"label": c.name, "value": str(i)} for i, c in enumerate(channels)]
    # Default to the first non-reference channel (that's what has a shift/quiver).
    default = next(
        (str(i) for i in range(len(channels)) if i != ref_idx), "0"
    )
    return options, default


# Grey out (disable) the Z slider while MIP is on.
omero_image_chromatic_shift.clientside_callback(
    "function(mip_on) { return !!mip_on; }",
    dash.dependencies.Output("cs_z_slider", "disabled"),
    dash.dependencies.Input("cs_mip_switch", "checked"),
)


@omero_image_chromatic_shift.expanded_callback(
    dash.dependencies.Output("cs_z_slider", "max"),
    dash.dependencies.Output("cs_z_slider", "value"),
    dash.dependencies.Output("cs_z_slider", "marks"),
    [dash.dependencies.Input("cs_blank_input", "children")],
)
def update_z_slider(_, **kwargs):
    context = deserialize(kwargs["session_state"]["context"])
    nz = int(context["size_z"])
    max_z = max(nz - 1, 0)
    step = max(1, nz // 8)
    marks = {z: str(z) for z in range(0, nz, step)}
    marks[max_z] = str(max_z)
    return max_z, nz // 2, marks


@omero_image_chromatic_shift.expanded_callback(
    dash.dependencies.Output("cs_before_graph", "figure"),
    dash.dependencies.Output("cs_after_graph", "figure"),
    [
        dash.dependencies.Input("cs_image_channel_selector", "value"),
        dash.dependencies.Input("cs_z_slider", "value"),
        dash.dependencies.Input("cs_mip_switch", "checked"),
    ],
)
def update_before_after(channel_index, z_value, mip_on, **kwargs):
    try:
        context = deserialize(kwargs["session_state"]["context"])
        mm_dataset = context["mm_dataset"]
        channels = context["mm_image"].channel_series.channels
        ref_idx = _reference_index(mm_dataset, len(channels))
        ch = int(channel_index)
        ref_name = channels[ref_idx].name
        mov_name = channels[ch].name
        use_mip = mip_on or z_value is None

        def planes(image_id, mip, ann_id=None):
            """(reference, moving) planes: from the stored MIP, or the Z plane
            read from OMERO on demand (corrected for display with the
            correction file ``ann_id`` when given)."""
            if image_id is None or mip is None:
                return None, None
            if use_mip:
                return mip[..., ref_idx], mip[..., ch]
            if ann_id is not None:
                ref_plane, mov_plane = views.corrected_section(
                    kwargs["request"], image_id=image_id, ann_id=ann_id,
                    z=int(z_value), channels=[ref_idx, ch],
                )
            else:
                ref_plane, mov_plane = views.image_planes(
                    kwargs["request"], image_id=image_id, z=int(z_value),
                    channels=[ref_idx, ch],
                )
            return ref_plane, mov_plane

        zlabel = "MIP" if use_mip else f"Z={int(z_value)}"

        b_ref, b_mov = planes(context["image_id"], context["mip_z"])
        before = _composite_figure(
            b_ref, b_mov, f"Before ({zlabel}) — {ref_name} (green) vs {mov_name} (magenta)"
        )

        ann_id = context.get("correction_ann_id")
        if context.get("corrected_image_id") is not None:
            a_ref, a_mov = planes(context["corrected_image_id"], context.get("corrected_mip"))
            after_title = f"After ({zlabel}) — {ref_name} vs {mov_name}"
        else:
            # average_references: this image has no corrected image of its own;
            # the dataset's correction is applied to the displayed section.
            a_ref, a_mov = planes(context["image_id"], context.get("corrected_mip"), ann_id)
            after_title = (
                f"After ({zlabel}, corrected for display) — {ref_name} vs {mov_name}"
            )
        if a_ref is not None:
            after = _composite_figure(a_ref, a_mov, after_title)
        else:
            after = px.imshow([[0]])
            after.update_layout(title="Corrected image not available")
        return before, after
    except Exception as e:
        logger.error(f"Error building before/after composite: {e}")
        empty = px.imshow([[0]])
        return empty, empty


@omero_image_chromatic_shift.expanded_callback(
    dash.dependencies.Output("cs_image_graph", "figure"),
    [dash.dependencies.Input("cs_image_channel_selector", "value")],
)
def update_image(channel_index, **kwargs):
    try:
        context = deserialize(kwargs["session_state"]["context"])
        mm_image = context["mm_image"]
        mm_dataset = context["mm_dataset"]
        channel_index = int(channel_index)
        image_id = mm_image.data_reference.omero_object_id
        channel_name = mm_image.channel_series.channels[channel_index].name

        background = context["mip_z"][..., channel_index]

        target_name = f"local_distortion_vectors_{image_id}_ch{channel_index}"
        rois = get_output_vectors(mm_dataset)
        roi = next((r for r in rois if r.name == target_name), None)
        if roi is None:
            # average_references: one distortion map (named after the first
            # image) is shared by all the images of the dataset.
            suffix = f"_ch{channel_index}"
            shared = [r for r in rois if r.name.endswith(suffix)]
            if len({r.name for r in shared}) == 1:
                roi = shared[0]
        lines = roi.lines if roi is not None else []

        return build_quiver_figure(
            lines,
            background=background,
            title=f"Channel {channel_name} — local distortion",
            colorscale="Greys",
        )
    except Exception as e:
        logger.error(f"Error updating chromatic-shift image: {e}")
        return build_quiver_figure([], title="Error loading image")
