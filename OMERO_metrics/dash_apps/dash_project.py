import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from datetime import datetime
import pandas as pd
from microscopemetrics_schema import datamodel as mm_schema
from OMERO_metrics.tools import dash_forms_tools as dft


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


# Modern color palette
COLORS = {
    "primary": "#10B981",  # Emerald-500
    "primary_light": "#D1FAE5",  # Emerald-100
    "secondary": "#1E293B",  # Slate-800
    "background": "#F8FAFC",  # Slate-50
    "surface": "#FFFFFF",
    "border": "#E2E8F0",  # Slate-200
    "text": "#334155",  # Slate-700
    "text_light": "#64748B",  # Slate-500
}

# Consistent styling
CARD_STYLE = {
    "backgroundColor": COLORS["surface"],
    "borderRadius": "8px",
    "border": f'1px solid {COLORS["border"]}',
    "padding": "24px",
    "height": "100%",
    "boxShadow": "0 1px 3px 0 rgb(0 0 0 / 0.1)",
}

BUTTON_STYLE = {
    "backgroundColor": COLORS["primary"],
    "color": "white",
    "fontSize": "14px",
    "fontWeight": 500,
    "height": "40px",
    "padding": "0 16px",
    "borderRadius": "6px",
}

# Initialize the Dash app
dashboard_name = "omero_project_dash"
dash_app_project = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=dmc.styles.ALL,
)

