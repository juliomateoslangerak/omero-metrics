import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from microscopemetrics.analyses.mappings import MAPPINGS
from microscopemetrics_schema import datamodel as mm_schema
from OMERO_metrics.tools import dash_forms_tools as dft
from time import sleep
import OMERO_metrics.views as views

DATASET_TO_INPUT = {
    "FieldIlluminationDataset": mm_schema.FieldIlluminationInputParameters,
    "PSFBeadsDataset": mm_schema.PSFBeadsInputParameters,
}

# Improved sample type formatting
sample_types = [x[0] for x in MAPPINGS]
sample_types_dp = [
    {
        "label": dft.add_space_between_capitals(x.__name__),
        "value": f"{i}",
        "description": f"Configure analysis for {x.__name__}",  # Added descriptions
    }
    for i, x in enumerate(sample_types)
]


def get_icon(icon):
    return DashIconify(icon=icon, height=20)


# Theme configuration
THEME = {
    "primary": "#189A35",
    "secondary": "#008080",
    "background": "#f8fafc",
    "surface": "#ffffff",
    "border": "#e2e8f0",
    "success": "#10b981",
    "error": "#ef4444",
    "text": {
        "primary": "#2C3E50",
        "secondary": "#6c757d",
    },
}

dashboard_name = "omero_project_config_form"
dash_form_project = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=dmc.styles.ALL,
)

# Improved layout with better visual hierarchy
dash_form_project.layout = dmc.MantineProvider(
    theme={
        "colorScheme": "light",
        "primaryColor": "green",
        "components": {
            "Button": {"styles": {"root": {"fontWeight": 500}}},
            "Title": {"styles": {"root": {"letterSpacing": "-0.5px"}}},
        },
    },
    children=[
        dmc.Container(
            [
                # Header Section
                dmc.Paper(
                    shadow="sm",
                    p="md",
                    radius="lg",
                    mb="md",
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
                                                    "Configuration Setup",
                                                    c=THEME["primary"],
                                                    size="h2",
                                                ),
                                                dmc.Text(
                                                    "Configure your sample type and input parameters",
                                                    c=THEME["text"][
                                                        "secondary"
                                                    ],
                                                    size="sm",
                                                ),
                                            ],
                                            gap="xs",
                                        ),
                                    ],
                                ),
                                dmc.Badge(
                                    "Analysis Form",
                                    color="green",
                                    variant="dot",
                                    size="lg",
                                ),
                            ],
                            justify="space-between",
                        ),
                    ],
                ),
                # Main Content
                dmc.Paper(
                    id="main-content",
                    children=[
                        dmc.LoadingOverlay(
                            id="loading-overlay",
                            overlayProps={"radius": "sm", "blur": 2},
                        ),
                        # Progress Indicator
                        dmc.Progress(
                            id="progress-bar",
                            value=0,
                            color=THEME["primary"],
                            size="sm",
                            mb="md",
                        ),
                        # Stepper
                        dmc.Stepper(
                            id="stepper-basic-usage",
                            active=0,
                            color=THEME["primary"],
                            size="sm",
                            iconSize=32,
                            children=[
                                dmc.StepperStep(
                                    id="step_sample",
                                    label="Sample Configuration",
                                    description="Define your sample parameters",
                                    icon=DashIconify(
                                        icon="mdi:microscope", width=20
                                    ),
                                    children=[
                                        dmc.Paper(
                                            children=[
                                                dmc.Title(
                                                    "Sample Configuration",
                                                    order=3,
                                                ),
                                                dmc.Text(
                                                    "Select your sample type and configure its parameters",
                                                    c="dimmed",
                                                    size="sm",
                                                ),
                                                dmc.Select(
                                                    id="sample_type_selector",
                                                    data=sample_types_dp,
                                                    searchable=True,
                                                    placeholder="Select Sample Type",
                                                    leftSection=DashIconify(
                                                        icon="mdi:database-search"
                                                    ),
                                                    allowDeselect=False,
                                                    size="md",
                                                    mb=10,
                                                    styles={
                                                        "input": {
                                                            "border": f"1px solid {THEME['border']}"
                                                        }
                                                    },
                                                ),
                                                html.Div(
                                                    id="sample_container"
                                                ),
                                            ],
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                        )
                                    ],
                                ),
                                dmc.StepperStep(
                                    id="step_input_data",
                                    label="Analysis Parameters",
                                    description="Set analysis configuration",
                                    icon=DashIconify(
                                        icon="mdi:tune-vertical", width=20
                                    ),
                                    children=[
                                        dmc.Paper(
                                            children=[
                                                dmc.Title(
                                                    "Analysis Parameters",
                                                    order=3,
                                                ),
                                                dmc.Text(
                                                    "Configure the input parameters for your analysis",
                                                    c="dimmed",
                                                    size="sm",
                                                    mb=10,
                                                ),
                                                html.Div(
                                                    id="input_parameters_container"
                                                ),
                                            ],
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                        )
                                    ],
                                ),
                                dmc.StepperCompleted(
                                    children=[
                                        dmc.Paper(
                                            children=[
                                                dmc.Title(
                                                    "Review Configuration",
                                                    order=3,
                                                ),
                                                dmc.Text(
                                                    "Review your configuration before saving",
                                                    c="dimmed",
                                                    size="sm",
                                                ),
                                                dmc.Grid(
                                                    children=[
                                                        dmc.GridCol(
                                                            dmc.Paper(
                                                                children=[
                                                                    dmc.Title(
                                                                        "Sample Details",
                                                                        order=4,
                                                                    ),
                                                                    html.Div(
                                                                        id="sample_col"
                                                                    ),
                                                                ],
                                                                p="md",
                                                                withBorder=True,
                                                                radius="md",
                                                            ),
                                                            span=6,
                                                        ),
                                                        dmc.GridCol(
                                                            dmc.Paper(
                                                                children=[
                                                                    dmc.Title(
                                                                        "Input Parameters",
                                                                        order=4,
                                                                    ),
                                                                    html.Div(
                                                                        id="input_col"
                                                                    ),
                                                                ],
                                                                p="md",
                                                                withBorder=True,
                                                                radius="md",
                                                            ),
                                                            span=6,
                                                        ),
                                                    ],
                                                    gutter="xl",
                                                ),
                                            ],
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                        ),
                                    ]
                                ),
                            ],
                        ),
                        # Navigation Buttons
                        dmc.Group(
                            children=[
                                dmc.Button(
                                    "Back",
                                    id="back-basic-usage",
                                    variant="outline",
                                    leftSection=DashIconify(
                                        icon="mdi:arrow-left"
                                    ),
                                ),
                                dmc.Button(
                                    "Next",
                                    id="next-basic-usage",
                                    rightSection=DashIconify(
                                        icon="mdi:arrow-right"
                                    ),
                                ),
                            ],
                            justify="space-between",
                            mt="xl",
                        ),
                    ],
                    p="xl",
                    radius="md",
                    withBorder=True,
                    mt="md",
                    shadow="xs",
                    style={"backgroundColor": "white"},
                ),
            ],
            size="xl",
            px="md",
            py="xl",
        ),
    ],
)


