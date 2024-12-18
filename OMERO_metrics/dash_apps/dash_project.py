import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from datetime import datetime
import pandas as pd
from linkml_runtime.dumpers import YAMLDumper, JSONDumper
from microscopemetrics_schema import datamodel as mm_schema
from OMERO_metrics.tools import dash_forms_tools as dft
from OMERO_metrics import views
from OMERO_metrics.styles import (
    THEME,
    CARD_STYLE1,
    BUTTON_STYLE,
    TAB_STYLES,
    TAB_ITEM_STYLE,
    CONTAINER_STYLE,
    SELECT_STYLES,
    DATEPICKER_STYLES,
    TABLE_MANTINE_STYLE,
    MANTINE_THEME,
    COLORS_CHANNELS,
)
import math
from time import sleep
import OMERO_metrics.dash_apps.dash_utils.omero_metrics_components as my_components


# Initialize the Dash app
dashboard_name = "omero_project_dash"
omero_project_dash = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=dmc.styles.ALL,
)


# Define the layout
omero_project_dash.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dmc.NotificationProvider(position="top-center"),
        html.Div(id="delete-notifications-container"),
        dmc.Modal(
            title="Confirm Delete",
            id="delete-confirm_delete",
            children=[
                dmc.Text(
                    "Are you sure you want to delete this project outputs?"
                ),
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
        html.Div(id="blank-input"),
        html.Div(id="save_config_result"),
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
                            leftSection=my_components.get_icon(
                                icon="ph:gear-bold"
                            ),
                            color=THEME["primary"],
                            style=TAB_ITEM_STYLE,
                        ),
                        dmc.TabsTab(
                            "Thresholds",
                            value="thresholds",
                            leftSection=my_components.get_icon(
                                icon="ph:ruler-bold"
                            ),
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
                                                        id="project-dropdown",
                                                        label="Select Measurement",
                                                        placeholder="Choose a measurement",
                                                        leftSection=my_components.get_icon(
                                                            icon="ph:magnifying-glass"
                                                        ),
                                                        value="0",
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
                                                    dmc.DatePicker(
                                                        id="date-picker",
                                                        label="Date Range",
                                                        type="range",
                                                        valueFormat="DD-MM-YYYY",
                                                        placeholder="Select date range",
                                                        leftSection=my_components.get_icon(
                                                            icon="ph:calendar"
                                                        ),
                                                        miw=150,
                                                        disabledDates=True,
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
                                    html.Div(
                                        id="graph-project",
                                        style={"height": "250px"},
                                        children=[
                                            dmc.LineChart(
                                                id="line-chart",
                                                h=300,
                                                data=[],
                                                dataKey="date",
                                                withLegend=True,
                                                legendProps={
                                                    "horizontalAlign": "top",
                                                    "left": 50,
                                                },
                                                series=[],
                                                curveType="linear",
                                                style={"padding": 20},
                                                xAxisLabel="Processed Date",
                                                connectNulls=True,
                                            ),
                                            html.Div(id="feedback_message"),
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
                                        id="text_km",
                                        c="#189A35",
                                        mt=10,
                                        ml=10,
                                        mr=10,
                                        fw="bold",
                                    ),
                                    dmc.ScrollArea(
                                        [
                                            dmc.Table(
                                                id="kkm_table",
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
                                                id="input_parameters_container",
                                                span="6",
                                            ),
                                            dmc.GridCol(
                                                id="sample_container",
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
                                                id="submit_config",
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
                                        id="thresholds-button_container",
                                        children=[],
                                    ),
                                    html.Div(id="notifications-container"),
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
    dash.dependencies.Output("project-dropdown", "data"),
    dash.dependencies.Output("date-picker", "minDate"),
    dash.dependencies.Output("date-picker", "maxDate"),
    dash.dependencies.Output("date-picker", "value"),
    dash.dependencies.Output("date-picker", "disabledDates"),
    dash.dependencies.Output("project-dropdown", "disabled"),
    dash.dependencies.Output("activate_download", "disabled"),
    dash.dependencies.Output("delete_data", "disabled"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_dropdown(*args, **kwargs):
    try:
        kkm = kwargs["session_state"]["context"]["kkm"]
        kkm = [k.replace("_", " ").title() for k in kkm]
        dates = kwargs["session_state"]["context"]["dates"]
        options = [
            {"value": f"{i}", "label": f"{k}"} for i, k in enumerate(kkm)
        ]
        min_date = min(dates)
        max_date = max(dates)
        data = options
        value_date = [min_date, max_date]
        return data, min_date, max_date, value_date, False, False, False, False
    except Exception as e:
        return (
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
        data = kwargs["session_state"]["context"]["key_measurements_list"]
        if data:
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
    dash.dependencies.Output("line-chart", "data"),
    dash.dependencies.Output("line-chart", "series"),
    dash.dependencies.Output("line-chart", "referenceLines"),
    [
        dash.dependencies.Input("project-dropdown", "value"),
        dash.dependencies.Input("date-picker", "value"),
    ],
    prevent_initial_call=True,
)
def update_table(measurement, dates_range, **kwargs):
    try:

        df_list = kwargs["session_state"]["context"]["key_measurements_list"]
        threshold = kwargs["session_state"]["context"]["threshold"]
        kkm = kwargs["session_state"]["context"]["kkm"]
        measurement = int(measurement)

        # Check if we have any data
        if not df_list:
            return dash.no_update
        if threshold:
            threshold_kkm = threshold[kkm[measurement]]
            ref = [
                {
                    "y": v,
                    "label": k.replace("_", " ").title(),
                    "color": "red.6" if k == "upper_limit" else "yellow.6",
                }
                for k, v in threshold_kkm.items()
                if v
            ]
        else:
            ref = []

        dates = kwargs["session_state"]["context"]["dates"]
        df_filtering = pd.DataFrame(dates, columns=["Date"])
        df_dates = df_filtering[
            (
                df_filtering["Date"]
                >= datetime.strptime(dates_range[0], "%Y-%m-%d").date()
            )
            & (
                df_filtering["Date"]
                <= datetime.strptime(dates_range[1], "%Y-%m-%d").date()
            )
        ].index.to_list()

        df_list_filtered = [df_list[i] for i in df_dates]
        dates_filtered = [dates[i] for i in df_dates]
        df = my_components.get_data_trends(
            kkm, measurement, dates_filtered, df_list_filtered
        )

        data = df.to_dict("records")
        channels = [
            c for c in df.columns if c not in ["dataset_index", "date"]
        ]
        series = [
            {
                "name": channel,
                "color": COLORS_CHANNELS[i % len(COLORS_CHANNELS)],
            }
            for i, channel in enumerate(channels)
        ]
        return data, series, ref

    except Exception as e:
        return dash.no_update


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("text_km", "children"),
    dash.dependencies.Output("kkm_table", "data"),
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
            table = kwargs["session_state"]["context"]["key_measurements_list"]
            dates = kwargs["session_state"]["context"]["dates"]
            kkm = kwargs["session_state"]["context"]["kkm"]
            selected_dataset = int(clicked_data["dataset_index"])
            df_selected = table[selected_dataset]
            table_kkm = df_selected.filter(["channel_name", *kkm])
            table_kkm = table_kkm.round(3)
            total = math.ceil(len(table_kkm) / 4)
            start_idx = (page - 1) * 4
            end_idx = start_idx + 4
            table_kkm.columns = table_kkm.columns.str.replace(
                "_", " "
            ).str.title()
            date = dates[selected_dataset]
            page_data = table_kkm.iloc[start_idx:end_idx]
            grid = {
                "head": page_data.columns.tolist(),
                "body": page_data.values.tolist(),
                "caption": "Key Measurements for the selected dataset",
            }
            return (
                f"Key Measurements processed at {str(date)}",
                grid,
                total,
                {"visible": True},
            )

        else:
            return dash.no_update
    except Exception as e:
        return dash.no_update


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("input_parameters_container", "children"),
    dash.dependencies.Output("sample_container", "children"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_modal(*args, **kwargs):
    setup = kwargs["session_state"]["context"]["setup"]
    sample = setup["sample"]
    mm_sample = getattr(mm_schema, sample["type"])
    mm_sample = mm_sample(**sample["fields"])
    sample_form = dft.get_form(
        mm_sample, disabled=False, form_id="sample_form"
    )
    input_parameters = setup["input_parameters"]
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
    dash.dependencies.Output(
        "loading-overlay", "visible", allow_duplicate=True
    ),
    dash.dependencies.Input("submit_config", "n_clicks"),
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
    dash.dependencies.Output("save_config_result", "children"),
    dash.dependencies.Output("loading-overlay", "visible"),
    [
        dash.dependencies.Input("submit_config", "n_clicks"),
        dash.dependencies.State("sample_form", "children"),
        dash.dependencies.State("input_parameters_form", "children"),
    ],
    prevent_initial_call=True,
)
def update_config_project(submit_click, sample_form, input_form, **kwargs):
    project_id = int(kwargs["session_state"]["context"]["project_id"])
    request = kwargs["request"]
    setup = kwargs["session_state"]["context"]["setup"]
    sample = setup["sample"]
    mm_sample = getattr(mm_schema, sample["type"])
    input_parameters = setup["input_parameters"]
    mm_input_parameters = getattr(mm_schema, input_parameters["type"])
    if dft.validate_form(sample_form) and dft.validate_form(input_form):
        try:
            input_parameters = dft.extract_form_data(input_form)
            mm_input_parameters = mm_input_parameters(**input_parameters)
            sample = dft.extract_form_data(sample_form)
            mm_sample = mm_sample(**sample)
            response, color = views.save_config(
                request=request,
                project_id=int(project_id),
                input_parameters=mm_input_parameters,
                sample=mm_sample,
            )
            sleep(1)
            return [
                dmc.Alert(
                    children=[
                        dmc.Title(response, order=4),
                        dmc.Text(
                            (
                                "Your configuration has been saved successfully."
                                if color == "green"
                                else "An error occurred while saving your configuration."
                            ),
                            size="sm",
                        ),
                    ],
                    color=color,
                    icon=my_components.get_icon(
                        icon=(
                            "mdi:check-circle"
                            if color == "green"
                            else "mdi:alert-circle"
                        )
                    ),
                    title="Success!" if color == "green" else "Error!",
                    radius="md",
                    withCloseButton=True,
                    duration=3000,
                )
            ], False
        except Exception as e:
            return [
                dmc.Alert(
                    children=[
                        dmc.Title("Error", order=4),
                        dmc.Text(str(e), size="sm"),
                    ],
                    color="red",
                    icon=my_components.get_icon(icon="mdi:alert"),
                    title="Error!",
                    radius="md",
                    withCloseButton=True,
                    duration=3000,
                )
            ], False
    else:
        return [
            dmc.Alert(
                children=[
                    dmc.Text("Please fill in all fields", size="sm"),
                    dmc.Text(
                        f"Sample form valid: {dft.validate_form(sample_form)}",
                        size="sm",
                    ),
                    dmc.Text(
                        f"Input parameter form valid: {dft.validate_form(input_form)}",
                        size="sm",
                    ),
                ],
                color="red",
                icon=my_components.get_icon(icon="mdi:alert"),
                title="Error!",
                radius="md",
                withCloseButton=True,
                duration=3000,
            )
        ], False


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("thresholds-dropdown", "data"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_thresholds(*args, **kwargs):
    try:
        kkm = kwargs["session_state"]["context"]["kkm"]
        kkm = [k.replace("_", " ").title() for k in kkm]
        data = [{"value": f"{i}", "label": f"{k}"} for i, k in enumerate(kkm)]
        return data
    except Exception as e:
        return dash.no_update


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
    dash.dependencies.Output("thresholds-button_container", "children"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_thresholds_controls(*args, **kwargs):
    try:
        kkm = kwargs["session_state"]["context"]["kkm"]
        threshold = kwargs["session_state"]["context"]["threshold"]
        if threshold:
            new_kkm = threshold
        else:
            new_kkm = {k: {"upper_limit": "", "lower_limit": ""} for k in kkm}

        threshold_control = [
            dmc.AccordionItem(
                [
                    my_components.make_control(
                        key.replace("_", " ").title(),
                        f"action-{i}",
                    ),
                    dmc.AccordionPanel(
                        id=key + "_panel",
                        children=[
                            dmc.Fieldset(
                                id=key + "_fieldset",
                                children=[
                                    dmc.NumberInput(
                                        label="Upper Limit",
                                        placeholder="Enter upper limit",
                                        leftSection=my_components.get_icon(
                                            icon="hugeicons:chart-maximum",
                                            color=THEME["primary"],
                                        ),
                                        value=value.get("upper_limit", ""),
                                    ),
                                    dmc.NumberInput(
                                        label="Lower Limit",
                                        placeholder="Enter lower limit",
                                        leftSection=my_components.get_icon(
                                            icon="hugeicons:chart-minimum",
                                            color=THEME["primary"],
                                        ),
                                        value=value.get("lower_limit", ""),
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
            for i, (key, value) in enumerate(new_kkm.items())
        ]
        button = dmc.Button(
            "Update",
            id="modal-submit-button",
            style=BUTTON_STYLE,
        )
        return threshold_control, button
    except Exception as e:
        return dash.no_update


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("notifications-container", "children"),
    dash.dependencies.Output("loading-overlay-threshold", "visible"),
    [
        dash.dependencies.Input("modal-submit-button", "n_clicks"),
        dash.dependencies.State("accordion-compose-controls", "children"),
    ],
    prevent_initial_call=True,
)
def threshold_callback1(*args, **kwargs):
    try:
        kkm = kwargs["session_state"]["context"]["kkm"]
        output = get_accordion_data(args[1], kkm)
        request = kwargs["request"]
        project_id = kwargs["session_state"]["context"]["project_id"]
        if output and args[0] > 0:
            response, color = views.save_threshold(
                request=request,
                project_id=int(project_id),
                threshold=output,
            )
            return (
                dmc.Notification(
                    title="Thresholds Updated",
                    id="simple-notify",
                    color=color,
                    action="show",
                    message=response,
                    icon=(
                        my_components.get_icon(icon="ic:round-celebration")
                        if color == "green"
                        else my_components.get_icon(icon="ic:round-error")
                    ),
                ),
                False,
            )
        else:
            return dash.no_update, False
    except Exception as e:
        return dash.no_update


def get_accordion_data(accordion_state, kkm):
    dict_data = {}
    try:
        for i in accordion_state:
            index = i["props"]["children"][1]["props"]["children"][0]["props"][
                "children"
            ]
            key = (
                i["props"]["children"][0]["props"]["children"][0]["props"][
                    "children"
                ]
                .replace(" ", "_")
                .lower()
            )
            dict_data[key] = {
                "upper_limit": (
                    index[0]["props"]["value"]
                    if "value" in index[0]["props"]
                    else ""
                ),
                "lower_limit": (
                    index[1]["props"]["value"]
                    if "value" in index[1]["props"]
                    else ""
                ),
            }
    except Exception as e:
        dict_data = {
            key: {"upper_limit": "", "lower_limit": ""} for key in kkm
        }
        print(f"Error: {e}")
    return dict_data


@omero_project_dash.expanded_callback(
    dash.dependencies.Output("delete-confirm_delete", "opened"),
    dash.dependencies.Output("delete-notifications-container", "children"),
    dash.dependencies.Output("delete-modal-submit-button", "loading"),
    [
        dash.dependencies.Input("delete_data", "n_clicks"),
        dash.dependencies.Input("delete-modal-submit-button", "n_clicks"),
        dash.dependencies.Input("delete-modal-close-button", "n_clicks"),
        dash.dependencies.State("delete-confirm_delete", "opened"),
    ],
    prevent_initial_call=True,
)
def delete_project(*args, **kwargs):
    try:
        triggered_button = kwargs["callback_context"].triggered[0]["prop_id"]
        project_id = kwargs["session_state"]["context"]["project_id"]
        request = kwargs["request"]
        opened = not args[3]
        if (
            triggered_button == "delete-modal-submit-button.n_clicks"
            and args[0] > 0
        ):
            sleep(1)
            msg, color = views.delete_project(request, project_id=project_id)
            message = dmc.Notification(
                title="Notification!",
                id="simple-notify",
                action="show",
                message=msg,
                icon=my_components.get_icon(
                    icon=(
                        "akar-icons:circle-check"
                        if color == "green"
                        else "akar-icons:circle-x"
                    )
                ),
                color=color,
            )
            return opened, message, False
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
        mm_datasets = kwargs["session_state"]["context"]["mm_datasets"]
        file_name = kwargs["session_state"]["context"]["project_name"]
        yaml_dumper = YAMLDumper()
        json_dumper = JSONDumper()
        if triggered_id == "download-yaml":
            return dict(
                content=yaml_dumper.dumps(mm_datasets),
                filename=f"{file_name}.yaml",
            )

        elif triggered_id == "download-json":
            return dict(
                content=json_dumper.dumps(mm_datasets),
                filename=f"{file_name}.json",
            )

        elif triggered_id == "download-text":
            return dict(
                content=yaml_dumper.dumps(mm_datasets),
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
