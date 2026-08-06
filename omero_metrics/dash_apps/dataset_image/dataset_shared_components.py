import math
from time import sleep

import dash_mantine_components as dmc
import numpy as np
import plotly.graph_objects as go
from dash import dcc, dependencies, html, no_update
from linkml_runtime.dumpers import JSONDumper, YAMLDumper
from scipy.interpolate import griddata
from scipy.spatial import QhullError

from omero_metrics import views
from omero_metrics.dash_apps.utils import omero_metrics_components
from omero_metrics.styles import (
    CONTAINER_STYLE,
    CONTENT_PAPER_STYLE,
    INPUT_BASE_STYLES,
    MANTINE_THEME,
    TABLE_MANTINE_STYLE,
    THEME,
)
from omero_metrics.tools import load
from omero_metrics.tools.schema_utils import remove_unsupported_types
from omero_metrics.tools.serializers import deserialize


# COMPONENTS
def notification_provider():
    return dmc.NotificationProvider(position="top-center")


def notifications_container():
    return html.Div(id="notifications-container")


def confirm_delete_modal():
    return dmc.Modal(
        title="Confirm Delete",
        id="confirm-delete-modal",
        children=[
            dmc.Text("Are you sure you want to delete this dataset outputs?"),
            dmc.Space(h=20),
            dmc.Group(
                [
                    dmc.Button(
                        "Delete",
                        id="confirm-delete-button",
                        color="red",
                    ),
                    dmc.Button(
                        "Cancel",
                        id="cancel-delete-button",
                        color="gray",
                        variant="outline",
                    ),
                ],
                justify="flex-end",
            ),
        ],
    )


def dataset_table_paper():
    return dmc.Paper(
        children=[
            dmc.Stack(
                [
                    dmc.Group(
                        [
                            dmc.Text(
                                "Key Measurements",
                                fw=500,
                                size="lg",
                            ),
                            dmc.Group(
                                [
                                    omero_metrics_components.download_table,
                                    dmc.Tooltip(
                                        label="Key measurements for all the channels",
                                        children=[
                                            omero_metrics_components.get_icon(
                                                icon="material-symbols:info",
                                                color=THEME["primary"],
                                            )
                                        ],
                                    ),
                                ]
                            ),
                        ],
                        justify="space-between",
                    ),
                    dmc.ScrollArea(
                        offsetScrollbars=True,
                        children=[
                            dmc.Table(
                                id="kkm-table",
                                striped=True,
                                highlightOnHover=True,
                                withTableBorder=False,
                                withColumnBorders=True,
                                fz="sm",
                                style=TABLE_MANTINE_STYLE,
                            ),
                            dmc.Group(
                                mt="md",
                                children=[
                                    dmc.Pagination(
                                        id="kkm-table-pagination",
                                        total=0,
                                        value=1,
                                        withEdges=True,
                                    )
                                ],
                                justify="center",
                            ),
                        ],
                    ),
                ],
                gap="md",
                justify="space-between",
                h="100%",
            ),
        ],
        **CONTENT_PAPER_STYLE,
    )


# CONTOUR CHART DASHBOARD
# The PSF beads and co-registration dashboards are the same dashboard: a
# contour chart of a per-bead measurement. They differ only in their heading
# text and in which input_data field holds the analysed images.
CONTOUR_CHART_WIDTH = 600


def empty_contour_figure(x_max=None, y_max=None):
    """Figure matching the contour chart footprint, ready for traces or messages.

    ``x_max``/``y_max`` are the analysed image shape. They are unknown when the
    context failed to load, in which case the figure falls back to a square.
    """
    aspect_ratio = y_max / x_max if x_max and y_max else 1
    fig = go.Figure()
    fig.update_layout(
        width=CONTOUR_CHART_WIDTH,
        height=CONTOUR_CHART_WIDTH * aspect_ratio,
        yaxis=dict(autorange="reversed"),
    )
    return fig


def add_centered_message(fig, text, y=0.5, size=20):
    """Overlay a message on the middle of ``fig``, in paper coordinates."""
    fig.add_annotation(
        x=0.5,
        y=y,
        xref="paper",
        yref="paper",
        text=text,
        showarrow=False,
        font=dict(size=size),
    )
    return fig


