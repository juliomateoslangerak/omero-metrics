import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from datetime import datetime
import pandas as pd
from microscopemetrics_schema import datamodel as mm_schema
from OMERO_metrics.tools import dash_forms_tools as dft
from OMERO_metrics import views
from OMERO_metrics.styles import (
    THEME,
    CARD_STYLE,
    CARD_STYLE1,
    BUTTON_STYLE,
    TAB_STYLES,
    TAB_ITEM_STYLE,
    CONTAINER_STYLE,
    SELECT_STYLES,
    DATEPICKER_STYLES,
    TABLE_MANTINE_STYLE,
    MANTINE_THEME,
    HEADER_PAPER_STYLE,
)
import math
from microscopemetrics.analyses.mappings import MAPPINGS

from time import sleep

sample_types = [x[0] for x in MAPPINGS]
sample_types_dp = [
    {
        "label": dft.add_space_between_capitals(x.__name__),
        "value": f"{i}",
        "description": f"Configure analysis for {x.__name__}",  # Added descriptions
    }
    for i, x in enumerate(sample_types)
]


def make_control(text, action_id):
    return dmc.Flex(
        [
            dmc.AccordionControl(text),
            dmc.ActionIcon(
                children=DashIconify(icon="lets-icons:check-fill"),
                color="green",
                variant="default",
                n_clicks=0,
                id={"index": action_id},
            ),
        ],
        justify="center",
        align="center",
    )


# Initialize the Dash app
dashboard_name = "omero_project_dash"
dash_app_project = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=dmc.styles.ALL,
)


