import math
from time import sleep

import dash_mantine_components as dmc
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, dependencies, html, no_update
from dash_iconify import DashIconify
from linkml_runtime.dumpers import JSONDumper, YAMLDumper
from scipy.interpolate import griddata
from scipy.spatial import QhullError

from omero_metrics import views
from omero_metrics.dash_apps.utils import omero_metrics_components
from omero_metrics.styles import (
    CONTENT_PAPER_STYLE,
    INPUT_BASE_STYLES,
    TABLE_MANTINE_STYLE,
    THEME,
)
from omero_metrics.tools import load
from omero_metrics.tools.schema_utils import remove_unsupported_types
from omero_metrics.tools.serializers import deserialize

SCALE_BAR_VALUES = [
    500,
    200,
    100,
    50,
    20,
    10,
    5,
    2,
    1,
    0.5,
]


# COMPONENTS
def notifications_container():
    """Renders notifications pushed to its ``sendNotifications`` prop.

    NotificationContainer is both the provider and the target, replacing the
    NotificationProvider/Div pair that DMC 2.8 deprecated.
    """
    return dmc.NotificationContainer(
        id="notifications-container", position="top-center"
    )


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


def dataset_header(title, description, tag, load_buttons=True):
    """Dashboard header with the dataset load/download/delete buttons."""
    return omero_metrics_components.header_component(
        title, description, tag, load_buttons=load_buttons
    )


def image_header(title, description, tag, load_buttons=False):
    return omero_metrics_components.header_component(
        title, description, tag, load_buttons=load_buttons
    )


def blank_input():
    """Hidden element used to trigger callbacks once on page load."""
    return html.Div(id="blank-input")