def _contour_controls():
    """Channel, measurement and precision selectors beside the contour chart."""
    return dmc.Stack(
        children=[
            dmc.Select(
                id="channel-select",
                clearable=False,
                allowDeselect=False,
                w="200",
                leftSection=omero_metrics_components.get_icon(
                    icon="material-symbols:layers"
                ),
                rightSection=omero_metrics_components.get_icon(
                    icon="radix-icons:chevron-down"
                ),
                styles=INPUT_BASE_STYLES,
            ),
            dmc.Select(
                id="measurement-select",
                clearable=False,
                allowDeselect=False,
                w="200",
                leftSection=omero_metrics_components.get_icon(
                    icon="ph:magnifying-glass"
                ),
                rightSection=omero_metrics_components.get_icon(
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
    )


def contour_dashboard_layout(title, description, tag):
    """Full layout for a dataset dashboard built around a contour chart."""
    return dmc.MantineProvider(
        theme=MANTINE_THEME,
        children=[
            notifications_container(),
            confirm_delete_modal(),
            omero_metrics_components.header_component(title, description, tag),
            dmc.Container(
                children=[
                    # Hidden element for callbacks
                    html.Div(id="blank-input"),
                    dmc.Group(
                        children=[
                            dcc.Graph(id="contour-chart", figure={}),
                            _contour_controls(),
                        ],
                        # Group wraps by default; the chart (600px) plus the
                        # controls (200px) overflow the panel and would stack.
                        wrap="nowrap",
                        align="flex-start",
                    ),
                    dataset_table_paper(),
                ],
                style=CONTAINER_STYLE,
            ),
        ],
    )


# CALLBACKS
def register_delete_dataset_callback(app):
    @app.expanded_callback(
        dependencies.Output("confirm-delete-modal", "opened"),
        dependencies.Output("notifications-container", "children"),
        dependencies.Output("confirm-delete-button", "loading"),
        [
            dependencies.Input("delete-data", "n_clicks"),
            dependencies.Input("confirm-delete-button", "n_clicks"),
            dependencies.Input("cancel-delete-button", "n_clicks"),
            dependencies.State("confirm-delete-modal", "opened"),
        ],
        prevent_initial_call=True,
    )
    def delete_dataset_callback(
        delete_data_clicks,
        confirm_delete_button_clicks,
        cancel_delete_button_clicks,
        confirm_delete_modal_opened,
        *,
        callback_context,
        session_state,
        request,
    ):
        triggered_button = callback_context.triggered[0]["prop_id"]
        context = deserialize(session_state["context"])
        dataset_id = context["mm_dataset"].data_reference.omero_object_id
        opened = not confirm_delete_modal_opened
        if (
            triggered_button == "confirm-delete-button.n_clicks"
            and delete_data_clicks > 0
        ):
            sleep(1)
            response_type, response_msg = views.delete_dataset(
                request, dataset_id=dataset_id
            )

            return omero_metrics_components.notification_handler(
                response_type, response_msg, opened
            )
        else:
            return opened, None, False


def register_download_datasets_callback(app):
    @app.expanded_callback(
        dependencies.Output("download", "data"),
        [
            dependencies.Input("download-yaml", "n_clicks"),
            dependencies.Input("download-json", "n_clicks"),
            dependencies.Input("download-text", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def download_dataset_callback(
        dl_yaml_n_clicks,
        dl_json_n_clicks,
        dl_text_n_clicks,
        *,
        callback_context,
        session_state,
    ):
        if not callback_context.triggered:
            raise no_update

        triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
        context = deserialize(session_state["context"])
        mm_dataset = context["mm_dataset"]
        remove_unsupported_types(mm_dataset.input_data)
        remove_unsupported_types(mm_dataset.output)
        remove_unsupported_types(mm_dataset.input_parameters)
        file_name = mm_dataset.name
        yaml_dumper = YAMLDumper()
        json_dumper = JSONDumper()
        if triggered_id == "download-yaml":
            return dict(
                content=yaml_dumper.dumps(mm_dataset), filename=f"{file_name}.yaml"
            )

        elif triggered_id == "download-json":
            return dict(
                content=json_dumper.dumps(mm_dataset), filename=f"{file_name}.json"
            )

        elif triggered_id == "download-text":
            return dict(
                content=yaml_dumper.dumps(mm_dataset), filename=f"{file_name}.txt"
            )

        raise no_update


def register_update_kkm_table_callback(app):
    @app.expanded_callback(
        dependencies.Output("kkm-table", "data"),
        dependencies.Output("kkm-table-pagination", "total"),
        [
            dependencies.Input("kkm-table-pagination", "value"),
        ],
    )
    def update_kkm_table_callback(pagination_value, *, session_state):
        try:
            page = int(pagination_value)
            context = deserialize(session_state["context"])
            kkm = context["assay_config"].kkm_configuration
            kkm_values = [k.value for k in kkm]
            col_rename = {"channel_name": "Channel Name"} | {
                k.value: k.display_name for k in kkm
            }
            # TODO: review how we process the tables here.
            table_km = load.get_km_mm_metrics_dataset(
                mm_dataset=context["mm_dataset"]
            )
            start_idx = (page - 1) * 4
            end_idx = start_idx + 4
            metrics_df = table_km.filter(["channel_name", *kkm_values])
            metrics_df = metrics_df.round(3)
            metrics_df = metrics_df.rename(columns=col_rename)
            page_data = metrics_df.iloc[start_idx:end_idx]
            return {
                "head": page_data.columns.tolist(),
                "body": page_data.values.tolist(),
                "caption": "Statistical measurements across channels",
            }, math.ceil(len(metrics_df) / 4)
        except Exception as e:
            return {
                "head": ["Error"],
                "body": [[str(e)]],
                "caption": "Error loading measurements",
            }, 1


def register_download_table_callback(app):
    @app.expanded_callback(
        dependencies.Output("table-download", "data"),
        [
            dependencies.Input("table-download-csv", "n_clicks"),
            dependencies.Input("table-download-xlsx", "n_clicks"),
            dependencies.Input("table-download-json", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def download_table_callback(
        tb_dw_csv_clicks,
        tb_dw_xlsx_clicks,
        tb_dw_json_clicks,
        *,
        callback_context,
        session_state,
    ):
        if not callback_context.triggered:
            raise no_update

        triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
        context = deserialize(session_state["context"])
        kkm = context["assay_config"].kkm_configuration
        kkm_values = [k.value for k in kkm]
        col_rename = {"channel_name": "Channel Name"} | {
            k.value: k.display_name for k in kkm
        }
        table_km = load.get_km_mm_metrics_dataset(mm_dataset=context["mm_dataset"])
        table_kkm = table_km.filter(["channel_name", *kkm_values])
        table_kkm = table_kkm.round(3)
        table_kkm = table_kkm.rename(columns=col_rename)
        if triggered_id == "table-download-csv":
            return dcc.send_data_frame(table_kkm.to_csv, "km_table.csv")
        elif triggered_id == "table-download-xlsx":
            return dcc.send_data_frame(table_kkm.to_excel, "km_table.xlsx")
        elif triggered_id == "table-download-json":
            return dcc.send_data_frame(table_kkm.to_json, "km_table.json")

        raise no_update


def register_delete_button_loading_callback(app):
    """Show a loading state on the delete-confirmation button once clicked."""
    app.clientside_callback(
        """
        function(n_clicks) {
            if (n_clicks > 0) {
                return true;
            }
            return false;
        }
        """,
        dependencies.Output(
            "confirm-delete-button", "loading", allow_duplicate=True
        ),
        dependencies.Input("confirm-delete-button", "n_clicks"),
        prevent_initial_call=True,
    )


def register_contour_callbacks(app, images_attr):
    """Register the selectors and the contour chart for a contour dashboard.

    ``images_attr`` names the ``input_data`` field holding the analysed images,
    e.g. ``"psf_beads_images"`` or ``"multiwavelength_beads_images"``.
    """

    @app.expanded_callback(
        dependencies.Output("channel-select", "data"),
        dependencies.Output("channel-select", "value"),
        dependencies.Output("measurement-select", "data"),
        dependencies.Output("measurement-select", "value"),
        [dependencies.Input("blank-input", "children")],
    )
    def update_dropdown_menus(_blank_input, *, session_state):
        try:
            context = deserialize(session_state["context"])
            return (
                [
                    {"label": str(name), "value": str(i)}
                    for i, name in enumerate(context["channel_names"])
                ],
                "0",
                [
                    {"label": c, "value": c}
                    for c in context["bead_properties"].keys()
                ],
                None,
            )
        except Exception:
            return (
                [{"label": "Error loading channels", "value": "0"}],
                "0",
                [],
                None,
            )

    @app.expanded_callback(
        dependencies.Output("contour-chart", "figure"),
        [
            dependencies.Input("channel-select", "value"),
            dependencies.Input("measurement-select", "value"),
            dependencies.Input("precision-slider", "value"),
        ],
    )
    def update_contour_chart(
        channel_value, measurement_value, precision_value, *, session_state
    ):
        if measurement_value is None:
            return no_update
        # Defined up front so the error handlers below can size their figure
        # even when loading the context is what failed.
        x_max = y_max = None
        try:
            context = deserialize(session_state["context"])
            images = getattr(context["mm_dataset"].input_data, images_attr)
            x_max = images[0].shape_x
            y_max = images[0].shape_y
            xi = np.linspace(0, x_max, 128)
            yi = np.linspace(0, y_max, 128)
            XI, YI = np.meshgrid(xi, yi)
            channel_name = context["channel_names"][int(channel_value)]
            bead_properties = context["bead_properties"]

            def valid_bead(i):
                return (
                    bead_properties["considered_valid"][i] == "True"
                    and bead_properties["channel_name"][i] == channel_name
                )

            indices = [
                i for i in range(len(bead_properties["center_x"])) if valid_bead(i)
            ]
            x = [float(bead_properties["center_x"][i]) for i in indices]
            y = [float(bead_properties["center_y"][i]) for i in indices]
            values = [
                round(float(bead_properties[measurement_value][i]), precision_value)
                for i in indices
            ]

            ZI = griddata(
                points=(x, y),
                values=values,
                xi=(XI, YI),
                method="cubic",
            )

            fig = empty_contour_figure(x_max, y_max)
            fig.add_trace(
                go.Contour(
                    x=xi,
                    y=yi,
                    z=ZI,
                    connectgaps=True,
                    contours=dict(
                        showlabels=True, labelformat=f".{precision_value}f"
                    ),
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

            return fig

        except QhullError:
            return add_centered_message(
                empty_contour_figure(x_max, y_max),
                "Not enough data for interpolation",
            )

        except ValueError as e:
            fig = empty_contour_figure(x_max, y_max)
            add_centered_message(
                fig, "Probably not a numeric measurement.", y=0.6, size=14
            )
            add_centered_message(fig, str(e), y=0.4, size=14)

            return fig

        except Exception as e:
            return add_centered_message(empty_contour_figure(x_max, y_max), str(e))
