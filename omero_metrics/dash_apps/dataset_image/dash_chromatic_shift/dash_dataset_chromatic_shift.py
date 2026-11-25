import logging

import dash
import dash_mantine_components as dmc
from dash import dcc, html
from django_plotly_dash import DjangoDash

from omero_metrics.dash_apps.dataset_image import dataset_shared_components as dsc
from omero_metrics.dash_apps.dataset_image.dash_chromatic_shift._quiver import (
    build_quiver_figure,
    get_output_vectors,
)
from omero_metrics.styles import (
    CONTAINER_STYLE,
    MANTINE_THEME,
    THEME,
)
from omero_metrics.tools.serializers import deserialize

logger = logging.getLogger(__name__)

dashboard_name = "omero_dataset_chromatic_shift"

omero_dataset_chromatic_shift = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)


def _distortion_paper():
    return dmc.Paper(
        children=[
            dmc.Group(
                [
                    dmc.Text(
                        "Local Distortion Field",
                        fw=500,
                        size="lg",
                        c=THEME["primary"],
                    ),
                    dmc.Select(
                        id="cs_vector_selector",
                        label="Channel / image",
                        w=280,
                        allowDeselect=False,
                    ),
                ],
                justify="space-between",
            ),
            dcc.Graph(
                id="cs_quiver_graph",
                figure={},
                style={"height": "600px"},
            ),
        ],
        p="md",
        radius="md",
        withBorder=True,
        shadow="sm",
    )


omero_dataset_chromatic_shift.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dsc.notifications_container(),
        dsc.confirm_delete_modal(),
        dsc.dataset_header(
            "Chromatic Shift",
            "Chromatic Shift Analysis Dashboard",
            "Chromatic Shift Analysis",
        ),
        dmc.Container(
            children=[
                html.Div(id="cs_blank_input"),
                dsc.dataset_table_paper(),
                dmc.Space(h=16),
                _distortion_paper(),
            ],
            style=CONTAINER_STYLE,
        ),
    ],
)


# Register shared callbacks
dsc.register_delete_dataset_callback(omero_dataset_chromatic_shift)
dsc.register_download_datasets_callback(omero_dataset_chromatic_shift)
dsc.register_update_kkm_table_callback(omero_dataset_chromatic_shift)
dsc.register_download_table_callback(omero_dataset_chromatic_shift)
dsc.register_delete_button_loading_callback(omero_dataset_chromatic_shift)


@omero_dataset_chromatic_shift.expanded_callback(
    dash.dependencies.Output("cs_vector_selector", "data"),
    dash.dependencies.Output("cs_vector_selector", "value"),
    [dash.dependencies.Input("cs_blank_input", "children")],
)
def populate_vector_selector(_, **kwargs):
    try:
        context = deserialize(kwargs["session_state"]["context"])
        vectors = get_output_vectors(context["mm_dataset"])
        options = [
            {"label": roi.name or f"field {i}", "value": str(i)}
            for i, roi in enumerate(vectors)
        ]
        value = options[0]["value"] if options else None
        return options, value
    except Exception as e:
        logger.error(f"Error populating vector selector: {e}")
        return [], None


@omero_dataset_chromatic_shift.expanded_callback(
    dash.dependencies.Output("cs_quiver_graph", "figure"),
    [dash.dependencies.Input("cs_vector_selector", "value")],
)
def update_quiver(selected, **kwargs):
    try:
        context = deserialize(kwargs["session_state"]["context"])
        vectors = get_output_vectors(context["mm_dataset"])
        if not vectors or selected is None:
            return build_quiver_figure([], title="No local distortion field")
        roi = vectors[int(selected)]
        return build_quiver_figure(
            roi.lines or [],
            title=roi.name or "Local distortion",
        )
    except Exception as e:
        logger.error(f"Error building quiver: {e}")
        return build_quiver_figure([], title="Error loading distortion field")
