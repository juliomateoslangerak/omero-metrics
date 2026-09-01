"""Pieces shared by the two field-illumination dashboards.

``dataset_shared_components`` holds what every dataset dashboard uses; this
module holds what only the field-illumination pair needs -- currently the
intensity-profile chart, in one piece: the profiles it draws, the component,
and the callbacks that feed it.
"""

import dash
import dash_mantine_components as dmc

from omero_metrics.styles import THEME
from omero_metrics.tools import load
from omero_metrics.tools.serializers import deserialize

# The profiles microscope-metrics measures across the field: the pattern
# matching the columns it writes them to, the label the chart shows, and the
# colour it draws them in. One table, because the label has to be both the name
# the columns are renamed to and the name of the series the chart looks for --
# they were separately maintained before, and drifted.
INTENSITY_PROFILES = [
    (r"ch\d+_leftTop_to_rightBottom", "Diagonal (↘)", "blue.3"),
    (r"ch\d+_leftBottom_to_rightTop", "Diagonal (↗)", "blue.7"),
    (r"ch\d+_center_horizontal", "Horizontal (→)", "red.3"),
    (r"ch\d+_center_vertical", "Vertical (↓)", "red.7"),
]

# The ``series`` of the chart, in the order they are legended.
PROFILE_SERIES = [
    {"name": label, "color": color} for _, label, color in INTENSITY_PROFILES
]

CHART_ID = "intensity-profile"
CURVE_TYPE_ID = "profile-type"


def intensity_profile_records(df_intensity_profiles, channel):
    """One channel's profiles, keyed by the names the chart expects.

    ``df_intensity_profiles`` is the loaded ``intensity_profiles`` table, whose
    columns cover every channel; ``channel`` selects one of them.
    """
    df_profile = df_intensity_profiles.filter(regex=f"ch0*{channel}_")
    columns = df_profile.columns
    for pattern, label, _ in INTENSITY_PROFILES:
        # regex=True is not pandas' default. Without it these patterns are
        # matched literally, nothing is renamed, and the columns keep their
        # ch<n>_ names -- which match no series, so the chart comes out empty.
        columns = columns.str.replace(pattern, label, regex=True)
    df_profile.columns = columns
    return df_profile.to_dict("records")


def intensity_profile_paper(**paper_props):
    """The intensity-profile chart, titled, with its curve-type control.

    Extra keyword arguments are passed through to the enclosing ``dmc.Paper``,
    so a dashboard can space it into its own layout. Pair with
    ``register_intensity_profile_callbacks`` to fill it.
    """
    props = {
        "shadow": "sm",
        "p": "md",
        "radius": "md",
        "withBorder": True,
        **paper_props,
    }
    return dmc.Paper(
        children=[
            dmc.Stack(
                [
                    dmc.Group(
                        [
                            dmc.Text(
                                "Intensity Profiles",
                                size="lg",
                                fw=500,
                                c=THEME["primary"],
                            ),
                            dmc.Badge(
                                "Microscope-Metrics Analysis",
                                color="blue",
                                variant="light",
                                size="sm",
                            ),
                            dmc.SegmentedControl(
                                id=CURVE_TYPE_ID,
                                data=[
                                    {"value": "natural", "label": "Smooth"},
                                    {"value": "linear", "label": "Linear"},
                                ],
                                value="natural",
                                color=THEME["primary"],
                            ),
                        ],
                        justify="space-between",
                    ),
                    dmc.LineChart(
                        id=CHART_ID,
                        h=300,
                        dataKey="Pixel",
                        data={},
                        series=PROFILE_SERIES,
                        xAxisLabel="Position (pixels)",
                        yAxisLabel="Intensity",
                        tickLine="y",
                        gridAxis="x",
                        withXAxis=True,
                        withYAxis=True,
                        withLegend=True,
                        strokeWidth=2,
                        withDots=False,
                    ),
                ],
                gap="md",
            ),
        ],
        **props,
    )


def register_intensity_profile_callbacks(app, channel_select_id, per_image=False):
    """Fill the chart from ``channel_select_id`` and wire its curve-type control.

    ``per_image`` picks between the two shapes the analysis output takes: a
    dataset dashboard reads the whole ``intensity_profiles`` table, an image
    dashboard reads the entry for the image it is showing.
    """

    @app.expanded_callback(
        dash.dependencies.Output(CHART_ID, "data"),
        [dash.dependencies.Input(channel_select_id, "value")],
    )
    def update_intensity_profile(channel, *, session_state):
        try:
            context = session_state["context"]
            profiles = deserialize(context["mm_dataset"]).output[
                "intensity_profiles"
            ]
            if per_image:
                profiles = profiles[int(context["image_index"])]
            return intensity_profile_records(
                load.load_table_mm_metrics(profiles), channel
            )
        except Exception:
            return [{"Pixel": 0}]

    # The curve type is a display choice: no part of the profile data depends on
    # it, so the chart is told about it in the browser rather than reloading and
    # reshaping the whole table on the server for every Smooth/Linear click.
    app.clientside_callback(
        "function(curveType) { return curveType; }",
        dash.dependencies.Output(CHART_ID, "curveType"),
        dash.dependencies.Input(CURVE_TYPE_ID, "value"),
    )
