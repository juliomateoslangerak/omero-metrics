import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from microscopemetrics_schema import datamodel as mm_schema
from OMERO_metrics.tools import dash_forms_tools as dft
from time import sleep
from microscopemetrics.samples import field_illumination, psf_beads
from OMERO_metrics.views import run_analysis_view

DATASET_TO_ANALYSIS = {
    "FieldIlluminationDataset": field_illumination.analise_field_illumination,
    "PSFBeadsDataset": psf_beads.analyse_psf_beads,
}


def get_icon(icon):
    return DashIconify(icon=icon, height=20)


min_step = 0
max_step = 3
active = 0

formManager = dft.dashForm(
    mm_schema.Sample, disabled=False, form_id="form_content"
)
sampleFORM = formManager.form

ALLOWED_ANALYSIS_TYPES = [
    "FieldIlluminationInputParameters",
    "PSFBeadsInputParameters",
]


primary_color = "#008080"

external_scripts = [
    # add the tailwind cdn url hosting the files with the utility classes
    {"src": "https://cdn.tailwindcss.com"}
]
stylesheets = [
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
    "./assets/omero_metrics.css",
]
dashboard_name = "omero_dataset_form"
dash_form_project = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=stylesheets,
    external_scripts=external_scripts,
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
                                    src="./assets/images/logo.png",
                                    style={"width": "100px"},
                                ),
                                dmc.Title(
                                    "Running an Analysis",
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
                        dmc.Stepper(
                            id="stepper-basic-usage",
                            mt="20",
                            ml="15",
                            active=active,
                            color="#189A35",
                            children=[
                                dmc.StepperStep(
                                    id="step_sample",
                                    label="First step: Sample Form",
                                    description="Create a sample",
                                    children=[
                                        dmc.Stack(
                                            children=[
                                                dmc.Text(
                                                    "Step 1 Sample: Create a Sample",
                                                    ta="center",
                                                ),
                                                html.Br(),
                                                sampleFORM,
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
                                    label="Second step: Input Data",
                                    description="Select input data",
                                    children=[
                                        dmc.Stack(
                                            [
                                                dmc.Text(
                                                    "Step 2 Input Data: Select the input data for the analysis",
                                                ),
                                                dmc.Divider(
                                                    label="Input data",
                                                    color="#189A35",
                                                    labelPosition="left",
                                                    size=10,
                                                ),
                                                dmc.MultiSelect(
                                                    label="Select Images to process",
                                                    placeholder="Select images",
                                                    id="framework-multi-select",
                                                    w="300",
                                                    mb=10,
                                                    leftSection=DashIconify(
                                                        icon="material-symbols-light:image"
                                                    ),
                                                    rightSection=DashIconify(
                                                        icon="radix-icons:chevron-down"
                                                    ),
                                                ),
                                                dmc.Divider(
                                                    label="Input Parameters from the config file",
                                                    color="#189A35",
                                                    labelPosition="left",
                                                    size=10,
                                                ),
                                                html.Div(
                                                    id="setup-text",
                                                ),
                                            ],
                                            align="flex-start",
                                            style={
                                                "background-color": "white",
                                                "border-radius": "0.5rem",
                                                "padding": "10px",
                                            },
                                        )
                                    ],
                                ),
                                dmc.StepperStep(
                                    id="step_review",
                                    label="Review",
                                    description="Get full access",
                                    children=dmc.Stack(
                                        [
                                            dmc.Text(
                                                "Step 3 Review: take a look at the data you have entered",
                                            ),
                                            html.Div(id="review-form"),
                                            dmc.Grid(
                                                [
                                                    dmc.GridCol(
                                                        id="sample_col", span=4
                                                    ),
                                                    dmc.GridCol(
                                                        id="config_col", span=4
                                                    ),
                                                    dmc.GridCol(
                                                        id="image_id", span=4
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                ),
                                dmc.StepperCompleted(
                                    children=[
                                        dmc.Text(
                                            "Please click on the button to run the analysis",
                                            ta="center",
                                            mt="20",
                                            mb="20",
                                        ),
                                        dmc.Center(
                                            id="analysis_progress",
                                            children=[
                                                dmc.Button(
                                                    id="run_analysis",
                                                    children="Run Analysis",
                                                    color="green",
                                                    size="lg",
                                                )
                                            ],
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
                                    variant="default",
                                ),
                                dmc.Button("Next step", id="next-basic-usage"),
                            ],
                        ),
                    ],
                    style={
                        "margin-top": 10,
                        "background-color": "white",
                        "border-radius": "0.5rem",
                        "padding": "10px",
                    },
                ),
                html.Div(id="blank"),
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
    dash.dependencies.Output("setup-text", "children"),
    [dash.dependencies.Input("blank", "children")],
)
def update_setup(*args, **kwargs):
    input_parameters = kwargs["session_state"]["context"]["input_parameters"]
    input_parameters_object = getattr(
        mm_schema, input_parameters["analyse_type"]
    )
    input_parameters_mm = input_parameters_object(
        **input_parameters["input_parameters"]
    )
    form = dft.dashForm(
        input_parameters_mm, disabled=True, form_id="input_parameters_form"
    )
    return form.form


@dash_form_project.expanded_callback(
    dash.dependencies.Output("framework-multi-select", "data"),
    dash.dependencies.Output("framework-multi-select", "value"),
    [dash.dependencies.Input("blank", "children")],
)
def list_images_multi_selector(*args, **kwargs):
    list_images = kwargs["session_state"]["context"]["list_images"]
    return list_images, [list_images[0]["value"]]


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
        dash.dependencies.State("form_content", "children"),
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
    [
        dash.dependencies.Input("back-basic-usage", "n_clicks"),
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("framework-multi-select", "value"),
        dash.dependencies.State("stepper-basic-usage", "active"),
        dash.dependencies.State("form_content", "children"),
    ],
    prevent_initial_call=True,
)
def stepper_callback(*args, **kwargs):
    current = args[3]
    multi_selector = args[2]
    button_id = kwargs["callback_context"].triggered[0]["prop_id"]
    step = current if current is not None else active
    if button_id == "back-basic-usage.n_clicks":
        step = step - 1 if step > min_step else step
    else:
        if step == 0 and not dft.validate_form(args[4]):
            step = 0
        elif step == 1 and len(multi_selector) < 1:
            step = 1
        else:
            step = step + 1 if step < max_step else step
    return step


dash_form_project.clientside_callback(
    """
    function updateLoadingState(n_clicks) {
        return [true, []];
    }
    """,
    dash.dependencies.Output("run_analysis", "loading", allow_duplicate=True),
    dash.dependencies.Output("group_buttons", "children"),
    dash.dependencies.Input("run_analysis", "n_clicks"),
    prevent_initial_call=True,
)


@dash_form_project.expanded_callback(
    dash.dependencies.Output("analysis_progress", "children"),
    [
        dash.dependencies.Input("run_analysis", "n_clicks"),
        dash.dependencies.State("framework-multi-select", "value"),
        dash.dependencies.State("form_content", "children"),
        dash.dependencies.State("stepper-basic-usage", "active"),
    ],
    prevent_initial_call=True,
)
def run_analysis(*args, **kwargs):
    input_parameters = kwargs["session_state"]["context"]["input_parameters"]
    dataset_id = kwargs["session_state"]["context"]["dataset_id"]
    list_images = args[1]
    input_parameters_object = getattr(
        mm_schema, input_parameters["analyse_type"]
    )
    mm_input_parameters = input_parameters_object(
        **input_parameters["input_parameters"]
    )
    form_content = args[2]
    sample = dft.extract_form_data(form_content)
    mm_sample = mm_schema.Sample(**sample)
    current = args[3]
    if current == 3:
        sleep(3)
        msg, color = run_analysis_view(
            request=kwargs["request"],
            dataset_id=dataset_id,
            mm_sample=mm_sample,
            list_images=list_images,
            mm_input_parameters=mm_input_parameters,
        )
        return dmc.Alert(msg, color=color)
    else:
        return dash.no_update
