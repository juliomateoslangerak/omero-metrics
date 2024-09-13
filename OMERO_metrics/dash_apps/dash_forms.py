import dash
from dash import html
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from microscopemetrics_schema import datamodel as mm_schema
from dataclasses import fields
import re
from omeroweb.webclient.decorators import login_required
from time import sleep
from OMERO_metrics.tools import omero_tools
from omero.gateway import ProjectWrapper, BlitzGateway
from linkml_runtime.dumpers import YAMLDumper
import tempfile


def _dump_config_input_parameters(
    conn: BlitzGateway,
    input_parameters: mm_schema.MetricsInputParameters,
    target_omero_obj: ProjectWrapper,
):
    dumper = YAMLDumper()

    with tempfile.NamedTemporaryFile(
        prefix=f"{input_parameters.class_name}_",
        suffix=".yaml",
        mode="w",
        delete=False,
    ) as f:
        f.write(dumper.dumps(input_parameters))
        f.close()
        file_ann = omero_tools.create_file(
            conn=conn,
            file_path=f.name,
            omero_object=target_omero_obj,
            file_description="Configuration file",
            namespace=input_parameters.class_class_curie,
            mimetype="application/yaml",
        )

    return file_ann


Field_TYPE_MAPPING = {
    "float": "NumberInput",
    "int": "NumberInput",
    "str": "TextInput",
    "bool": "Checkbox",
}


def clean_field_name(field: str):
    return field.replace("_", " ").title()


def get_field_types(field, supported_types=["str", "int", "float", "bool"]):
    data_type = {
        "field_name": clean_field_name(field.name),
        "type": None,
        "optional": False,
        "default": field.default,
    }
    if field.type.__name__ == "Optional":
        data_type["type"] = field.type.__args__[0].__name__
        data_type["optional"] = True
    elif field.type.__name__ in supported_types:
        data_type["type"] = field.type.__name__
    else:
        data_type["type"] = "unsupported"
    return data_type


def get_dmc_field_input(field, type_mapping=Field_TYPE_MAPPING):
    field_info = get_field_types(field)
    input_field_name = getattr(dmc, type_mapping[field_info["type"]])
    input_field = input_field_name()
    input_field.id = field_info["field_name"].replace(" ", "_").lower()
    input_field.label = field_info["field_name"]
    input_field.placeholder = "Enter " + field_info["field_name"]
    input_field.value = field_info["default"]
    input_field.w = "300"
    input_field.required = not field_info["optional"]
    input_field.leftSection = DashIconify(icon="radix-icons:ruler-horizontal")
    # if not field_info['optional']:
    #     input_field.error = "This field is required"
    return input_field


def add_space_between_capitals(s: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", s)


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
                dmc.Stack(
                    id="form_stack",
                    children=[
                        dmc.Select(
                            id="analysis_type_selector",
                            label="Select Analysis Type",
                            data=analysis_types,
                            w="300",
                            value="0",
                            clearable=False,
                            leftSection=DashIconify(
                                icon="radix-icons:ruler-horizontal"
                            ),
                            rightSection=DashIconify(
                                icon="radix-icons:chevron-down"
                            ),
                        ),
                        html.Div(id="form_analysis_type"),
                    ],
                    gap="xs",
                    style={"margin-top": 10},
                ),
                html.Div(id="test_wawa", children=[]),
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


@login_required()
def get_connection(request, conn=None, **kwargs):
    return conn


@dash_form_project.expanded_callback(
    dash.dependencies.Output("form_analysis_type", "children"),
    [
        dash.dependencies.Input("analysis_type_selector", "value"),
    ],
)
def form_update(*args, **kwargs):
    conn = get_connection(kwargs["request"])
    project_id = int(kwargs["session_state"]["context"]["project_id"])
    # projectWrapper = conn.getObject("Project", int(project_id))
    analysis_type = analysis_types[int(args[0])]
    if analysis_type["label"] in ALLOWED_ANALYSIS_TYPES:
        form_content = dmc.Stack(
            id="form_content",
            children=[],
            align="center",
            style={
                "width": "auto",
                "height": "auto",
                "border-radius": "0.5rem",
                "padding": "10px",
                "border": "1px solid #189A35",
            },
        )

        for field in fields(getattr(mm_schema, analysis_type["label"])):
            form_content.children.append(
                get_dmc_field_input(field, Field_TYPE_MAPPING)
            )
        form_content.children.append(
            dmc.Button(id="submit_id", children=["Submit"], color="green")
        )
        form = dmc.Stack(
            [
                dmc.Group(
                    [
                        dmc.Title(
                            [
                                analysis_type["label"].replace(
                                    "InputParameters", ""
                                )
                                + " Configuration Form"
                            ],
                            c="#189A35",
                            size="h3",
                            mb=10,
                        ),
                    ],
                ),
                form_content,
            ],
            align="center",
            style={
                "background-color": "white",
                "border-radius": "0.5rem",
                "padding": "10px",
            },
        )
        return form
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


@login_required()
def get_connection(request, conn, **kwargs):
    return conn


def validate_form(state):
    return all(
        i["props"]["id"] == "submit_id"
        or not (i["props"]["required"] and i["props"]["value"] is None)
        for i in state
    )


@dash_form_project.expanded_callback(
    dash.dependencies.Output("form_stack", "children"),
    [
        dash.dependencies.Input("submit_id", "n_clicks"),
        dash.dependencies.State("form_content", "children"),
        dash.dependencies.State("analysis_type_selector", "value"),
    ],
    prevent_initial_call=True,
)
def save_config(*args, **kwargs):
    analysis_type = analysis_types[int(args[2])]
    form = getattr(mm_schema, analysis_type["label"])
    conn = get_connection(kwargs["request"])
    project_id = int(kwargs["session_state"]["context"]["project_id"])
    projectWrapper = conn.getObject("Project", int(project_id))
    form_content = args[1]
    sleep(3)
    if validate_form(form_content):
        form_data = {}
        for i in form_content:
            if i["props"]["id"] != "submit_id":
                form_data[i["props"]["id"]] = i["props"]["value"]
        form_instance = form(**form_data)
        _dump_config_input_parameters(conn, form_instance, projectWrapper)
        return [dmc.Alert("Configuration saved", color="green")]

    else:
        return [dmc.Alert("Please fill all required fields", color="red")]