# Define the layout
dash_app_project.layout = dmc.MantineProvider(
    theme={
        "primaryColor": "teal",
        "components": {
            "Button": {"styles": {"root": {"fontWeight": 500}}},
            "Select": {"styles": {"input": {"height": "40px"}}},
            "DatePicker": {"styles": {"input": {"height": "40px"}}},
        },
    },
    children=[
        dmc.Container(
            fluid=True,
            style={
                "backgroundColor": COLORS["background"],
                "minHeight": "100vh",
                "padding": "24px",
            },
            children=[
                html.Div(id="blank-input"),
                # Header Section
                dmc.Paper(
                    style={**CARD_STYLE, "marginBottom": "24px"},
                    children=[
                        dmc.Group(
                            justify="space-between",
                            align="center",
                            children=[
                                dmc.Group(
                                    children=[
                                        html.Img(
                                            src="/static/OMERO_metrics/images/metrics_logo.png",
                                            style={"width": "48px"},
                                        ),
                                        dmc.Title(
                                            "Project Dashboard",
                                            order=2,
                                            style={
                                                "color": COLORS["secondary"]
                                            },
                                        ),
                                    ]
                                ),
                                dmc.Text(
                                    f"Last updated: {datetime.now().strftime('%B %d, %Y %H:%M')}",
                                    c="dimmed",
                                    size="sm",
                                ),
                            ],
                        ),
                    ],
                ),
                # Navigation Tabs
                dmc.Tabs(
                    value="dashboard",
                    styles={
                        "tab": {
                            "fontSize": "14px",
                            "fontWeight": 500,
                            "height": "40px",
                            "borderRadius": "6px",
                            "&[data-active]": {
                                "backgroundColor": COLORS["primary_light"],
                                "color": COLORS["primary"],
                            },
                        }
                    },
                    children=[
                        dmc.TabsList(
                            children=[
                                dmc.TabsTab(
                                    "Dashboard",
                                    value="dashboard",
                                    leftSection=DashIconify(
                                        icon="ph:chart-line-bold"
                                    ),
                                ),
                                dmc.TabsTab(
                                    "Settings",
                                    value="settings",
                                    leftSection=DashIconify(
                                        icon="ph:gear-bold"
                                    ),
                                ),
                                dmc.TabsTab(
                                    "Thresholds",
                                    value="thresholds",
                                    leftSection=DashIconify(
                                        icon="ph:ruler-bold"
                                    ),
                                ),
                            ],
                        ),
                        # Dashboard Panel
                        dmc.TabsPanel(
                            value="dashboard",
                            children=[
                                # Filters Section
                                dmc.Paper(
                                    style={**CARD_STYLE, "marginTop": "24px"},
                                    children=[
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
                                                            styles={
                                                                "label": {
                                                                    "marginBottom": "8px"
                                                                }
                                                            },
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
                                                            styles={
                                                                "label": {
                                                                    "marginBottom": "8px"
                                                                }
                                                            },
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                # Chart Section
                                dmc.Paper(
                                    style={**CARD_STYLE, "marginTop": "24px"},
                                    children=[
                                        dmc.Title(
                                            "Measurement Trends",
                                            order=3,
                                            style={"marginBottom": "16px"},
                                        ),
                                        html.Div(
                                            id="graph-project",
                                            style={"height": "250px"},
                                        ),
                                    ],
                                ),
                                # Data Table Section
                                dmc.Paper(
                                    style={**CARD_STYLE, "marginTop": "24px"},
                                    children=[
                                        dmc.Text(
                                            id="text_km",
                                            c="#189A35",
                                            mt=10,
                                            ml=10,
                                            mr=10,
                                            fw="bold",
                                        ),
                                        html.Div(id="click_data"),
                                    ],
                                ),
                            ],
                        ),
                        # Settings Panel
                        dmc.TabsPanel(
                            value="settings",
                            children=[
                                dmc.Paper(
                                    style={**CARD_STYLE, "marginTop": "24px"},
                                    children=[
                                        dmc.Grid(
                                            children=[
                                                dmc.GridCol(
                                                    id="input_parameters_container",
                                                    span=6,
                                                ),
                                                dmc.GridCol(
                                                    id="sample_container",
                                                    span=6,
                                                ),
                                            ],
                                        ),
                                        dmc.Group(
                                            justify="flex-end",
                                            mt="xl",
                                            children=[
                                                dmc.Button(
                                                    "Reset",
                                                    id="modal-close-button",
                                                    variant="outline",
                                                    color="red",
                                                ),
                                                dmc.Button(
                                                    "Update",
                                                    id="modal-submit-button",
                                                    style=BUTTON_STYLE,
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        # Thresholds Panel
                        dmc.TabsPanel(
                            value="thresholds",
                            children=[
                                dmc.Paper(
                                    style={**CARD_STYLE, "marginTop": "24px"},
                                    children=[
                                        # dmc.Grid(
                                        #     children=[
                                        #         dmc.GridCol(
                                        #             span=4,
                                        #             children=[
                                        #                 dmc.Select(
                                        #                     id="thresholds-dropdown",
                                        #                     label="Select KKM",
                                        #                     placeholder="Choose KKM",
                                        #                 ),
                                        #             ],
                                        #         ),
                                        #         dmc.GridCol(
                                        #             span=4,
                                        #             children=[
                                        #                 dmc.Select(
                                        #                     label="Threshold Type",
                                        #                     data=[
                                        #                         "Upper Limit",
                                        #                         "Lower Limit",
                                        #                     ],
                                        #                     placeholder="Select type",
                                        #                 ),
                                        #             ],
                                        #         ),
                                        #         dmc.GridCol(
                                        #             span=4,
                                        #             children=[
                                        #                 dmc.NumberInput(
                                        #                     label="Value",
                                        #                     placeholder="Enter threshold",
                                        #                 ),
                                        #             ],
                                        #         ),
                                        #     ],
                                        # ),
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
                                                    "Reset",
                                                    id="modal-close-button",
                                                    variant="outline",
                                                    color="red",
                                                ),
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
                                        dmc.Button(
                                            "Show Notification", id="notify"
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
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
    dash.dependencies.Output("graph-project", "children"),
    [
        dash.dependencies.Input("project-dropdown", "value"),
        dash.dependencies.Input("date-picker", "value"),
    ],
)
def update_table(*args, **kwargs):
    df_list = kwargs["session_state"]["context"]["key_measurements_list"]
    kkm = kwargs["session_state"]["context"]["kkm"]
    measurement = int(args[0])
    dates_range = args[1]
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
    line = dmc.LineChart(
        id="line-chart",
        h=300,
        dataKey="Date",
        data=data,
        withLegend=True,
        legendProps={"horizontalAlign": "top", "height": 50},
        series=[{"name": kkm[measurement], "color": "green.7"}],
        curveType="natural",
        style={"padding": 20},
        xAxisLabel="Processed Date",
        # yAxisLabel=str(kkm[measurement]).replace("_", " ").title(),
    )

    return line


@dash_app_project.expanded_callback(
    dash.dependencies.Output("text_km", "children"),
    dash.dependencies.Output("click_data", "children"),
    [dash.dependencies.Input("line-chart", "clickData")],
    prevent_initial_call=True,
)
def update_project_view(*args, **kwargs):
    if args[0]:
        table = kwargs["session_state"]["context"]["key_measurements_list"]
        dates = kwargs["session_state"]["context"]["dates"]
        kkm = kwargs["session_state"]["context"]["kkm"]
        selected_dataset = int(args[0]["Name"].split(" ")[-1])
        df_selected = table[selected_dataset]
        table_kkm = df_selected[kkm].copy()
        table_kkm = table_kkm.round(3)
        table_kkm.columns = table_kkm.columns.str.replace("_", " ").str.title()
        date = dates[selected_dataset]
        grid = dmc.ScrollArea(
            [
                dmc.Table(
                    striped=True,
                    data={
                        "head": table_kkm.columns.tolist(),
                        "body": table_kkm.values.tolist(),
                        "caption": "Key Measurements for the selected dataset",
                    },
                    highlightOnHover=True,
                    style={
                        "background-color": "white",
                        "width": "98%",
                        "height": "auto",
                        "margin": "5px",
                        "border-radius": "0.5rem",
                        "align": "center",
                    },
                )
            ]
        )
        return (
            "Key Measurements" " processed at " + str(date),
            grid,
        )

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


@dash_app_project.expanded_callback(
    dash.dependencies.Output("modal-simple", "opened"),
    [
        dash.dependencies.Input("modal-demo-button", "n_clicks"),
        dash.dependencies.Input("modal-close-button", "n_clicks"),
        dash.dependencies.Input("modal-submit-button", "n_clicks"),
        dash.dependencies.State("modal-simple", "opened"),
    ],
    prevent_initial_call=True,
)
def modal_demo(*args, **kwargs):
    opened = args[3]
    return not opened


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
    kkm = [k.replace("_", " ").title() for k in kkm]
    threshold_control = [
        dmc.AccordionItem(
            [
                make_control(
                    key,
                    f"action-{i}",
                ),
                dmc.AccordionPanel(
                    [
                        dmc.Fieldset(
                            [
                                dmc.NumberInput(
                                    label="Upper Limit",
                                    placeholder="Enter upper limit",
                                ),
                                dmc.NumberInput(
                                    label="Lower Limit",
                                    placeholder="Enter lower limit",
                                ),
                            ],
                            legend=key,
                            variant="filled",
                            radius="md",
                        )
                    ]
                ),
            ],
            value=f"item-{i}",
        )
        for i, key in enumerate(kkm)
    ]
    return threshold_control


@dash_app_project.expanded_callback(
    dash.dependencies.Output("notifications-container", "children"),
    [dash.dependencies.Input("notify", "n_clicks")],
    prevent_initial_call=True,
)
def show(*args, **kwargs):
    n_clicks = args[0]
    return dmc.Notification(
        title="Hey there!",
        id="simple-notify",
        action="show",
        message="Notifications in Dash, Awesome!",
        icon=DashIconify(icon="ic:round-celebration"),
    )