# Define the layout
dash_app_project.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        html.Div(id="blank-input"),
        html.Div(id="save_config_result"),
        dmc.Paper(
            children=[
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                html.Img(
                                    src="/static/OMERO_metrics/images/metrics_logo.png",
                                    style={
                                        "width": "120px",
                                        "height": "auto",
                                    },
                                ),
                                dmc.Stack(
                                    [
                                        dmc.Title(
                                            "Project Dashboard",
                                            c=THEME["primary"],
                                            size="h2",
                                        ),
                                        dmc.Text(
                                            "Microscopy Image Analysis Dashboard",
                                            c=THEME["text"]["secondary"],
                                            size="sm",
                                        ),
                                    ],
                                    gap="xs",
                                ),
                            ],
                        ),
                        dmc.Group(
                            [
                                dmc.Button(
                                    id="download_project_data",
                                    children="Download",
                                    color="blue",
                                    variant="filled",
                                    leftSection=DashIconify(
                                        icon="ic:round-cloud-download"
                                    ),
                                ),
                                # dmc.Select(
                                #     label="Select your favorite library",
                                #     placeholder="Select value",
                                #     id="select-opened",
                                #     value="pd",
                                #     data=[
                                #         {"value": "pd", "label": "Pandas"},
                                #         {"value": "np", "label": "NumPy"},
                                #         {"value": "tf", "label": "TensorFlow"},
                                #         {"value": "torch", "label": "PyTorch"},
                                #     ],
                                #     w=100,
                                #     mb=10,
                                #
                                # ),
                                dmc.Button(
                                    id="delete_project_data",
                                    children="Delete",
                                    color="red",
                                    variant="filled",
                                    leftSection=DashIconify(
                                        icon="ic:round-delete-forever"
                                    ),
                                ),
                                dmc.Badge(
                                    "Project Analysis",
                                    color=THEME["primary"],
                                    variant="dot",
                                    size="lg",
                                ),
                            ]
                        ),
                    ],
                    justify="space-between",
                ),
            ],
            **HEADER_PAPER_STYLE,
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
                            leftSection=DashIconify(icon="ph:chart-line-bold"),
                            color=THEME["primary"],
                            style=TAB_ITEM_STYLE,
                        ),
                        dmc.TabsTab(
                            "Settings",
                            value="settings",
                            leftSection=DashIconify(icon="ph:gear-bold"),
                            color=THEME["primary"],
                            style=TAB_ITEM_STYLE,
                        ),
                        dmc.TabsTab(
                            "Thresholds",
                            value="thresholds",
                            leftSection=DashIconify(icon="ph:ruler-bold"),
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
                                                        leftSection=DashIconify(
                                                            icon="ph:magnifying-glass"
                                                        ),
                                                        value="0",
                                                        rightSection=DashIconify(
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
                                                        leftSection=DashIconify(
                                                            icon="ph:calendar"
                                                        ),
                                                        styles=DATEPICKER_STYLES,
                                                    ),
                                                ],
                                            ),
                                        ],
                                        style={
                                            "marginBottom": "12px",
                                        },
                                    ),
                                    html.Div(
                                        id="graph-project",
                                        style={"height": "250px"},
                                        children=dmc.LineChart(
                                            id="line-chart",
                                            h=300,
                                            data=[],
                                            dataKey="Date",
                                            withLegend=True,
                                            legendProps={
                                                "horizontalAlign": "top",
                                                "left": 50,
                                            },
                                            series=[],
                                            curveType="natural",
                                            style={"padding": 20},
                                            xAxisLabel="Processed Date",
                                        ),
                                    ),
                                ],
                            ),
                            # Data Table Section
                            dmc.Paper(
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
                                overlayProps={"radius": "sm", "blur": 2},
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
                                overlayProps={"radius": "sm", "blur": 2},
                            ),
                            dmc.Paper(
                                style={**CARD_STYLE1, "marginTop": "12px"},
                                children=[
                                    dmc.Accordion(
                                        id="accordion-compose-controls",
                                        chevron=DashIconify(
                                            icon="ant-design:plus-outlined"
                                        ),
                                        disableChevronRotation=True,
                                        children=[],
                                    ),
                                    dmc.Group(
                                        justify="flex-end",
                                        mt="xl",
                                        children=[
                                            dmc.Button(
                                                "Update",
                                                id="modal-submit-button",
                                                style=BUTTON_STYLE,
                                            ),
                                        ],
                                    ),
                                    dmc.NotificationProvider(
                                        position="top-center"
                                    ),
                                    html.Div(id="notifications-container"),
                                    html.Div(id="result_data"),
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


@dash_app_project.expanded_callback(
    dash.dependencies.Output("project-dropdown", "data"),
    dash.dependencies.Output("date-picker", "minDate"),
    dash.dependencies.Output("date-picker", "maxDate"),
    dash.dependencies.Output("date-picker", "value"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_dropdown(*args, **kwargs):
    kkm = kwargs["session_state"]["context"]["kkm"]
    kkm = [k.replace("_", " ").title() for k in kkm]
    dates = kwargs["session_state"]["context"]["dates"]
    options = [{"value": f"{i}", "label": f"{k}"} for i, k in enumerate(kkm)]
    min_date = min(dates)
    max_date = max(dates)
    data = options
    value_date = [min_date, max_date]
    return data, min_date, max_date, value_date


@dash_app_project.expanded_callback(
    dash.dependencies.Output("line-chart", "data"),
    dash.dependencies.Output("line-chart", "series"),
    dash.dependencies.Output("line-chart", "referenceLines"),
    [
        dash.dependencies.Input("project-dropdown", "value"),
        dash.dependencies.Input("date-picker", "value"),
    ],
    prevent_initial_call=True,
)
def update_table(*args, **kwargs):
    df_list = kwargs["session_state"]["context"]["key_measurements_list"]
    threshold = kwargs["session_state"]["context"]["threshold"]
    kkm = kwargs["session_state"]["context"]["kkm"]
    measurement = int(args[0])
    if threshold:
        threshold_kkm = threshold[kkm[measurement]]
        ref = [
            {
                "y": v,
                "label": k.replace("_", " ").title(),
                "color": "red.6",
            }
            for k, v in threshold_kkm.items()
            if v
        ]
    else:
        ref = []
    dates_range = args[1]
    print(f"Dates range: {dates_range}")
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
    # kkm = [k.replace("_", " ").title() for k in kkm]
    df_list_filtered = [df_list[i] for i in df_dates]
    data = [
        {"Date": dates[i], "Name": f"Dataset {i}"}
        | df[[kkm[measurement]]]
        .copy()
        .mean()
        .reset_index(name="Mean")
        .rename(columns={"index": "Measurement"})
        .pivot_table(columns="Measurement")
        .to_dict("records")[0]
        for i, df in enumerate(df_list_filtered)
    ]
    series = [
        {
            "name": kkm[measurement],
            "color": "green.7",
        }
    ]
    return data, series, ref


@dash_app_project.expanded_callback(
    dash.dependencies.Output("text_km", "children"),
    dash.dependencies.Output("kkm_table", "data"),
    dash.dependencies.Output("pagination", "total"),
    [
        dash.dependencies.Input("line-chart", "clickData"),
        dash.dependencies.Input("pagination", "value"),
    ],
    prevent_initial_call=True,
)
def update_project_view(*args, **kwargs):
    if args[0]:
        page = args[1]
        table = kwargs["session_state"]["context"]["key_measurements_list"]
        dates = kwargs["session_state"]["context"]["dates"]
        kkm = kwargs["session_state"]["context"]["kkm"]
        selected_dataset = int(args[0]["Name"].split(" ")[-1])
        df_selected = table[selected_dataset]
        table_kkm = df_selected[kkm].copy()
        table_kkm = table_kkm.round(3)
        total = math.ceil(len(table_kkm) / 4)
        start_idx = (page - 1) * 4
        end_idx = start_idx + 4
        table_kkm.columns = table_kkm.columns.str.replace("_", " ").str.title()
        date = dates[selected_dataset]
        page_data = table_kkm.iloc[start_idx:end_idx]
        grid = {
            "head": page_data.columns.tolist(),
            "body": page_data.values.tolist(),
            "caption": "Key Measurements for the selected dataset",
        }
        return ("Key Measurements" " processed at " + str(date), grid, total)

    else:
        return dash.no_update


@dash_app_project.expanded_callback(
    dash.dependencies.Output("input_parameters_container", "children"),
    dash.dependencies.Output("sample_container", "children"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_modal(*args, **kwargs):
    setup = kwargs["session_state"]["context"]["setup"]
    sample = setup["sample"]
    mm_sample = getattr(mm_schema, sample["type"])
    mm_sample = mm_sample(**sample["fields"])
    sample_form = dft.DashForm(
        mm_sample, disabled=False, form_id="sample_form"
    )
    input_parameters = setup["input_parameters"]
    mm_input_parameters = getattr(mm_schema, input_parameters["type"])
    mm_input_parameters = mm_input_parameters(**input_parameters["fields"])
    input_parameters_form = dft.DashForm(
        mm_input_parameters, disabled=False, form_id="input_parameters_form"
    )

    return (
        input_parameters_form.form,
        sample_form.form,
    )


dash_app_project.clientside_callback(
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
dash_app_project.clientside_callback(
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


@dash_app_project.expanded_callback(
    dash.dependencies.Output("save_config_result", "children"),
    dash.dependencies.Output("loading-overlay", "visible"),
    [
        dash.dependencies.Input("submit_config", "n_clicks"),
        dash.dependencies.State("sample_form", "children"),
        dash.dependencies.State("input_parameters_form", "children"),
    ],
    prevent_initial_call=True,
)
def update_config_project(*args, **kwargs):
    sample_form = args[1]
    input_form = args[2]
    print(f"Sample form valid: {sample_form}")
    print(f"Input form valid: {input_form}")
    project_id = int(kwargs["session_state"]["context"]["project_id"])
    request = kwargs["request"]
    setup = kwargs["session_state"]["context"]["setup"]
    sample = setup["sample"]
    mm_sample = getattr(mm_schema, sample["type"])
    input_parameters = setup["input_parameters"]
    mm_input_parameters = getattr(mm_schema, input_parameters["type"])
    if dft.validate_form(sample_form) and dft.validate_form(input_form):
        try:
            input_parameters = dft.extract_form_data(
                input_form, mm_input_parameters.class_name
            )
            mm_input_parameters = mm_input_parameters(**input_parameters)
            sample = dft.extract_form_data(sample_form, mm_sample.class_name)
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
                    icon=DashIconify(
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
                    icon=DashIconify(icon="mdi:alert"),
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
                icon=DashIconify(icon="mdi:alert"),
                title="Error!",
                radius="md",
                withCloseButton=True,
                duration=3000,
            )
        ], False


# @dash_app_project.expanded_callback(
#     dash.dependencies.Output("modal-simple", "opened"),
#     [
#         dash.dependencies.Input("modal-demo-button", "n_clicks"),
#         dash.dependencies.Input("modal-close-button", "n_clicks"),
#         dash.dependencies.Input("modal-submit-button", "n_clicks"),
#         dash.dependencies.State("modal-simple", "opened"),
#     ],
#     prevent_initial_call=True,
# )
# def modal_demo(*args, **kwargs):
#     opened = args[3]
#     return not opened


@dash_app_project.expanded_callback(
    dash.dependencies.Output("thresholds-dropdown", "data"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_thresholds(*args, **kwargs):
    kkm = kwargs["session_state"]["context"]["kkm"]
    kkm = [k.replace("_", " ").title() for k in kkm]
    data = [{"value": f"{i}", "label": f"{k}"} for i, k in enumerate(kkm)]
    return data


@dash_app_project.expanded_callback(
    dash.dependencies.Output({"index": dash.dependencies.MATCH}, "variant"),
    dash.dependencies.Input({"index": dash.dependencies.MATCH}, "n_clicks"),
)
def update_heart(*args, **kwargs):
    n = args[0]
    if n % 2 == 0:
        return "default"
    return "filled"


@dash_app_project.expanded_callback(
    dash.dependencies.Output("accordion-compose-controls", "children"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_thresholds_controls(*args, **kwargs):
    kkm = kwargs["session_state"]["context"]["kkm"]
    threshold = kwargs["session_state"]["context"]["threshold"]
    # kkm = [k.replace("_", " ").title() for k in kkm]
    if threshold:
        new_kkm = threshold
    else:
        new_kkm = {k: {"upper_limit": "", "lower_limit": ""} for k in kkm}

    threshold_control = [
        dmc.AccordionItem(
            [
                make_control(
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
                                    leftSection=DashIconify(
                                        icon="hugeicons:chart-maximum",
                                        color=THEME["primary"],
                                    ),
                                    value=value.get("upper_limit", ""),
                                ),
                                dmc.NumberInput(
                                    label="Lower Limit",
                                    placeholder="Enter lower limit",
                                    leftSection=DashIconify(
                                        icon="hugeicons:chart-minimum",
                                        color=THEME["primary"],
                                    ),
                                    value=value.get("lower_limit", ""),
                                ),
                            ],
                            # legend=key.replace("_", " ").title(),
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
    return threshold_control


@dash_app_project.expanded_callback(
    dash.dependencies.Output("notifications-container", "children"),
    dash.dependencies.Output("loading-overlay-threshold", "visible"),
    [
        dash.dependencies.Input("modal-submit-button", "n_clicks"),
        dash.dependencies.State("accordion-compose-controls", "children"),
    ],
    prevent_initial_call=True,
)
def threshold_callback1(*args, **kwargs):
    kkm = kwargs["session_state"]["context"]["kkm"]
    output = get_accordion_data(args[1], kkm)
    request = kwargs["request"]
    project_id = kwargs["session_state"]["context"]["project_id"]
    print(output)
    if output:
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
                    DashIconify(icon="ic:round-celebration")
                    if color == "green"
                    else DashIconify(icon="ic:round-error")
                ),
            ),
            False,
        )
    else:
        return dash.no_update, False


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
