import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from microscopemetrics_schema import datamodel as mm_schema
from time import sleep
from OMERO_metrics import views
from OMERO_metrics.tools import dash_forms_tools as dft


formManager = dft.dashForm(
    mm_schema.Sample, disabled=False, form_id="sample_content"
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
dashboard_name = "omero_project_config_form"
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
                                    "Add a Configuration file",
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
                dmc.Select(
                    id="analysis_type_selector",
                    label="Select Analysis Type",
                    data=analysis_types,
                    w="300",
                    value="0",
                    clearable=False,
                    leftSection=DashIconify(
                        icon="radix-icons:magnifying-glass"
                    ),
                    rightSection=DashIconify(icon="radix-icons:chevron-down"),
                    placeholder="Select Analysis Type",
                ),
                dmc.Stack(
                    id="form_stack",
                    children=[
                        dmc.Grid(
                            [
                                dmc.GridCol(
                                    [
                                        dmc.Center(
                                            dmc.Text(
                                                "Sample Information",
                                                mb=10,
                                                c="#189A35",
                                                fw="bold",
                                            )
                                        ),
                                        sampleFORM,
                                    ],
                                    span="content",
                                ),
                                dmc.GridCol(
                                    id="form_analysis_type",
                                    span="content",
                                ),
                            ],
                            justify="space-around",
                            align="flex-start",
                        ),
                        dmc.Center(
                            dmc.Button(
                                id="submit_id",
                                children="Submit",
                                color="green",
                                n_clicks=0,
                            )
                        ),
                    ],
                    gap="xs",
                    style={
                        "margin-top": "20px",
                        "background-color": "white",
                        "border-radius": "0.5rem",
                        "padding": "10px",
                    },
                ),
                html.Div(id="saving_result", children=[]),
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
    dash.dependencies.Output("form_analysis_type", "children"),
    [
        dash.dependencies.Input("analysis_type_selector", "value"),
    ],
)
def form_update(*args, **kwargs):
    analysis_type = analysis_types[int(args[0])]
    if analysis_type["label"] in ALLOWED_ANALYSIS_TYPES:
        ana = getattr(mm_schema, analysis_type["label"])
        form = dft.dashForm(ana, disabled=False, form_id="config_content")
        return [
            dmc.Center(
                dmc.Text(
                    "Analysis Configuration", mb=10, c="#189A35", fw="bold"
                )
            ),
            form.form,
        ]
    else:
        return dmc.Alert("Analysis type not allowed", color="red")


dash_form_project.clientside_callback(
    """
    function updateLoadingState(n_clicks) {
        return true
    }
    """,
    dash.dependencies.Output("submit_id", "loading", allow_duplicate=True),
    dash.dependencies.Input("submit_id", "n_clicks"),
    prevent_initial_call=True,
)


@dash_form_project.expanded_callback(
    dash.dependencies.Output("form_stack", "children"),
    dash.dependencies.Output("submit_id", "loading"),
    [
        dash.dependencies.Input("submit_id", "n_clicks"),
        dash.dependencies.State("sample_content", "children"),
        dash.dependencies.State("config_content", "children"),
        dash.dependencies.State("analysis_type_selector", "value"),
    ],
    prevent_initial_call=True,
)
def save_config_dash(*args, **kwargs):
    analysis_type = analysis_types[int(args[3])]
    sample_form_content = args[1]
    config_content = args[2]
    project_id = int(kwargs["session_state"]["context"]["project_id"])
    request = kwargs["request"]

    if args[0] > 0:
        if dft.validate_form(config_content) and dft.validate_form(
            sample_form_content
        ):
            sleep(2)
            mm_input_parameters = getattr(mm_schema, analysis_type["label"])
            input_parameters = dft.extract_form_data(config_content)
            mm_input_parameters = mm_input_parameters(**input_parameters)
            sample = dft.extract_form_data(sample_form_content)
            mm_sample = mm_schema.Sample(**sample)
            response, color = views.save_config(
                request=request,
                project_id=int(project_id),
                input_parameters=mm_input_parameters,
                sample=mm_sample,
            )
            return [dmc.Alert(response, color=color)], False
        else:
            return dash.no_update, False
    else:
        dash.no_update, False
