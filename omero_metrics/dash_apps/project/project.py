import math
import traceback
from time import sleep

import dash
import dash_mantine_components as dmc
import plotly.graph_objects as go
from django_plotly_dash import DjangoDash
from linkml_runtime.dumpers import JSONDumper, YAMLDumper
from microscopemetrics_schema import datamodel as mm_schema

import omero_metrics.dash_apps.utils.omero_metrics_components as my_components
from omero_metrics import views
from omero_metrics.dash_apps.utils import dash_forms_tools as dft
from omero_metrics.styles import (
    BUTTON_STYLE,
    CARD_STYLE1,
    COLORS_CHANNELS,
    CONTAINER_STYLE,
    DATEPICKER_STYLES,
    MANTINE_THEME,
    SELECT_STYLES,
    TAB_ITEM_STYLE,
    TAB_STYLES,
    TABLE_MANTINE_STYLE,
    THEME,
)
from omero_metrics.tools.serializers import deserialize

# Initialize the Dash app
dashboard_name = "omero_project_dash"
omero_project_dash = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)


# Define the layout
omero_project_dash.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dmc.NotificationProvider(position="top-center"),
        dash.html.Div(id="delete-notifications-container"),
        dmc.Modal(
            title="Confirm Delete",
            id="delete-confirm-delete",
            children=[
                dmc.Text("Are you sure you want to delete this project outputs?"),
                dmc.Space(h=20),
                dmc.Group(
                    [
                        dmc.Button(
                            "Submit",
                            id="delete-modal-submit-button",
                            color="red",
                        ),
                        dmc.Button(
                            "Close",
                            color="gray",
                            variant="outline",
                            id="delete-modal-close-button",
                        ),
                    ],
                    justify="flex-end",
                ),
            ],
        ),
        dash.html.Div(id="blank-input"),
        dash.html.Div(id="save-config-result"),
        my_components.header_component(
            "Project Dashboard",
            "Microscopy Image Analysis Dashboard",
            "Project Analysis",
        ),
        dmc.Tabs(
            value="dashboard",
            styles=TAB_STYLES,
            children=[
                dmc.TabsList(
                    children=[
                        dmc.TabsTab(
                            "Dashboard",
                            value="dashboard",
                            leftSection=my_components.get_icon(
                                icon="ph:chart-line-bold"
                            ),
                            color=THEME["primary"],
                            style=TAB_ITEM_STYLE,
                        ),
                        dmc.TabsTab(
                            "Settings",
                            value="settings",
                            leftSection=my_components.get_icon(icon="ph:gear-bold"),
                            color=THEME["primary"],
                            style=TAB_ITEM_STYLE,
                        ),
                        dmc.TabsTab(
                            "Thresholds",
                            value="thresholds",
                            leftSection=my_components.get_icon(icon="ph:ruler-bold"),
                            color=THEME["primary"],
                            style=TAB_ITEM_STYLE,
                        ),
                    ],
                    grow=True,
                    justify="space-around",
                    variant="light",
                    style={"backgroundColor": THEME["surface"]},
                ),
                # Dashboard Panel
                dmc.TabsPanel(
                    value="dashboard",
                    children=dmc.Container(
                        children=[
                            # Chart Section
                            dmc.Paper(
                                style={**CARD_STYLE1, "marginTop": "12px"},
                                children=[
                                    dmc.Title(
                                        "Measurement Trends",
                                        order=3,
                                        style={
                                            "marginBottom": "12px",
                                        },
                                    ),
                                    dmc.Grid(
                                        children=[
                                            dmc.GridCol(
                                                span=6,
                                                children=[
                                                    dmc.Select(
                                                        id="key-measurement-dropdown",
                                                        label="Select Measurement",
                                                        placeholder="Choose a measurement",
                                                        leftSection=my_components.get_icon(
                                                            icon="ph:magnifying-glass"
                                                        ),
                                                        disabled=True,
                                                        rightSection=my_components.get_icon(
                                                            icon="ph:caret-down"
                                                        ),
                                                        allowDeselect=False,
                                                        styles=SELECT_STYLES,
                                                    ),
                                                ],
                                            ),
                                            dmc.GridCol(
                                                span=6,
                                                children=[
                                                    dmc.DatePickerInput(
                                                        id="date-picker",
                                                        label="Date Range",
                                                        type="range",
                                                        valueFormat="DD-MM-YYYY",
                                                        placeholder="Select date range",
                                                        leftSection=my_components.get_icon(
                                                            icon="ph:calendar"
                                                        ),
                                                        miw=150,
                                                        disabled=True,
                                                        styles=DATEPICKER_STYLES,
                                                    ),
                                                ],
                                            ),
                                        ],
                                        align="flex-end",
                                        style={
                                            "marginBottom": "12px",
                                        },
                                    ),
                                    dash.html.Div(
                                        id="graph-project",
                                        style={"height": "350px"},
                                        children=[
                                            dash.dcc.Graph(
                                                id="line-chart", figure={}
                                            ),
                                            dash.html.Div(id="feedback_message"),
                                        ],
                                    ),
                                ],
                            ),
                            # Data Table Section
                            dmc.Paper(
                                id="clicked_data_paper",
                                hiddenFrom={"visible": False, "display": None},
                                style={**CARD_STYLE1, "marginTop": "12px"},
                                children=[
                                    dmc.Text(
                                        id="text-km",
                                        c="#189A35",
                                        mt=10,
                                        ml=10,
                                        mr=10,
                                        fw="bold",
                                    ),
                                    dmc.ScrollArea(
                                        [
                                            dmc.Table(
                                                id="kkm-table",
                                                striped=True,
                                                data={},  # data will be updated by the callback
                                                highlightOnHover=True,
                                                style=TABLE_MANTINE_STYLE,
                                            ),
                                            dmc.Group(
                                                mt="md",
                                                children=[
                                                    dmc.Pagination(
                                                        id="pagination",
                                                        total=0,
                                                        value=1,
                                                        withEdges=True,
                                                    )
                                                ],
                                                justify="center",
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ],
                        fluid=True,
                        style=CONTAINER_STYLE,
                    ),
                ),
                # Settings Panel
                dmc.TabsPanel(
                    value="settings",
                    children=dmc.Container(
                        children=[
                            dmc.LoadingOverlay(
                                id="loading-overlay",
                                overlayProps={
                                    "radius": "sm",
                                    "blur": 1,
                                },
                            ),
                            dmc.Paper(
                                style={**CARD_STYLE1, "marginTop": "12px"},
                                children=[
                                    dmc.Grid(
                                        children=[
                                            dmc.GridCol(
                                                id="input-parameters-container",
                                                span="6",
                                            ),
                                            dmc.GridCol(
                                                id="sample-container",
                                                span="6",
                                            ),
                                        ],
                                        justify="space-between",
                                    ),
                                    dmc.Group(
                                        justify="flex-end",
                                        mt="xl",
                                        children=[
                                            dmc.Button(
                                                "Update",
                                                id="submit-config",
                                                style=BUTTON_STYLE,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                        fluid=True,
                        style=CONTAINER_STYLE,
                    ),
                ),
                # Thresholds Panel
                dmc.TabsPanel(
                    value="thresholds",
                    children=dmc.Container(
                        children=[
                            dmc.LoadingOverlay(
                                id="loading-overlay-threshold",
                                overlayProps={
                                    "radius": "sm",
                                    "blur": 1,
                                },
                            ),
                            dmc.Paper(
                                style={**CARD_STYLE1, "marginTop": "12px"},
                                children=[
                                    dmc.Accordion(
                                        id="accordion-compose-controls",
                                        chevron=my_components.get_icon(
                                            icon="ant-design:plus-outlined"
                                        ),
                                        disableChevronRotation=True,
                                        children=[],
                                    ),
                                    dmc.Group(
                                        justify="flex-end",
                                        mt="xl",
                                        id="thresholds-button-container",
                                        children=[],
                                    ),
                                    dash.html.Div(id="notifications-container"),
                                ],
                            ),
                        ],
                        fluid=True,
                        style=CONTAINER_STYLE,
                    ),
                ),
            ],
        ),
    ],
)


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("key-measurement-dropdown", "data"),
    dash.dependencies.Output("key-measurement-dropdown", "value"),
    dash.dependencies.Output("date-picker", "minDate"),
    dash.dependencies.Output("date-picker", "maxDate"),
    dash.dependencies.Output("date-picker", "value"),
    dash.dependencies.Output("date-picker", "disabled"),
    dash.dependencies.Output("key-measurement-dropdown", "disabled"),
    dash.dependencies.Output("activate-download", "disabled"),
    dash.dependencies.Output("delete-data", "disabled"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_dropdown(*args, **kwargs):
    try:
        context = deserialize(kwargs["session_state"]["context"])
        kkm_config = context["assay_config"].kkm_configuration
        kkm_options = [
            {"value": str(i), "label": k.display_name}
            for i, k in enumerate(kkm_config)
        ]

        # Parse datetime strings and get min/max
        datetimes = context["dates"]
        min_date = context["min_date"]
        max_date = context["max_date"]

        value_date = [min_date, max_date]
        return (
            kkm_options,
            "0",
            min_date,
            max_date,
            value_date,
            False,
            False,
            False,
            False,
        )
    except Exception as e:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            True,
            True,
            True,
            True,
        )


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("graph-project", "children"),
    [dash.dependencies.Input("blank-input", "children")],
)
def check_data(*args, **kwargs):
    try:
        data = deserialize(kwargs["session_state"]["context"])[
            "key_measurements_by_kkm"
        ]
        # FIXME: This expression is odd in any case this returns no update
        if not data:
            return dash.no_update
        return dash.no_update
    except Exception as e:
        return [
            dmc.Stack(
                children=[
                    dmc.Text(
                        "No data available for this project",
                        size="lg",
                        fw=500,
                        c="dimmed",
                    ),
                    dmc.Space(h=100),  # Add some vertical spacing
                ],
                align="center",
                justify="center",
                style={"height": "250px"},
            )
        ]


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("line-chart", "figure"),
    [
        dash.dependencies.Input("key-measurement-dropdown", "value"),
        dash.dependencies.Input("date-picker", "value"),
    ],
    prevent_initial_call=True,
)
def update_table(measurement, dates_range, **kwargs):
    try:
        context = deserialize(kwargs["session_state"]["context"])
        key_measurements_by_kkm = context["key_measurements_by_kkm"]
        comments_by_dataset_id = context["comments_by_dataset_id"]
        threshold = context["thresholds"]
        kkm_config = context["assay_config"].kkm_configuration
        measurement = int(measurement)

        # Check if we have any data
        if not key_measurements_by_kkm:
            return dash.no_update
        selected_kkm = kkm_config[measurement]

        dates_range = [d.split("T")[0] for d in dates_range]

        fig = go.Figure()

        data = key_measurements_by_kkm[selected_kkm.value]
        keys = sorted(
            {
                k
                for m in data
                for k in m
                if k not in ["date", "dataset_id"] and not k.endswith("_err")
            }
        )
        for i, k in enumerate(keys):
            fig.add_trace(
                go.Scatter(
                    x=[
                        m["date"]
                        for m in data
                        if dates_range[0] <= m["date"] <= dates_range[1]
                    ],
                    y=[
                        m[k]
                        for m in data
                        if dates_range[0] <= m["date"] <= dates_range[1]
                    ],
                    error_y={
                        "array": [
                            m.get(f"{k}_err")
                            for m in data
                            if dates_range[0] <= m["date"] <= dates_range[1]
                        ]
                    },
                    customdata=[
                        m["dataset_id"]
                        for m in data
                        if dates_range[0] <= m["date"] < dates_range[1]
                    ],
                    mode="lines+markers",
                    name=k,
                )
            )

        for id, comment in comments_by_dataset_id.items():
            if comment:
                # fig.add_trace(
                #     go.Scatter(
                #         x=[comment["datetime"], comment["datetime"]],
                #         # y=[ymin, ymax],
                #         mode="lines",
                #         customdata=comment["text"],
                #         hovertemplate="%{customdata}<extra></extra>",
                #         showlegend=False,
                #     )
                # )
                fig.add_shape(
                    type="line",
                    x0=comment["datetime"],
                    x1=comment["datetime"],
                    y0=0,
                    y1=1,
                    yref="paper",
                    line=dict(color="blue", dash="dash"),
                )

        if threshold:
            threshold_kkm = threshold[selected_kkm.value]
            fig.add_hline(
                y=threshold_kkm["upper_limit"],
                line={"color": "red", "dash": "dash"},
                name="Upper threshold",
            )
            fig.add_hline(
                y=threshold_kkm["lower_limit"],
                line={"color": "orangered", "dash": "dot"},
                name="Lower threshold",
            )

        return fig

    except Exception as e:
        return dash.no_update


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("text-km", "children"),
    dash.dependencies.Output("kkm-table", "data"),
    dash.dependencies.Output("pagination", "total"),
    dash.dependencies.Output("clicked_data_paper", "hiddenFrom"),
    [
        dash.dependencies.Input("line-chart", "clickData"),
        dash.dependencies.Input("pagination", "value"),
    ],
)
def update_project_view(clicked_data, page, **kwargs):
    try:
        if clicked_data:
            context = deserialize(kwargs["session_state"]["context"])
            key_measurements_by_dataset_id = context[
                "key_measurements_by_dataset_id"
            ]
            data = key_measurements_by_dataset_id[
                str(clicked_data["points"][0]["customdata"])
            ]
            total = math.ceil(len(data["head"]) / 4)
            start_idx = (page - 1) * 4
            end_idx = start_idx + 4
            page_data = {
                "caption": data["caption"],
                "head": data["head"][start_idx:end_idx],
                "body": [i[start_idx:end_idx] for i in data["body"]],
            }
            return (
                data["caption"],
                page_data,
                total,
                {"visible": True},
            )

        else:
            return dash.no_update
    except Exception as e:
        return dash.no_update


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("input-parameters-container", "children"),
    dash.dependencies.Output("sample-container", "children"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_modal(*args, **kwargs):
    context = deserialize(kwargs["session_state"]["context"])
    sample = context["sample"]
    mm_sample = getattr(mm_schema, sample["type"])
    mm_sample = mm_sample(**sample["fields"])
    sample_form = dft.get_form(mm_sample, disabled=False, form_id="sample_form")
    input_parameters = context["input_parameters"]
    mm_input_parameters = getattr(mm_schema, input_parameters["type"])
    mm_input_parameters = mm_input_parameters(**input_parameters["fields"])
    input_parameters_form = dft.get_form(
        mm_input_parameters, disabled=False, form_id="input_parameters_form"
    )

    return (
        input_parameters_form,
        sample_form,
    )


omero_project_dash.clientside_callback(
    """
    function updateLoadingState(n_clicks) {
        if (n_clicks > 0 ) {
            return true;
        }
        return false;
    }


    """,
    dash.dependencies.Output("loading-overlay", "visible", allow_duplicate=True),
    dash.dependencies.Input("submit-config", "n_clicks"),
    prevent_initial_call=True,
)
omero_project_dash.clientside_callback(
    """
    function updateLoadingThresholdState(n_clicks) {
        if (n_clicks > 0) {
            return true;
        }
        return false;
    }


    """,
    dash.dependencies.Output(
        "loading-overlay-threshold", "visible", allow_duplicate=True
    ),
    dash.dependencies.Input("modal-submit-button", "n_clicks"),
    prevent_initial_call=True,
)


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("save-config-result", "children"),
    dash.dependencies.Output("loading-overlay", "visible"),
    [
        dash.dependencies.Input("submit-config", "n_clicks"),
        dash.dependencies.State("sample_form", "children"),
        dash.dependencies.State("input_parameters_form", "children"),
    ],
    prevent_initial_call=True,
)
def update_config_project(submit_click, sample_form, input_form, **kwargs):
    context = deserialize(kwargs["session_state"]["context"])
    project_id = int(context["project_id"])
    request = kwargs["request"]
    sample = context["sample"]
    mm_sample = getattr(mm_schema, sample["type"])
    input_parameters = context["input_parameters"]
    mm_input_parameters = getattr(mm_schema, input_parameters["type"])
    if dft.validate_form(sample_form) and dft.validate_form(input_form):
        try:
            input_parameters = dft.extract_form_data(input_form)
            mm_input_parameters = mm_input_parameters(**input_parameters)
            sample = dft.extract_form_data(sample_form)
            mm_sample = mm_sample(**sample)
            response_type, response_msg = views.save_config(
                request=request,
                project_id=project_id,
                input_parameters=mm_input_parameters,
                sample=mm_sample,
            )
            sleep(1)

            return my_components.alert_handler(
                response_type,
                response_msg,
                with_close_button=True,
                duration=3000,
            )
        except Exception as e:
            return my_components.alert_handler(
                "unidentified error",
                str(e),
                response_details=traceback.format_exc(),
                with_close_button=True,
                duration=3000,
            )
    else:
        return my_components.alert_handler(
            "unidentified error",  # TODO: Make datatype error
            "Please fill in all fields",
            response_details=f"Sample form valid: {dft.validate_form(sample_form)}\n"
            f"Input parameter form valid: {dft.validate_form(input_form)}",
            with_close_button=True,
            duration=3000,
        )


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("thresholds-dropdown", "data"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_thresholds(*args, **kwargs):
    try:
        kkm_config = deserialize(kwargs["session_state"]["context"])[
            "assay_config"
        ].kkm_configuration
        data = [
            {"value": str(i), "label": k.display_name}
            for i, k in enumerate(kkm_config)
        ]
        return data
    except Exception as e:
        return dash.no_update


# TODO: What is this?
@omero_project_dash.expanded_callback(
    dash.dependencies.Output({"index": dash.dependencies.MATCH}, "variant"),
    dash.dependencies.Input({"index": dash.dependencies.MATCH}, "n_clicks"),
)
def update_heart(n, **kwargs):
    if n % 2 == 0:
        return "default"
    return "filled"


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("accordion-compose-controls", "children"),
    dash.dependencies.Output("thresholds-button-container", "children"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_thresholds_controls(*args, **kwargs):
    try:
        context = deserialize(kwargs["session_state"]["context"])
        kkm_config = context["assay_config"].kkm_configuration
        threshold = context["thresholds"] or {
            k.value: {"upper_limit": "", "lower_limit": ""} for k in kkm_config
        }

        thresholds_component = [
            dmc.AccordionItem(
                [
                    my_components.make_control(
                        kkm.display_name,
                        f"action-{i}",
                    ),
                    dmc.AccordionPanel(
                        id=kkm.value + "_panel",
                        children=[
                            dmc.Fieldset(
                                id={
                                    "type": "threshold-fieldset",
                                    "index": kkm.value,
                                },
                                children=[
                                    dmc.NumberInput(
                                        id={
                                            "type": "threshold-upper",
                                            "index": kkm.value,
                                        },
                                        label="Upper Limit",
                                        placeholder="Enter upper limit",
                                        leftSection=my_components.get_icon(
                                            icon="hugeicons:chart-maximum",
                                            color=THEME["primary"],
                                        ),
                                        value=threshold[kkm.value].get(
                                            "upper_limit", ""
                                        ),
                                    ),
                                    dmc.NumberInput(
                                        id={
                                            "type": "threshold-lower",
                                            "index": kkm.value,
                                        },
                                        label="Lower Limit",
                                        placeholder="Enter lower limit",
                                        leftSection=my_components.get_icon(
                                            icon="hugeicons:chart-minimum",
                                            color=THEME["primary"],
                                        ),
                                        value=threshold[kkm.value].get(
                                            "lower_limit", ""
                                        ),
                                    ),
                                ],
                                variant="filled",
                                radius="md",
                                style={"padding": "10px", "margin": "10px"},
                            )
                        ],
                    ),
                ],
                value=f"item-{i}",
            )
            for i, kkm in enumerate(kkm_config)
        ]
        button = dmc.Button(
            "Update",
            id="modal-submit-button",
            style=BUTTON_STYLE,
        )
        return thresholds_component, button
    except Exception as e:
        return dash.no_update


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("notifications-container", "children"),
    dash.dependencies.Output("loading-overlay-threshold", "visible"),
    [
        dash.dependencies.Input("modal-submit-button", "n_clicks"),
        dash.dependencies.State(
            {"type": "threshold-fieldset", "index": dash.dependencies.ALL}, "id"
        ),
        dash.dependencies.State(
            {"type": "threshold-upper", "index": dash.dependencies.ALL}, "value"
        ),
        dash.dependencies.State(
            {"type": "threshold-lower", "index": dash.dependencies.ALL}, "value"
        ),
    ],
    prevent_initial_call=True,
)
def save_thresholds(*args, **kwargs):
    try:
        context = deserialize(kwargs["session_state"]["context"])
        project_id = int(context["project_id"])
        fieldset_ids, upper_values, lower_values = args[1], args[2], args[3]
        output = {
            fieldset_id["index"]: {"upper_limit": uv, "lower_limit": lv}
            for fieldset_id, uv, lv in zip(fieldset_ids, upper_values, lower_values)
        }
        if output and args[0]:
            response_type, response_msg = views.save_threshold(
                request=kwargs["request"],
                project_id=project_id,
                threshold=output,
            )

            return my_components.notification_handler(
                response_type, response_msg, None
            )[1:]
        else:
            return dash.no_update, False
    except Exception as e:
        return dash.no_update


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("delete-confirm-delete", "opened"),
    dash.dependencies.Output("delete-notifications-container", "children"),
    dash.dependencies.Output("delete-modal-submit-button", "loading"),
    [
        dash.dependencies.Input("delete-data", "n_clicks"),
        dash.dependencies.Input("delete-modal-submit-button", "n_clicks"),
        dash.dependencies.Input("delete-modal-close-button", "n_clicks"),
        dash.dependencies.State("delete-confirm-delete", "opened"),
    ],
    prevent_initial_call=True,
)
def delete_project(*args, **kwargs):
    try:
        triggered_button = kwargs["callback_context"].triggered[0]["prop_id"]
        project_id = deserialize(kwargs["session_state"]["context"])["project_id"]
        request = kwargs["request"]
        opened = not args[3]
        if triggered_button == "delete-modal-submit-button.n_clicks" and args[0] > 0:
            sleep(1)
            response_type, response_msg = views.delete_project(
                request, project_id=project_id
            )

            return my_components.notification_handler(
                response_type, response_msg, opened
            )
        else:
            return opened, None, False
    except Exception as e:
        return dash.no_update


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("download", "data"),
    [
        dash.dependencies.Input("download-yaml", "n_clicks"),
        dash.dependencies.Input("download-json", "n_clicks"),
        dash.dependencies.Input("download-text", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def download_project_data(*args, **kwargs):
    try:
        if not kwargs["callback_context"].triggered:
            raise dash.no_update

        triggered_id = (
            kwargs["callback_context"].triggered[0]["prop_id"].split(".")[0]
        )
        context = deserialize(kwargs["session_state"]["context"])
        mm_dataset_collection = context["mm_dataset_collection"]
        file_name = context["project_name"]
        yaml_dumper = YAMLDumper()
        json_dumper = JSONDumper()
        if triggered_id == "download-yaml":
            return dict(
                content=yaml_dumper.dumps(mm_dataset_collection),
                filename=f"{file_name}.yaml",
            )

        elif triggered_id == "download-json":
            return dict(
                content=json_dumper.dumps(mm_dataset_collection),
                filename=f"{file_name}.json",
            )

        elif triggered_id == "download-text":
            return dict(
                content=yaml_dumper.dumps(mm_dataset_collection),
                filename=f"{file_name}.txt",
            )

        raise dash.no_update
    except Exception as e:
        return dash.no_update


omero_project_dash.clientside_callback(
    """
    function loadingDeleteButton(n_clicks) {
        if (n_clicks > 0) {
            return true;
        }
        return false;
    }
    """,
    dash.dependencies.Output(
        "delete-modal-submit-button", "loading", allow_duplicate=True
    ),
    dash.dependencies.Input("delete-modal-submit-button", "n_clicks"),
    prevent_initial_call=True,
)
