import logging

import dash
import dash_mantine_components as dmc
import numpy as np
import plotly.graph_objs as go
from dash import dcc
from django_plotly_dash import DjangoDash
from plotly.subplots import make_subplots

from omero_metrics.dash_apps.dataset_image import dataset_shared_components as dsc
from omero_metrics.styles import MANTINE_THEME, THEME
from omero_metrics.tools.serializers import deserialize

_MEASUREMENTS = [
    {"label": "Relative position", "value": "relative_position"},
    {"label": "Displacement", "value": "displacement"},
    {"label": "Square displacement", "value": "square_displacement"},
    {"label": "Velocity", "value": "velocity"},
]
_DEFAULT_MEASUREMENT = ["square_displacement"]


logger = logging.getLogger(__name__)
dashboard_name = "omero_image_stage_drift"

omero_image_stage_drift = DjangoDash(name=dashboard_name, serve_locally=True)

omero_image_stage_drift.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        # Header Section
        dsc.image_header(
            "Stage Drift Analysis",
            "Analysis of stage drift",
            "Stage drift Analysis",
        ),
        # Main Content
        dmc.Container(
            [
                dsc.blank_input(),
                dsc.time_chart(
                    measurements=_MEASUREMENTS,
                    default_measurement=_DEFAULT_MEASUREMENT,
                ),
            ],
            size="xl",
            p="md",
            style={"backgroundColor": THEME["surface"]},
        ),
    ],
)


dsc.register_time_chart_callbacks(omero_image_stage_drift)
