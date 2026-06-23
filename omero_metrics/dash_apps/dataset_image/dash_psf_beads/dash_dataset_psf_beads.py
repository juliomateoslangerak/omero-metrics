import dash
import dash_mantine_components as dmc
import numpy as np
import plotly.graph_objects as go
from django_plotly_dash import DjangoDash
from scipy.interpolate import griddata
from scipy.spatial import QhullError

import omero_metrics.dash_apps.utils.omero_metrics_components as my_components
from omero_metrics.dash_apps.dataset_image import dataset_shared_components as dsc
from omero_metrics.styles import CONTAINER_STYLE, INPUT_BASE_STYLES, MANTINE_THEME
from omero_metrics.tools.serializers import deserialize

dashboard_name = "omero_dataset_psf_beads"

omero_dataset_psf_beads = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)


omero_dataset_psf_beads.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dsc.notification_provider(),
        dsc.notifications_container(),
        dsc.confirm_delete_modal(),
        my_components.header_component(
            "PSF Beads", "PSF Beads Analysis Dashboard", "PSF Beads Analysis"
        ),
        dmc.Container(
            children=[
                # Hidden element for callbacks
                dash.html.Div(id="blank-input"),
                dmc.Group(
                    children=[
                        dash.dcc.Graph(id="contour-chart", figure={}),
                        dmc.Stack(
                            children=[
                                dmc.Select(
                                    id="channel-select",
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
                                dmc.Select(
                                    id="measurement-select",
                                    clearable=False,
                                    allowDeselect=False,
                                    w="200",
                                    leftSection=my_components.get_icon(
                                        icon="ph:magnifying-glass"
                                    ),
                                    rightSection=my_components.get_icon(
                                        icon="radix-icons:chevron-down"
                                    ),
                                    styles=INPUT_BASE_STYLES,
                                ),
                                dmc.Text("Select precision"),
                                dmc.Slider(
                                    id="precision-slider",
                                    min=0,
                                    max=10,
                                    step=1,
                                    value=2,
                                    marks=[
                                        {"value": 0, "label": "0"},
                                        {"value": 5, "label": "5"},
                                        {"value": 10, "label": "10"},
                                    ],
                                ),
                            ]
                        ),
                    ]
                ),
                dsc.dataset_table_paper(),
            ],
            style=CONTAINER_STYLE,
        ),
    ],
)


# Register shared callbacks
dsc.register_delete_dataset_callback(omero_dataset_psf_beads)
dsc.register_download_datasets_callback(omero_dataset_psf_beads)
dsc.register_update_kkm_table_callback(omero_dataset_psf_beads)
dsc.register_download_table_callback(omero_dataset_psf_beads)


@omero_dataset_psf_beads.expanded_callback(
    dash.dependencies.Output("channel-select", "data"),
    dash.dependencies.Output("channel-select", "value"),
    dash.dependencies.Output("measurement-select", "data"),
    dash.dependencies.Output("measurement-select", "value"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_dropdown_menus(*args, **kwargs):
    try:
        context = deserialize(kwargs["session_state"]["context"])
        return (
            [
                {"label": str(name), "value": str(i)}
                for i, name in enumerate(context["channel_names"])
            ],
            "0",
            [{"label": c, "value": c} for c in context["bead_properties"].keys()],
            None,
        )
    except Exception as e:
        return [{"label": "Error loading channels", "value": "0"}], "0"


@omero_dataset_psf_beads.expanded_callback(
    dash.dependencies.Output("contour-chart", "figure"),
    [
        dash.dependencies.Input("channel-select", "value"),
        dash.dependencies.Input("measurement-select", "value"),
        dash.dependencies.Input("precision-slider", "value"),
    ],
)
def update_contour_chart(
    channel_value, measurement_value, precision_value, **kwargs
):
    if measurement_value is None:
        return dash.no_update
    try:
        context = deserialize(kwargs["session_state"]["context"])
        x_max = context["mm_dataset"].input_data.psf_beads_images[0].shape_x
        y_max = context["mm_dataset"].input_data.psf_beads_images[0].shape_y
        xi = np.linspace(0, x_max, 128)
        yi = np.linspace(0, y_max, 128)
        XI, YI = np.meshgrid(xi, yi)
        channel_name = context["channel_names"][int(channel_value)]
        x = [
            float(context["bead_properties"]["center_x"][i])
            for i in range(len(context["bead_properties"]["center_x"]))
            if context["bead_properties"]["considered_valid"][i] == "True"
            and context["bead_properties"]["channel_name"][i] == channel_name
        ]
        y = [
            float(context["bead_properties"]["center_y"][i])
            for i in range(len(context["bead_properties"]["center_y"]))
            if context["bead_properties"]["considered_valid"][i] == "True"
            and context["bead_properties"]["channel_name"][i] == channel_name
        ]
        values = [
            round(
                float(context["bead_properties"][measurement_value][i]),
                precision_value,
            )
            for i in range(len(context["bead_properties"]["center_y"]))
            if context["bead_properties"]["considered_valid"][i] == "True"
            and context["bead_properties"]["channel_name"][i] == channel_name
        ]

        ZI = griddata(
            points=(x, y),
            values=values,
            xi=(XI, YI),
            method="cubic",
        )

        fig = go.Figure()
        fig.add_trace(
            go.Contour(
                x=xi,
                y=yi,
                z=ZI,
                connectgaps=True,
                contours=dict(showlabels=True, labelformat=f".{precision_value}f"),
                colorbar=dict(tickformat=f".{precision_value}f"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                marker=dict(size=6, color="black", symbol="circle"),
                name="Measurements",
            )
        )
        fig.update_layout(
            width=600, height=600 * y_max / x_max, yaxis=dict(autorange="reversed")
        )

        return fig

    except QhullError as e:
        fig = go.Figure()
        fig.update_layout(
            width=600, height=600 * y_max / x_max, yaxis=dict(autorange="reversed")
        )
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            text="Not enough data for interpolation",
            showarrow=False,
            font=dict(size=20),
        )

        return fig

    except ValueError as e:
        fig = go.Figure()
        fig.update_layout(
            width=600, height=600 * y_max / x_max, yaxis=dict(autorange="reversed")
        )
        fig.add_annotation(
            x=0.5,
            y=0.6,
            xref="paper",
            yref="paper",
            text="Probably not a numeric measurement.",
            showarrow=False,
            font=dict(size=14),
        )
        fig.add_annotation(
            x=0.5,
            y=0.4,
            xref="paper",
            yref="paper",
            text=str(e),
            showarrow=False,
            font=dict(size=14),
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.update_layout(
            width=600, height=600 * y_max / x_max, yaxis=dict(autorange="reversed")
        )
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            text=str(e),
            showarrow=False,
            font=dict(size=20),
        )

        return fig


omero_dataset_psf_beads.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            return true;
        }
        return false;
    }
    """,
    dash.dependencies.Output(
        "confirm-delete-button", "loading", allow_duplicate=True
    ),
    dash.dependencies.Input("confirm-delete-button", "n_clicks"),
    prevent_initial_call=True,
)
