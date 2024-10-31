import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from microscopemetrics_schema import datamodel as mm_schema
from OMERO_metrics.tools import dash_forms_tools as dft
from time import sleep
from OMERO_metrics.views import run_analysis_view

# Theme Configuration
THEME = {
    "primary": "#189A35",
    "secondary": "#63aa47",
    "background": "#ffffff",
    "surface": "#f8f9fa",
    "border": "#e9ecef",
    "text": {
        "primary": "#2C3E50",
        "secondary": "#6c757d",
    },
}
# Constants and theme configuration
THEME_COLOR = "#189A35"
SECONDARY_COLOR = "#008080"
ERROR_COLOR = "#FF4136"
SUCCESS_COLOR = "#2ECC40"
active = 0
min_step = 0
max_step = 2


def get_icon(icon, size=20, color=None):
    return DashIconify(icon=icon, height=size, color=color)


# Initialize dashboard
dashboard_name = "omero_dataset_form"
dash_form_project = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=dmc.styles.ALL,
)

# Layout configuration
dash_form_project.layout = dmc.MantineProvider(
    theme={
        "colorScheme": "light",
        "primaryColor": "green",
        "components": {
            "Button": {"styles": {"root": {"fontWeight": 500}}},
            "Alert": {"styles": {"root": {"borderRadius": "8px"}}},
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
                                                    "Analysis Dashboard",
                                                    c=THEME["primary"],
                                                    size="h2",
                                                ),
                                                dmc.Text(
                                                    "Configure and run your analysis",
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
                # Main content
                dmc.Paper(
                    id="main-content",
                    shadow="xs",
                    p="xl",
                    mt="md",
                    radius="md",
                    style={"backgroundColor": "white"},
                    children=[
                        # Progress indicator
                        dmc.Progress(
                            id="analysis-progress",
                            value=0,
                            color=THEME_COLOR,
                            radius="xl",
                            size="sm",
                            mb="xl",
                        ),
                        # Stepper
                        dmc.Stepper(
                            id="stepper-basic-usage",
                            active=0,
                            color=THEME_COLOR,
                            size="sm",
                            iconSize=32,
                            children=[
                                dmc.StepperStep(
                                    id="step_sample",
                                    label="Sample Configuration",
                                    description="Define sample parameters",
                                    icon=get_icon(
                                        "material-symbols:science-outline"
                                    ),
                                    children=[
                                        dmc.Paper(
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                            children=[
                                                dmc.Text(
                                                    "Sample Configuration",
                                                    size="lg",
                                                    fw=500,
                                                    mb="md",
                                                ),
                                                html.Div(
                                                    id="sample_container"
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                dmc.StepperStep(
                                    id="step_input_data",
                                    label="Data Selection",
                                    description="Choose input images",
                                    icon=get_icon(
                                        "material-symbols:image-search"
                                    ),
                                    children=[
                                        dmc.Paper(
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                            children=[
                                                dmc.Grid(
                                                    [
                                                        dmc.GridCol(
                                                            [
                                                                dmc.Stack(
                                                                    [
                                                                        dmc.MultiSelect(
                                                                            label="Select Images",
                                                                            placeholder="Choose images to process",
                                                                            id="framework-multi-select",
                                                                            clearable=True,
                                                                            searchable=True,
                                                                            leftSection=get_icon(
                                                                                "material-symbols-light:image"
                                                                            ),
                                                                            styles={
                                                                                "input": {
                                                                                    "borderColor": THEME_COLOR
                                                                                }
                                                                            },
                                                                        ),
                                                                        dmc.Textarea(
                                                                            id="comment",
                                                                            label="Analysis Notes",
                                                                            placeholder="Add analysis comments or notes...",
                                                                            autosize=True,
                                                                            minRows=3,
                                                                            styles={
                                                                                "input": {
                                                                                    "borderColor": THEME_COLOR
                                                                                }
                                                                            },
                                                                        ),
                                                                    ],
                                                                    gap="md",
                                                                ),
                                                            ],
                                                            span=6,
                                                        ),
                                                        dmc.GridCol(
                                                            [
                                                                dmc.Paper(
                                                                    withBorder=True,
                                                                    p="md",
                                                                    radius="md",
                                                                    children=[
                                                                        dmc.Text(
                                                                            "Configuration Preview",
                                                                            fw=500,
                                                                            mb="md",
                                                                        ),
                                                                        html.Div(
                                                                            id="setup-text"
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                            span=6,
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                dmc.StepperCompleted(
                                    children=dmc.Paper(
                                        p="md",
                                        radius="md",
                                        withBorder=True,
                                        children=[
                                            dmc.Stack(
                                                [
                                                    dmc.Text(
                                                        "Review Configuration",
                                                        size="lg",
                                                        fw=500,
                                                    ),
                                                    dmc.Grid(
                                                        [
                                                            dmc.GridCol(
                                                                id="sample_col",
                                                                span=4,
                                                            ),
                                                            dmc.GridCol(
                                                                id="config_col",
                                                                span=4,
                                                            ),
                                                            dmc.GridCol(
                                                                id="image_id",
                                                                span=4,
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                                gap="xl",
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                        # Navigation buttons
                        dmc.Group(
                            [
                                dmc.Button(
                                    "Back",
                                    id="back-basic-usage",
                                    variant="outline",
                                    leftSection=get_icon(
                                        "material-symbols:arrow-back"
                                    ),
                                    color=SECONDARY_COLOR,
                                ),
                                dmc.Button(
                                    "Next",
                                    id="next-basic-usage",
                                    rightSection=get_icon(
                                        "material-symbols:arrow-forward"
                                    ),
                                    color=THEME_COLOR,
                                ),
                            ],
                            justify="space-between",
                            mt="xl",
                        ),
                    ],
                ),
                # Results section
                html.Div(id="analysis-results"),
                # Hidden elements
                html.Div(id="blank"),
            ],
            size="xl",
            px="md",
            py="xl",
        ),
    ],
)


@dash_form_project.expanded_callback(
    dash.dependencies.Output("setup-text", "children"),
    [dash.dependencies.Input("blank", "children")],
)
def update_setup(*args, **kwargs):
    input_parameters = kwargs["session_state"]["context"]["input_parameters"][
        "input_parameters"
    ]
    input_parameters_object = getattr(mm_schema, input_parameters["type"])
    input_parameters_mm = input_parameters_object(**input_parameters["fields"])
    form = dft.DashForm(
        input_parameters_mm, disabled=True, form_id="input_parameters_form"
    )
    return form.form


@dash_form_project.expanded_callback(
    dash.dependencies.Output("sample_container", "children"),
    [dash.dependencies.Input("blank", "children")],
)
def update_sample(*args, **kwargs):
    sample = kwargs["session_state"]["context"]["input_parameters"]["sample"]
    mm_sample = getattr(mm_schema, sample["type"])
    mm_sample = mm_sample(**sample["fields"])
    form = dft.DashForm(mm_sample, disabled=True, form_id="sample_form")
    return form.form


@dash_form_project.expanded_callback(
    dash.dependencies.Output("framework-multi-select", "data"),
    dash.dependencies.Output("framework-multi-select", "value"),
    [dash.dependencies.Input("blank", "children")],
)
def list_images_multi_selector(*args, **kwargs):
    list_images = kwargs["session_state"]["context"]["list_images"]
    return list_images, [
        list_images[i]["value"] for i in range(len(list_images))
    ]


@dash_form_project.expanded_callback(
    dash.dependencies.Output("framework-multi-select", "error"),
    [dash.dependencies.Input("framework-multi-select", "value")],
)
def multi_selector_callback(*args, **kwargs):
    value = args[0]
    return "Select at least 1." if len(value) < 1 else ""


@dash_form_project.expanded_callback(
    dash.dependencies.Output("image_id", "children"),
    dash.dependencies.Output("sample_col", "children"),
    dash.dependencies.Output("config_col", "children"),
    [
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("sample_form", "children"),
        dash.dependencies.State("framework-multi-select", "value"),
        dash.dependencies.State("input_parameters_form", "children"),
        dash.dependencies.State("stepper-basic-usage", "active"),
    ],
)
def update_review_form(*args, **kwargs):
    form_content = args[1]
    multi_selector = args[2]
    current = args[4]
    input_parameters = args[3]
    selectors = dmc.MultiSelect(
        label="Images selected",
        data=[f"Image ID: {i}" for i in multi_selector],
        value=multi_selector,
        clearable=False,
        w="auto",
        disabled=True,
        leftSection=DashIconify(icon="material-symbols-light:image"),
        rightSection=DashIconify(icon="radix-icons:chevron-down"),
    )
    if current == 1:
        return (
            selectors,
            dft.disable_all_fields_dash_form(form_content),
            input_parameters,
        )
    else:
        return dash.no_update


# @dash_form_project.expanded_callback(
#     dash.dependencies.Output("step_sample", "progressIcon"),
#            dash.dependencies.Output("step_sample", "color"),
#     [
#         dash.dependencies.State("stepper-basic-usage", "active"),
#        dash.dependencies.State("form_content", "children"),
#        ],
# )
# def update_sample_icon(*args, **kwargs):
#     step = args[1]
#     form_content = args[2]
#     if step == 0 and dft.validate_form(form_content):
#         return get_icon(icon="mdi:cross-circle"), "red"
#     else:
#         return dash.no_update


@dash_form_project.expanded_callback(
    dash.dependencies.Output("stepper-basic-usage", "active"),
    dash.dependencies.Output("next-basic-usage", "children"),
    dash.dependencies.Output("next-basic-usage", "color"),
    [
        dash.dependencies.Input("back-basic-usage", "n_clicks"),
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("framework-multi-select", "value"),
        dash.dependencies.State("stepper-basic-usage", "active"),
        dash.dependencies.State("sample_form", "children"),
    ],
    prevent_initial_call=True,
)
def stepper_callback(*args, **kwargs):
    current = args[3]
    multi_selector = args[2]
    button_id = kwargs["callback_context"].triggered[0]["prop_id"]
    step = current if current is not None else active
    next_text = "Next"
    next_color = "blue"
    if button_id == "back-basic-usage.n_clicks":
        step = step - 1 if step > min_step else step
    else:
        if step == 0 and not dft.validate_form(args[4]):
            step = 0
        elif step == 1 and len(multi_selector) < 1:
            step = 1
        else:
            if step >= 1:
                next_text = "Run Analysis"
                next_color = "green"
            step = step + 1 if step < max_step else step
    return step, next_text, next_color


dash_form_project.clientside_callback(
    """
    function updateLoadingState(n_clicks, current) {
        if (current == 2) {
            return true
        } else {
            return false
        }
    }
    """,
    dash.dependencies.Output(
        "next-basic-usage", "loading", allow_duplicate=True
    ),
    dash.dependencies.Input("next-basic-usage", "n_clicks"),
    dash.dependencies.State("stepper-basic-usage", "active"),
    prevent_initial_call=True,
)


@dash_form_project.expanded_callback(
    dash.dependencies.Output("main-content", "children"),
    [
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("framework-multi-select", "value"),
        dash.dependencies.State("stepper-basic-usage", "active"),
        dash.dependencies.State("comment", "value"),
    ],
    prevent_initial_call=True,
)
def run_analysis(*args, **kwargs):
    config = kwargs["session_state"]["context"]["input_parameters"]
    input_parameters = config["input_parameters"]
    sample = config["sample"]
    dataset_id = kwargs["session_state"]["context"]["dataset_id"]
    list_images = args[1]
    current = args[2]

    if current == 2:
        sleep(1)  # Reduced sleep time for better UX
        try:
            input_parameters_object = getattr(
                mm_schema, input_parameters["type"]
            )
            mm_input_parameters = input_parameters_object(
                **input_parameters["fields"]
            )
            sample_object = getattr(mm_schema, sample["type"])
            mm_sample = sample_object(**sample["fields"])

            msg, color = run_analysis_view(
                request=kwargs["request"],
                dataset_id=dataset_id,
                mm_sample=mm_sample,
                list_images=list_images,
                mm_input_parameters=mm_input_parameters,
                comment=args[3],
            )

            return dmc.Alert(
                children=[
                    dmc.Title(
                        "Your analysis completed successfully!", order=4
                    ),
                    dmc.Text(
                        msg,
                        size="sm",
                    ),
                ],
                color=color,
                icon=DashIconify(icon="mdi:check-circle"),
                title="Success!",
                radius="md",
                withCloseButton=True,
            )
        except Exception as e:
            return dmc.Alert(
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
    return dash.no_update


dash_form_project.clientside_callback(
    """
    function updateProgress(active) {
        return active * 50;
    }
    """,
    dash.dependencies.Output("analysis-progress", "value"),
    dash.dependencies.Input("stepper-basic-usage", "active"),
)