# Updated callback for stepper progress
@dash_form_project.expanded_callback(
    [
        dash.dependencies.Output("stepper-basic-usage", "active"),
        dash.dependencies.Output("next-basic-usage", "children"),
        dash.dependencies.Output("next-basic-usage", "color"),
        dash.dependencies.Output("progress-bar", "value"),
        dash.dependencies.Output("next-basic-usage", "rightSection"),
    ],
    [
        dash.dependencies.Input("back-basic-usage", "n_clicks"),
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("stepper-basic-usage", "active"),
        dash.dependencies.State("sample_content", "children"),
        dash.dependencies.State("input_content", "children"),
    ],
    prevent_initial_call=True,
)
def stepper_callback(*args, **kwargs):
    current = args[2]
    button_id = kwargs["callback_context"].triggered[0]["prop_id"]
    step = current if current is not None else 0

    # Calculate progress percentage
    progress = (step / 2) * 100

    if button_id == "back-basic-usage.n_clicks":
        step = max(0, step - 1)
        next_text = ["Next"]
        next_icon = DashIconify(icon="mdi:arrow-right")
        next_color = THEME["primary"]
    else:
        sample = args[3]
        input_parameters = args[4]

        if step == 0 and not dft.validate_form(sample):
            return dash.no_update, dash.no_update, dash.no_update, progress
        elif step == 1 and not dft.validate_form(input_parameters):
            return dash.no_update, dash.no_update, dash.no_update, progress

        step = min(2, step + 1)

        if step == 2:
            next_text = ["Save Configuration"]
            next_icon = DashIconify(icon="mdi:check")
            next_color = THEME["primary"]
        else:
            next_text = ["Next"]
            next_color = THEME["primary"]
            next_icon = DashIconify(icon="mdi:arrow-right")

    progress = (step / 2) * 100
    return step, next_text, next_color, progress, next_icon


