import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from microscopemetrics_schema import datamodel as mm_schema
from OMERO_metrics.tools import dash_forms_tools as dft
from time import sleep
from microscopemetrics.analyses import field_illumination, psf_beads
from OMERO_metrics.views import run_analysis_view

DATASET_TO_ANALYSIS = {
    "FieldIlluminationDataset": field_illumination.analyse_field_illumination,
    "PSFBeadsDataset": psf_beads.analyse_psf_beads,
}


def get_icon(icon):
    return DashIconify(icon=icon, height=20)


min_step = 0
max_step = 2
active = 0


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
dashboard_name = "omero_dataset_form"
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
                                                html.Div(
                                                    id="sample_container"
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
                                    label="Second step: Input Data",
                                    description="Select input data",
                                    children=[
                                        dmc.Stack(
                                            [
                                                dmc.Text(
                                                    "Step 2 Input Data: Select the input data for the analysis",
                                                ),
                                                dmc.Grid(
                                                    [
                                                        dmc.GridCol(
                                                            html.Div(
                                                                [
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
                                                                    dmc.Textarea(
                                                                        id="comment",
                                                                        label="Comment",
                                                                        placeholder="Add a comment",
                                                                        w=300,
                                                                        autosize=True,
                                                                        minRows=2,
                                                                    ),
                                                                ],
                                                                style={
                                                                    "border-radius": "0.5rem",
                                                                    "border": "1px solid #189A35",
                                                                    "padding": "10px",
                                                                },
                                                            ),
                                                            span="auto",
                                                        ),
                                                        dmc.GridCol(
                                                            [
                                                                html.Div(
                                                                    id="setup-text",
                                                                ),
                                                            ],
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
                                        )
                                    ],
                                ),
                                dmc.StepperCompleted(
                                    children=dmc.Stack(
                                        [
                                            dmc.Text(
                                                "Step 3 Review: take a look at the data you have entered",
                                            ),
                                            html.Div(id="review-form"),
                                            dmc.Grid(
                                                [
                                                    dmc.GridCol(
                                                        id="sample_col",
                                                        span="auto",
                                                    ),
                                                    dmc.GridCol(
                                                        id="config_col",
                                                        span="auto",
                                                    ),
                                                    dmc.GridCol(
                                                        id="image_id",
                                                        span="auto",
                                                    ),
                                                ],
                                                justify="space-around",
                                            ),
                                        ]
                                    ),
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
    dash.dependencies.Output("output-data-upload", "children"),
    [
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("framework-multi-select", "value"),
        # dash.dependencies.State("form_content", "children"),
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
    input_parameters_object = getattr(mm_schema, input_parameters["type"])
    mm_input_parameters = input_parameters_object(**input_parameters["fields"])
    # form_content = args[1]
    sample_object = getattr(mm_schema, sample["type"])
    print(f"Comment object: {args[3]}")
    # sample_ex = dft.extract_form_data(form_content, sample_object.__class__.__name__)
    mm_sample = sample_object(**sample["fields"])
    current = args[2]
    if current == 2:
        sleep(3)
        msg, color = run_analysis_view(
            request=kwargs["request"],
            dataset_id=dataset_id,
            mm_sample=mm_sample,
            list_images=list_images,
            mm_input_parameters=mm_input_parameters,
            comment=args[3],
        )
        return dmc.Alert(msg, color=color, title="Analysis Results")
    else:
        return dash.no_update


#
# @dash_form_project.expanded_callback(
#
# )
# def update_next_button(*args, **kwargs):
#     return dmc.Button("Next step", id="next-basic-usage")
