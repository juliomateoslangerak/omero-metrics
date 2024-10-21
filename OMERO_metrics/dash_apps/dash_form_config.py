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

sample_types = [x[0] for x in MAPPINGS]
sample_types_dp = [
    {"label": dft.add_space_between_capitals(x.__name__), "value": f"{i}"}
    for i, x in enumerate(sample_types)
]


def get_icon(icon):
    return DashIconify(icon=icon, height=20)


min_step = 0
max_step = 2
active = 0

formManager = dft.DashForm(
    mm_schema.Sample, disabled=False, form_id="form_content"
)
sampleFORM = formManager.form

ALLOWED_ANALYSIS_TYPES = [
    "FieldIlluminationInputParameters",
    "PSFBeadsInputParameters",
]


primary_color = "#008080"


stylesheets = [
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
]
dashboard_name = "omero_project_config_form"
dash_form_project = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=stylesheets,
)

analysis_types = [
    {"label": field.__name__, "value": f"{i}"}
    for i, field in enumerate(
        mm_schema.MetricsInputParameters.__subclasses__()
    )
]


dash_form_project.layout = dmc.MantineProvider(
    [
        dmc.Container(
            [
                dmc.Center(
                    [
                        dmc.Group(
                            [
                                html.Img(
                                    src="assets/images/metrics_logo.png",
                                    style={"width": "100px"},
                                ),
                                dmc.Title(
                                    "Configuration Set Up",
                                    c="#189A35",
                                    size="h3",
                                    mb=10,
                                    mt=5,
                                ),
                            ]
                        ),
                    ],
                    style={
                        "background-color": "white",
                        "border-radius": "0.5rem",
                        "padding": "10px",
                    },
                ),
                html.Div(
                    id="output-data-upload",
                    children=[
                        dmc.LoadingOverlay(
                            visible=False,
                            id="loading-overlay",
                            overlayProps={"radius": "sm", "blur": 2},
                            zIndex=10,
                        ),
                        dmc.Stepper(
                            id="stepper-basic-usage",
                            mt="20",
                            ml="15",
                            active=active,
                            color="#189A35",
                            children=[
                                dmc.StepperStep(
                                    id="step_sample",
                                    label="Sample Form",
                                    description="Create a sample",
                                    children=[
                                        dmc.Stack(
                                            children=[
                                                dmc.Text(
                                                    "Step 1 Sample: Select your sample type",
                                                    ta="center",
                                                ),
                                                html.Br(),
                                                dmc.Select(
                                                    id="sample_type_selector",
                                                    data=sample_types_dp,
                                                    w=300,
                                                    searchable=True,
                                                    placeholder="Select Sample Type",
                                                    clearable=False,
                                                ),
                                                html.Div(
                                                    id="sample_container",
                                                ),
                                            ],
                                            align="center",
                                            style={
                                                "background-color": "white",
                                                "border-radius": "0.5rem",
                                                "padding": "10px",
                                            },
                                        )
                                    ],
                                ),
                                dmc.StepperStep(
                                    id="step_input_data",
                                    label="Input Parameters",
                                    description="Configure the input parameters",
                                    children=[
                                        dmc.Stack(
                                            [
                                                dmc.Text(
                                                    "Step 2 Input Parameters: Fill in the input parameters for your analysis",
                                                ),
                                                html.Div(
                                                    id="input_parameters_container",
                                                ),
                                            ],
                                            align="center",
                                            style={
                                                "background-color": "white",
                                                "border-radius": "0.5rem",
                                                "padding": "10px",
                                            },
                                        )
                                    ],
                                ),
                                dmc.StepperCompleted(
                                    children=[
                                        dmc.Text(
                                            "Review the configuration and save it",
                                            ta="center",
                                            mt="20",
                                            mb="20",
                                        ),
                                        dmc.Stack(
                                            id="save_progress",
                                            children=[
                                                dmc.Grid(
                                                    [
                                                        dmc.GridCol(
                                                            id="sample_col",
                                                            span="auto",
                                                        ),
                                                        dmc.GridCol(
                                                            id="input_col",
                                                            span="auto",
                                                        ),
                                                    ],
                                                    justify="space-around",
                                                ),
                                            ],
                                            align="center",
                                            style={
                                                "background-color": "white",
                                                "border-radius": "0.5rem",
                                                "padding": "10px",
                                            },
                                        ),
                                    ]
                                ),
                            ],
                            styles={
                                "separator": {"border-color": "#189A35"},
                                "verticalSeparator": {
                                    "border-color": "#189A35"
                                },
                            },
                        ),
                        dmc.Group(
                            id="group_buttons",
                            justify="center",
                            mt="xl",
                            children=[
                                dmc.Button(
                                    "Back",
                                    id="back-basic-usage",
                                    # variant="default",
                                ),
                                dmc.Button("Next", id="next-basic-usage"),
                            ],
                        ),
                    ],
                    style={
                        "margin-top": 10,
                        "background-color": "white",
                        "border-radius": "0.5rem",
                        "padding": "10px",
                        "border": "1px solid #189A35",
                    },
                ),
            ],
            fluid=True,
            style={
                "background-color": "#eceff1",
                "margin": "10px",
                "border-radius": "0.5rem",
                "padding": "10px",
            },
        ),
    ]
)


@dash_form_project.expanded_callback(
    dash.dependencies.Output("stepper-basic-usage", "active"),
    dash.dependencies.Output("next-basic-usage", "children"),
    dash.dependencies.Output("next-basic-usage", "color"),
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
    step = current if current is not None else active
    next_text = "Next"
    next_color = "blue"
    if button_id == "back-basic-usage.n_clicks":
        step = step - 1 if step > min_step else step
    else:
        sample = args[3]
        input_parameters = args[4]
        if step == 0 and not dft.validate_form(sample):
            step = 0
        elif step == 1 and not dft.validate_form(input_parameters):
            step = 1
        else:
            if step >= 1:
                next_text = "Save Configuration"
                next_color = "green"
            step = step + 1 if step < max_step else step
    return step, next_text, next_color


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
    dash.dependencies.Output("output-data-upload", "children"),
    dash.dependencies.Output("loading-overlay", "loading"),
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
            input_parameters = dft.extract_form_data(
                input_form, mm_input_parameters.__class__.__name__
            )
            mm_input_parameters = mm_input_parameters(**input_parameters)
            sample = dft.extract_form_data(
                sample_form, mm_sample.__class__.__name__
            )
            mm_sample = mm_sample(**sample)
            response, color = views.save_config(
                request=request,
                project_id=int(project_id),
                input_parameters=mm_input_parameters,
                sample=mm_sample,
            )
            return [dmc.Alert(response, color=color, title="Feedback!")], False
        else:
            return dash.no_update, False
    else:
        dash.no_update, False