@dash_form_project.expanded_callback(
    dash.dependencies.Output("sample_container", "children"),
    [
        dash.dependencies.Input("sample_type_selector", "value"),
    ],
    prevent_initial_call=True,
)
def update_sample_container(*args, **kwargs):
    mm_sample = MAPPINGS[int(args[0])][0]
    form_manager = dft.DashForm(
        mm_sample, disabled=False, form_id="sample_content"
    )
    sample_form = form_manager.form
    return [sample_form]


@dash_form_project.expanded_callback(
    dash.dependencies.Output("input_parameters_container", "children"),
    [
        dash.dependencies.Input("sample_type_selector", "value"),
    ],
    prevent_initial_call=True,
)
def update_input_parameters(*args, **kwargs):
    analysis_type = MAPPINGS[int(args[0])][2].__name__
    mm_input_parameters = DATASET_TO_INPUT[analysis_type]
    form_manager = dft.DashForm(
        mm_input_parameters, disabled=False, form_id="input_content"
    )
    mm_input_parameters = form_manager.form
    return [mm_input_parameters]


@dash_form_project.expanded_callback(
    dash.dependencies.Output("sample_col", "children"),
    dash.dependencies.Output("input_col", "children"),
    [
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("sample_content", "children"),
        dash.dependencies.State("input_content", "children"),
        dash.dependencies.State("stepper-basic-usage", "active"),
    ],
    prevent_initial_call=True,
)
def review_configuration(*args, **kwargs):
    sample = dft.disable_all_fields_dash_form(args[1])
    input_parameters = dft.disable_all_fields_dash_form(args[2])
    current = args[3]
    if current == 1:
        return sample, input_parameters
    else:
        return dash.no_update


dash_form_project.clientside_callback(
    """
    function updateLoadingState(n_clicks, current) {
    if (current == 2) {
        return true}
    else {
        return false}
    }
    """,
    dash.dependencies.Output(
        "loading-overlay", "visible", allow_duplicate=True
    ),
    dash.dependencies.Input("next-basic-usage", "n_clicks"),
    dash.dependencies.State("stepper-basic-usage", "active"),
    prevent_initial_call=True,
)


@dash_form_project.expanded_callback(
    dash.dependencies.Output("main-content", "children"),
    dash.dependencies.Output("loading-overlay", "visible"),
    [
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("sample_content", "children"),
        dash.dependencies.State("input_content", "children"),
        dash.dependencies.State("stepper-basic-usage", "active"),
        dash.dependencies.State("sample_type_selector", "value"),
    ],
    prevent_initial_call=True,
)
def save_config_dash(*args, **kwargs):
    current = args[3]
    if not args[4]:  # No sample type selected
        return dash.no_update, False

    analysis_type = MAPPINGS[int(args[4])][2].__name__
    mm_sample = MAPPINGS[int(args[4])][0]
    mm_input_parameters = DATASET_TO_INPUT[analysis_type]
    sample_form = args[1]
    input_form = args[2]
    project_id = int(kwargs["session_state"]["context"]["project_id"])
    request = kwargs["request"]

    if args[0] > 0 and current == 2:
        if dft.validate_form(sample_form) and dft.validate_form(input_form):
            sleep(2)
            try:
                input_parameters = dft.extract_form_data(
                    input_form, mm_input_parameters.class_name
                )
                mm_input_parameters = mm_input_parameters(**input_parameters)
                sample = dft.extract_form_data(
                    sample_form, mm_sample.class_name
                )
                mm_sample = mm_sample(**sample)
                response, color = views.save_config(
                    request=request,
                    project_id=int(project_id),
                    input_parameters=mm_input_parameters,
                    sample=mm_sample,
                )
                return [
                    dmc.Alert(
                        children=[
                            dmc.Title(response, order=4),
                            dmc.Text(
                                "Your configuration has been saved successfully.",
                                size="sm",
                            ),
                        ],
                        color=color,
                        icon=DashIconify(icon="mdi:check-circle"),
                        title="Success!",
                        radius="md",
                        withCloseButton=True,
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
                    )
                ], False
    return dash.no_update, False
