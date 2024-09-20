import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from microscopemetrics_schema import datamodel as mm_schema
from dataclasses import fields
from time import sleep
from OMERO_metrics.views import get_connection
from OMERO_metrics.tools import dash_forms_tools as dft

# ----------------------------------------------

min_step = 0
max_step = 3
active = 0

# ----------------------------------------------
formManager = dft.dashForm(mm_schema.Sample)
sampleFORM = formManager.form
# print(f'------------------------------------{sampleFORM}')
# ----------------------------------------------

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
                            active=active,
                            color="#189A35",
                            children=[
                                dmc.StepperStep(
                                    label="First step: Sample Form",
                                    description="Create a sample",
                                    children=[
                                        dmc.Stack(
                                            [
                                                dmc.Text(
                                                    "Step 1 content: Create a Sample",
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
                                    label="Second step: Input Data",
                                    description="Select input data",
                                    children=dmc.Text(
                                        "Step 2 content: Verify email",
                                        ta="center",
                                    ),
                                ),
                                dmc.StepperStep(
                                    label="Review",
                                    description="Get full access",
                                    children=dmc.Text(
                                        "Step 3 content: Get full access",
                                        ta="center",
                                    ),
                                ),
                                dmc.StepperCompleted(
                                    children=dmc.Text(
                                        "Completed, please wait while we process your images",
                                        ta="center",
                                    )
                                ),
                            ],
                        ),
                        dmc.Group(
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
            ],
            fluid=True,
            style={
                "background-color": "#eceff1",
                "margin": "20px",
                "border-radius": "0.5rem",
                "padding": "10px",
            },
        ),
    ]
)


@dash_form_project.expanded_callback(
    dash.dependencies.Output("stepper-basic-usage", "active"),
    dash.dependencies.Input("back-basic-usage", "n_clicks"),
    dash.dependencies.Input("next-basic-usage", "n_clicks"),
    dash.dependencies.State("stepper-basic-usage", "active"),
    prevent_initial_call=True,
)
def stepper_callback(*args, **kwargs):
    back = (args[0],)
    next = (args[1],)
    current = args[2]
    # print(kwargs)
    # print(current)
    button_id = kwargs["callback_context"].triggered[0]["prop_id"]
    step = current if current is not None else active
    if button_id == "back-basic-usage.n_clicks":
        step = step - 1 if step > min_step else step
    else:
        step = step + 1 if step < max_step else step
    return step
