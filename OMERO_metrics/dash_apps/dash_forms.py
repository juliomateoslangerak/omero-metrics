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
            form_content.children.append(dft.get_dmc_field_input(field))
        form_content.children.append(
            dmc.Button(
                id="submit_id", children=["Submit"], color="green", n_clicks=0
            )
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


def validate_form(state):
    return all(
        i["props"]["id"] == "submit_id"
        or not (
            i["props"]["required"]
            and i["props"]["value"] is None
            or i["props"]["value"] == ""
        )
        for i in state
    )


@dash_form_project.expanded_callback(
    dash.dependencies.Output("form_content", "children"),
    dash.dependencies.Output("submit_id", "loading"),
    [
        dash.dependencies.Input("submit_id", "n_clicks"),
        dash.dependencies.State("form_content", "children"),
        dash.dependencies.State("analysis_type_selector", "value"),
    ],
)
def save_config(*args, **kwargs):
    analysis_type = analysis_types[int(args[2])]
    form = getattr(mm_schema, analysis_type["label"])
    request = kwargs["request"]
    project_id = int(kwargs["session_state"]["context"]["project_id"])
    form_content = args[1]
    if args[0] > 0:
        if validate_form(form_content):
            form_data = {}
            sleep(2)
            for i in form_content:
                if i["props"]["id"] != "submit_id":
                    form_data[i["props"]["id"]] = i["props"]["value"]
            form_instance = form(**form_data)
            response, color = get_connection(
                request, project_id=project_id, form_instance=form_instance
            )
            return [dmc.Alert(response, color=color)], False
        else:
            return dash.no_update, False
    else:
        dash.no_update, False