def _download_table():
    """Download menu for the key measurements table."""
    return dmc.Group(
        [
            dmc.Menu(
                [
                    dmc.MenuTarget(
                        dmc.ActionIcon(
                            DashIconify(icon="material-symbols:download", width=20),
                            color=THEME["primary"],
                        )
                    ),
                    dmc.MenuDropdown(
                        [
                            dmc.MenuItem(
                                "CSV",
                                id="table-download-csv",
                                leftSection=DashIconify(
                                    icon="iwwa:file-csv", width=20
                                ),
                            ),
                            dmc.MenuItem(
                                "Excel",
                                id="table-download-xlsx",
                                leftSection=DashIconify(
                                    icon="vscode-icons:file-type-excel", width=20
                                ),
                            ),
                            dmc.MenuItem(
                                "JSON",
                                id="table-download-json",
                                leftSection=DashIconify(
                                    icon="vscode-icons:file-type-json", width=20
                                ),
                            ),
                        ]
                    ),
                ],
                trigger="click",
            ),
            dcc.Download(id="table-download"),
        ]
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
                                    _download_table(),
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


# The PSF beads and co-registration dashboards are the same dashboard: a
# contour chart of a per-bead measurement. They differ only in their heading
# text and in which input_data field holds the analysed images.
IMAGE_CHART_WIDTH = 600
# Trimmed from the Plotly defaults (l/r 80, t 100, b 80). The default top
# margin holds a title this chart does not have, and its whitespace pushed the
# plotting area well below the top of the controls standing beside it.
IMAGE_CHART_MARGIN = dict(l=45, r=15, t=15, b=45)
# Plotly widens the right margin to fit the colorbar. Allow for it so the
# height below is derived from the width the plotting area actually gets.
IMAGE_COLORBAR_WIDTH = 90


def _apply_image_layout(fig, x_max=None, y_max=None):
    """Give ``fig`` the footprint shared by the image-shaped charts.

    ``x_max``/``y_max`` are the analysed image shape. They are unknown when the
    context failed to load, in which case the figure falls back to a square.

    The axes are pinned to the image bounds rather than autoranged: the bead
    markers would otherwise pad the range past the image, leaving a band of
    plot background around it. ``constrain="domain"`` keeps the pixels square
    by shrinking the plotting area instead of widening that range again.
    """
    aspect_ratio = y_max / x_max if x_max and y_max else 1
    plot_width = (
        IMAGE_CHART_WIDTH
        - IMAGE_CHART_MARGIN["l"]
        - IMAGE_CHART_MARGIN["r"]
        - IMAGE_COLORBAR_WIDTH
    )
    if x_max and y_max:
        axes = dict(
            # px.imshow squares its pixels by anchoring x to y. Clearing that
            # avoids a circular constraint with the y anchor below.
            xaxis=dict(range=[0, x_max], constrain="domain", scaleanchor=None),
            # px.imshow also flips the y axis with autorange, which would take
            # precedence over the explicit range.
            yaxis=dict(
                range=[y_max, 0],
                autorange=False,
                scaleanchor="x",
                constrain="domain",
            ),
        )
    else:
        axes = dict(yaxis=dict(autorange="reversed"))
    fig.update_layout(
        width=IMAGE_CHART_WIDTH,
        # Sizing the plotting area, rather than the whole figure, to the image
        # shape: the margins are fixed, so anything they take is added back.
        height=(
            plot_width * aspect_ratio
            + IMAGE_CHART_MARGIN["t"]
            + IMAGE_CHART_MARGIN["b"]
        ),
        margin=IMAGE_CHART_MARGIN,
        plot_bgcolor=THEME["background"],
        paper_bgcolor=THEME["background"],
        **axes,
    )
    return fig


def empty_image_figure(x_max=None, y_max=None):
    """Figure matching the image chart footprint, ready for traces or messages."""
    return _apply_image_layout(go.Figure(), x_max, y_max)


def image_figure(image, colorscale=None, zmin=None, zmax=None):
    """``image`` rendered in the same footprint as ``empty_image_figure``.

    ``px.imshow`` of a 2D array is a ``go.Heatmap`` bound to the layout
    coloraxis, so the colorbar is configured through ``coloraxis_colorbar``
    rather than on the trace. ``zmin``/``zmax`` default to the image min/max.
    """
    fig = px.imshow(
        image,
        zmin=zmin,
        zmax=zmax,
        color_continuous_scale=colorscale,
    )
    return _apply_image_layout(fig, image.shape[1], image.shape[0])


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


def contour_chart(**group_props):
    """The contour chart beside its controls.

    Extra keyword arguments are passed through to ``dmc.Group``, so a dashboard
    can override the defaults or add its own props. Compose ``contour_chart()``
    and ``contour_controls()`` directly for a different arrangement.
    """
    props = {
        # Not space-around: the chart has a fixed width, so the leftover space
        # in the row became gutters on either side of it.
        "justify": "flex-start",
        "gap": "xl",
        "wrap": "nowrap",
        "align": "flex-start",
        "direction": "row",
        **group_props,
    }
    return dmc.Flex(
        children=[
            dcc.Graph(
                id="contour-chart",
                figure={},
                # The wrapper div is block level and would stretch across the
                # row, leaving the fixed-width figure adrift inside it.
                style={"width": IMAGE_CHART_WIDTH},
            ),
            dmc.Stack(
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
                        w="200",
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
        ],
        **props,
    )


def intensity_chart(**group_props):
    """The intensity chart beside its controls.

    Extra keyword arguments are passed through to ``dmc.Group``, so a dashboard
    can override the defaults or add its own props. Compose ``contour_chart()``
    and ``contour_controls()`` directly for a different arrangement.
    """
    props = {
        # Not space-around: the chart has a fixed width, so the leftover space
        # in the row became gutters on either side of it.
        "justify": "flex-start",
        "gap": "xl",
        "wrap": "nowrap",
        "align": "flex-start",
        "direction": "row",
        **group_props,
    }
    return dmc.Flex(
        children=[
            dcc.Graph(
                id="intensity-chart",
                figure={},
                # The wrapper div is block level and would stretch across the
                # row, leaving the fixed-width figure adrift inside it.
                style={"width": IMAGE_CHART_WIDTH},
            ),
            dmc.Stack(
                children=[
                    dmc.Divider(
                        label="Channel Selection",
                        labelPosition="center",
                    ),
                    dmc.Select(
                        id="intensity-chart-channel-select",
                        label="Channel",
                        w="100%",
                        allowDeselect=False,
                        leftSection=omero_metrics_components.get_icon(
                            "material-symbols:layers"
                        ),
                        rightSection=omero_metrics_components.get_icon(
                            "radix-icons:chevron-down"
                        ),
                    ),
                    dmc.Divider(
                        label="Display Options",
                        labelPosition="center",
                        mt="md",
                    ),
                    dmc.Switch(
                        id="show-info-switch",
                        label="Show bead info on hover",
                        checked=True,
                        size="md",
                        color=THEME["primary"],
                    ),
                    dmc.Stack(
                        [
                            dmc.Switch(
                                id="show-rois-switch",
                                label="Show ROI Boundaries",
                                checked=True,
                                size="md",
                                color=THEME["primary"],
                            ),
                        ],
                        gap="xs",
                    ),
                    dmc.Divider(
                        label="Color Settings",
                        labelPosition="center",
                        mt="md",
                    ),
                    dmc.Select(
                        id="intensity-chart-color-select",
                        label="Color Scheme",
                        allowDeselect=False,
                        data=[
                            {
                                "value": "Hot",
                                "label": "Hot",
                            },
                            {
                                "value": "Blackbody",
                                "label": "Blackbody",
                            },
                            {
                                "value": "Viridis",
                                "label": "Viridis",
                            },
                            {
                                "value": "Inferno",
                                "label": "Inferno",
                            },
                        ],
                        value="Blackbody",
                        leftSection=omero_metrics_components.get_icon(
                            "material-symbols:palette"
                        ),
                        rightSection=omero_metrics_components.get_icon(
                            "radix-icons:chevron-down"
                        ),
                    ),
                    dmc.Switch(
                        id="invert-color-switch",
                        label="Invert Colors",
                        checked=False,
                        size="md",
                        color=THEME["primary"],
                    ),
                ],
                gap="sm",
            ),
        ],
        **props,
    )


# CALLBACKS
def register_delete_dataset_callback(app):

    @app.expanded_callback(
        dependencies.Output("confirm-delete-modal", "opened"),
        dependencies.Output("notifications-container", "sendNotifications"),
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


def register_contour_chart_callbacks(app, images_attr):
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
            x_pixel_size = images[0].voxel_size_x_micron
            image_width_micron = x_max * x_pixel_size

            min_bar_length = 0.05 * image_width_micron
            max_bar_length = 0.20 * image_width_micron
            scale_bar_length = None
            for value in SCALE_BAR_VALUES:
                if min_bar_length <= value <= max_bar_length:
                    scale_bar_length = value
                    break

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

            fig = empty_image_figure(x_max, y_max)
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
            if scale_bar_length is not None:
                fig.add_shape(
                    type="line",
                    x0=50,
                    y0=y_max - 55,
                    x1=50 + (scale_bar_length / x_pixel_size),
                    y1=y_max - 50,
                    line=dict(color="white", width=8),
                )
                fig.add_annotation(
                    x=50 + (scale_bar_length / x_pixel_size) / 2,
                    y=y_max - 140,
                    align="center",
                    text=f"{scale_bar_length} µm",
                    showarrow=False,
                    font=dict(color="white", size=14),
                )

            return fig

        except QhullError:
            return add_centered_message(
                empty_image_figure(x_max, y_max),
                "Not enough data for interpolation",
            )

        except ValueError as e:
            fig = empty_image_figure(x_max, y_max)
            add_centered_message(
                fig, "Probably not a numeric measurement.", y=0.6, size=14
            )
            add_centered_message(fig, str(e), y=0.4, size=14)

            return fig

        except Exception as e:
            return add_centered_message(empty_image_figure(x_max, y_max), str(e))


def register_intensity_chart_callbacks(app, images_attr, hover_info=None):
    """Register the callbacks for the intensity chart.

    ``images_attr`` names the ``input_data`` field holding the analysed images,
    e.g. ``"psf_beads_images"`` or ``"multiwavelength_beads_images"``.
    ``hover_info`` describes the bead hover box. Rows of the beads scatter hover box,
    in display order. Each key is the label shown to the user;
    each value is either a column of the bead properties table or a callable
    taking that table and returning one value per bead.
    """

    @app.expanded_callback(
        dependencies.Output("intensity-chart", "figure"),
        [
            dependencies.Input("intensity-chart-channel-select", "value"),
            dependencies.Input("intensity-chart-color-select", "value"),
            dependencies.Input("invert-color-switch", "checked"),
            dependencies.Input("show-rois-switch", "checked"),
            dependencies.Input("show-info-switch", "checked"),
        ],
    )
    def update_image(
        channel_index,
        color,
        invert_color,
        show_rois,
        show_beads_info,
        *,
        session_state,
    ):
        try:
            context = deserialize(session_state["context"])
            mm_dataset = context["mm_dataset"]
            mm_image = context["mm_image"]
            image_id = mm_image.data_reference.omero_object_id
            channel_index = int(channel_index)
            min_lateral_distance_px = context["min_lateral_distance_px"]
            half_lateral_min_distance_px = min_lateral_distance_px // 2
            bead_properties_df = load.load_table_mm_metrics(
                mm_dataset.output["bead_properties"]
            )
            beads_location_df = bead_properties_df.loc[
                (bead_properties_df["image_id"] == image_id)
                & (bead_properties_df["channel_nr"] == channel_index),
                :,
            ].copy()

            scatter, roi_rect = beads_scatter_plot(
                beads_location_df, half_lateral_min_distance_px, hover_info
            )

            if invert_color:
                color = f"{color}_r"
            mip_z = context["mip_z"][..., channel_index]

            fig = image_figure(mip_z, colorscale=color)

            fig.add_trace(scatter)

            if show_rois:
                fig.update_layout(shapes=roi_rect)
            else:
                fig.update_layout(shapes=None)

            if show_beads_info:
                fig.update_traces(
                    visible=True, selector=dict(name="Beads Locations")
                )
            else:
                fig.update_traces(
                    visible=False, selector=dict(name="Beads Locations")
                )

            fig.update_layout(
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, visible=False),
                coloraxis_colorbar=dict(
                    thickness=15,
                    len=0.7,
                    title=dict(text="Intensity", side="right"),
                    tickfont=dict(size=10),
                ),
            )

            return fig

        except Exception as e:
            return add_centered_message(empty_image_figure(), str(e))

    @app.expanded_callback(
        dependencies.Output("intensity-chart-channel-select", "data"),
        dependencies.Output("intensity-chart-channel-select", "value"),
        [dependencies.Input("blank-input", "children")],
    )
    def update_channels_intensity_chart(_blank_input, *, session_state):
        context = deserialize(session_state["context"])
        channel_series = context["mm_image"].channel_series
        return [
            {"label": c.name, "value": str(i)}
            for i, c in enumerate(channel_series.channels)
        ], "0"


def yes_no(flags):
    """Render a boolean bead property as Yes/No for the hover text.

    hovertemplate has no conditionals, so the mapping has to happen here. The
    object dtype keeps np.stack from casting the numeric customdata columns
    standing next to these to strings. Use it to build hover rows that no
    ``hover_flag`` column covers on its own.
    """
    return np.where(np.asarray(flags, dtype=bool), "Yes", "No").astype(object)


def hover_flag(column, *more_columns):
    """Hover row for bead properties stored as "True"/"False", shown as Yes/No.

    Given several columns the row reads Yes where any of them is set, e.g. a
    gaussian fit that failed on any one axis.
    """
    columns = (column, *more_columns)

    def flag(df):
        flags = [df[col] == "True" for col in columns]
        return yes_no(np.logical_or.reduce(flags))

    return flag


def beads_scatter_plot(df, half_min_distance_px, hover_info=None):
    """Scatter of the bead locations, hover box described by ``hover_info``.

    ``hover_info`` holds the hover rows in display order: each key is the label
    shown to the user, each value is either a column of the bead properties
    table or a callable taking that table and returning one value per bead.
    """
    df["color"] = np.where(df["considered_valid"] == "True", "green", "red")

    if hover_info is not None:
        customdata = np.stack(
            [
                np.asarray(
                    source(df) if callable(source) else df[source], dtype=object
                )
                for source in hover_info.values()
            ],
            axis=-1,
        )
        hovertemplate = (
            "".join(
                f"<b>{label}:</b> %{{customdata[{i}]}}<br>"
                for i, label in enumerate(hover_info)
            )
            + "<extra></extra>"
        )

    else:
        customdata = None
        hovertemplate = None

    beads_location_plot = go.Scatter(
        y=df["center_y"],
        x=df["center_x"],
        mode="markers",
        name="Beads Locations",
        marker=dict(
            size=0.001,
            opacity=0.01,
            color=df["color"],
        ),
        text=df["channel_nr"],
        customdata=customdata,
        hovertemplate=hovertemplate,
    )

    bead_frames = [
        dict(
            type="rect",
            x0=row.center_x - half_min_distance_px,
            y0=row.center_y - half_min_distance_px,
            x1=row.center_x + half_min_distance_px,
            y1=row.center_y + half_min_distance_px,
            xref="x",
            yref="y",
            line=dict(
                color=row["color"],
                width=3,
            ),
        )
        for _, row in df.iterrows()
    ]

    return beads_location_plot, bead_frames
