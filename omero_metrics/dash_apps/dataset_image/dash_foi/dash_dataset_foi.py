import dash
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from skimage.exposure import rescale_intensity

import omero_metrics.dash_apps.dataset_image.dash_foi.foi_shared_components as fsc
import omero_metrics.dash_apps.utils.omero_metrics_components as my_components
from omero_metrics.dash_apps.dataset_image import dataset_shared_components as dsc
from omero_metrics.styles import (
    CONTAINER_STYLE,
    CONTENT_PAPER_STYLE,
    GRAPH_STYLE,
    INPUT_BASE_STYLES,
    MANTINE_THEME,
    PLOT_LAYOUT,
)
from omero_metrics.tools.serializers import deserialize

dashboard_name = "omero_dataset_foi"
omero_dataset_foi = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)

omero_dataset_foi.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dsc.notifications_container(),
        dsc.confirm_delete_modal(),
        dsc.dataset_header("Field Illumination", "Dataset Analysis", "FOI Analysis"),
        dmc.Container(
            children=[
                # Main Content
                dmc.Grid(
                    gutter="md",
                    align="stretch",
                    children=[
                        # Left Column - Intensity Map
                        dmc.GridCol(
                            span=6,
                            children=[
                                dmc.Paper(
                                    children=[
                                        dmc.Stack(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.Text(
                                                            "Intensity Map",
                                                            fw=500,
                                                            size="lg",
                                                        ),
                                                        dmc.Select(
                                                            id="channel-dropdown-foi",
                                                            clearable=False,
                                                            allowDeselect=False,
                                                            w="200",
                                                            leftSection=my_components.get_icon(
                                                                icon="material-symbols:layers"
                                                            ),
                                                            rightSection=my_components.get_icon(
                                                                icon="radix-icons:chevron-down"
                                                            ),
                                                            styles=INPUT_BASE_STYLES,
                                                        ),
                                                    ],
                                                    justify="space-between",
                                                ),
                                                dash.dcc.Graph(
                                                    id="intensity-map",
                                                    config={
                                                        "displayModeBar": True,
                                                        "scrollZoom": True,
                                                        "modeBarButtonsToRemove": [
                                                            "lasso2d",
                                                            "select2d",
                                                        ],
                                                    },
                                                    style=GRAPH_STYLE,
                                                ),
                                            ],
                                            gap="md",
                                            justify="space-between",
                                            h="100%",
                                        ),
                                    ],
                                    **CONTENT_PAPER_STYLE,
                                ),
                            ],
                        ),
                        # Right Column - Key Measurements
                        dmc.GridCol(
                            span=6,
                            children=[
                                dsc.dataset_table_paper(),
                            ],
                        ),
                    ],
                ),
                # Hidden element for callbacks
                dsc.blank_input(),
                # Intensity Profiles Section
                fsc.intensity_profile_paper(mt="md"),
            ],
            style=CONTAINER_STYLE,
        ),
    ],
)


# Register shared callbacks
dsc.register_delete_dataset_callback(omero_dataset_foi)
dsc.register_download_datasets_callback(omero_dataset_foi)
dsc.register_update_kkm_table_callback(omero_dataset_foi)
dsc.register_download_table_callback(omero_dataset_foi)


@omero_dataset_foi.expanded_callback(
    dash.dependencies.Output("channel-dropdown-foi", "data"),
    dash.dependencies.Output("channel-dropdown-foi", "value"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_dropdown_menu(_blank_input, *, session_state):
    try:
        channel_names = session_state["context"]["channel_names"]
        return [
            {"label": str(name), "value": str(i)}
            for i, name in enumerate(channel_names)
        ], "0"
    except Exception as e:
        return [{"label": "Error loading channels", "value": "0"}], "0"


@omero_dataset_foi.expanded_callback(
    dash.dependencies.Output("intensity-map", "figure"),
    [
        dash.dependencies.Input("channel-dropdown-foi", "value"),
    ],
)
def update_intensity_map(channel, *, session_state):
    try:
        channel = int(channel)
        images = deserialize(session_state["context"])["image_data"]
        image = images[channel]
        image_channel = image[0, 0, :, :]
        image_channel = rescale_intensity(
            image_channel,
            in_range=(0, image_channel.max()),
            out_range=(0.0, 1.0),
        )
        # Create intensity map
        fig = px.imshow(
            image_channel,
            zmin=0.0,
            zmax=1.0,
            color_continuous_scale="hot",
            labels={"color": "Intensity"},
        )
        fig.update_layout(
            **PLOT_LAYOUT,
            xaxis_title="X Position (pixels)",
            yaxis_title="Y Position (pixels)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            coloraxis_colorbar=dict(
                thickness=15,
                len=0.7,
                title=dict(text="Intensity", side="right"),
                tickfont=dict(size=10),
            ),
        )
        return fig
    except Exception as e:
        fig = px.imshow([[0]])
        fig.add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig


fsc.register_intensity_profile_callbacks(omero_dataset_foi, "channel-dropdown-foi")


def restyle_dataframe(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Improve column names for better readability."""
    value = getattr(df, col).str.replace("_", " ", regex=True).str.title()
    setattr(df, col, value)
    return df


dsc.register_delete_button_loading_callback(omero_dataset_foi)
