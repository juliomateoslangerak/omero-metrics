import traceback
from time import sleep

import dash
import dash_mantine_components as dmc
from dash import html
from django_plotly_dash import DjangoDash
from microscopemetrics.analyses.mappings import MAPPINGS
from microscopemetrics_schema import datamodel as mm_schema

import omero_metrics.dash_apps.utils.omero_metrics_components as my_components
import omero_metrics.views as views
from omero_metrics.dash_apps.utils import dash_forms_tools as dft
from omero_metrics.styles import (
    CONTAINER_STYLE,
    MANTINE_THEME,
    THEME,
)

# TODO: change the styles import


DATASET_TO_INPUT_PARAMETERS = {
    "FieldIlluminationDataset": mm_schema.FieldIlluminationInputParameters,
    "PSFBeadsDataset": mm_schema.PSFBeadsInputParameters,
    "CoRegistrationDataset": mm_schema.CoRegistrationInputParameters,
}

SAMPLE_TYPE_LOOKUP = {
    f"{dataset_cls}:{sample_cls}": (sample_cls, dataset_cls)
    for dataset_cls, mapping in MAPPINGS.items()
    for sample_cls in mapping.sample_classes
}

sample_types_dp = [
    {
        "label": dft.add_space_between_capitals(sample_cls.__name__),
        "value": key,
        "description": f"Configure analysis for {sample_cls.__name__}",
    }
    for key, (sample_cls, _) in SAMPLE_TYPE_LOOKUP.items()
]


dashboard_name = "omero_project_config_form"
dash_form_project = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "/static/omero_metrics/css/style_app.css",
    ],
)

dash_form_project.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        my_components.header_component(
            "Configuration Setup",
            "Configure your sample type and input parameters",
            "Analysis Form",
            load_buttons=False,
        ),
        dmc.Container(
            [
                dmc.Paper(
                    id="main-content",
                    children=[
                        dmc.LoadingOverlay(
                            id="loading-overlay",
                            overlayProps={
                                "radius": "sm",
                                "blur": 1,
                            },
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
                                    id="step-sample",
                                    label="Sample Configuration",
                                    description="Define your sample parameters",
                                    icon=my_components.get_icon(
                                        icon="mdi:microscope"
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
                                                    id="sample-type-selector",
                                                    data=sample_types_dp,
                                                    searchable=True,
                                                    placeholder="Select Sample Type",
                                                    leftSection=my_components.get_icon(
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
                                                html.Div(id="sample-container"),
                                            ],
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                        )
                                    ],
                                ),
                                dmc.StepperStep(
                                    id="step-input-data",
                                    label="Analysis Parameters",
                                    description="Set analysis configuration",
                                    icon=my_components.get_icon(
                                        icon="mdi:tune-vertical"
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
                                                    id="input-parameters-container"
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
                                                                        id="sample-col"
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
                                                                        id="input-col"
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
                        dmc.Group(
                            children=[
                                dmc.Button(
                                    "Back",
                                    id="back-basic-usage",
                                    variant="outline",
                                    leftSection=my_components.get_icon(
                                        icon="mdi:arrow-left"
                                    ),
                                ),
                                dmc.Button(
                                    "Next",
                                    id="next-basic-usage",
                                    color=THEME["primary"],
                                    rightSection=my_components.get_icon(
                                        icon="mdi:arrow-right"
                                    ),
                                ),
                            ],
                            justify="space-between",
                            mt="xl",
                        ),
                    ],
                    shadow="xs",
                    p="md",
                    radius="md",
                ),
            ],
            size="xl",
            p="md",
            style=CONTAINER_STYLE,
        ),
    ],
)

dft.register_growing_list_callbacks(dash_form_project)


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
        dash.dependencies.State("sample-content", "children"),
        dash.dependencies.State("input-content", "children"),
    ],
    prevent_initial_call=True,
)
def stepper_callback(*args, **kwargs):
    current = args[2]
    button_id = kwargs["callback_context"].triggered[0]["prop_id"]
    step = current if current is not None else 0

    progress = (step / 2) * 100

    if button_id == "back-basic-usage.n_clicks":
        step = max(0, step - 1)
        next_text = ["Next"]
        next_icon = my_components.get_icon(icon="mdi:arrow-right")
        next_color = THEME["primary"]
    else:
        sample = args[3]
        input_parameters = args[4]

        if step == 0 and not dft.validate_form(sample):
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                progress,
                dash.no_update,
            )
        elif step == 1 and not dft.validate_form(input_parameters):
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                progress,
                dash.no_update,
            )

        step = min(2, step + 1)

        if step == 2:
            next_text = ["Save Configuration"]
            next_icon = my_components.get_icon(icon="mdi:check")
            next_color = THEME["primary"]
        else:
            next_text = ["Next"]
            next_color = THEME["primary"]
            next_icon = my_components.get_icon(icon="mdi:arrow-right")

    progress = (step / 2) * 100
    return step, next_text, next_color, progress, next_icon


@dash_form_project.expanded_callback(
    dash.dependencies.Output("sample-container", "children"),
    [
        dash.dependencies.Input("sample-type-selector", "value"),
    ],
    prevent_initial_call=True,
)
def update_sample_container(sample_type_selector, **kwargs):
    mm_sample = SAMPLE_TYPE_LOOKUP[sample_type_selector][0]
    sample_form = dft.render_fieldset(
        mm_sample, disabled=False, form_id="sample-content"
    )
    return [sample_form]


@dash_form_project.expanded_callback(
    dash.dependencies.Output("input-parameters-container", "children"),
    [
        dash.dependencies.Input("sample-type-selector", "value"),
    ],
    prevent_initial_call=True,
)
def update_input_parameters(sample_type_selector, **kwargs):
    analysis_type = SAMPLE_TYPE_LOOKUP[sample_type_selector][1].split("/")[-1]
    mm_input_parameters = DATASET_TO_INPUT_PARAMETERS[analysis_type]
    mm_input_parameters = dft.render_fieldset(
        mm_input_parameters, disabled=False, form_id="input-content"
    )
    return [mm_input_parameters]


@dash_form_project.expanded_callback(
    dash.dependencies.Output("sample-col", "children"),
    dash.dependencies.Output("input-col", "children"),
    [
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("sample-content", "children"),
        dash.dependencies.State("input-content", "children"),
        dash.dependencies.State("stepper-basic-usage", "active"),
    ],
    prevent_initial_call=True,
)
def review_configuration(_, sample_form, input_parameters_form, current, **kwargs):
    sample = dft.disable_all_fields_dash_form(sample_form)
    input_parameters = dft.disable_all_fields_dash_form(input_parameters_form)
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
    dash.dependencies.Output("loading-overlay", "visible", allow_duplicate=True),
    dash.dependencies.Input("next-basic-usage", "n_clicks"),
    dash.dependencies.State("stepper-basic-usage", "active"),
    prevent_initial_call=True,
)


@dash_form_project.expanded_callback(
    dash.dependencies.Output("main-content", "children"),
    dash.dependencies.Output("loading-overlay", "visible"),
    [
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("sample-content", "children"),
        dash.dependencies.State("input-content", "children"),
        dash.dependencies.State("stepper-basic-usage", "active"),
        dash.dependencies.State("sample-type-selector", "value"),
    ],
    prevent_initial_call=True,
)
def save_config_dash(
    clicked_data,
    sample_form,
    input_form,
    current,
    sample_type_selector,
    **kwargs,
):
    if not sample_type_selector:  # No sample type selected
        return dash.no_update, False

    analysis_type = SAMPLE_TYPE_LOOKUP[sample_type_selector][1].split("/")[-1]
    mm_sample = SAMPLE_TYPE_LOOKUP[sample_type_selector][0]
    mm_input_parameters = DATASET_TO_INPUT_PARAMETERS[analysis_type]
    project_id = int(kwargs["session_state"]["context"]["project_id"])
    request = kwargs["request"]
    if clicked_data > 0 and current == 2:
        if dft.validate_form(sample_form) and dft.validate_form(input_form):
            sleep(1)
            try:
                input_parameters = dft.extract_form_data(input_form)
                mm_input_parameters = mm_input_parameters(**input_parameters)
                sample = dft.extract_form_data(sample_form)
                mm_sample = mm_sample(**sample)
                response_type, response_msg = views.save_config(
                    request=request,
                    project_id=project_id,
                    input_parameters=mm_input_parameters,
                    sample=mm_sample,
                )
                sleep(1)

                return my_components.alert_handler(response_type, response_msg)
            except Exception as e:
                return my_components.alert_handler(
                    "unidentified_error", str(e), traceback.format_exc()
                )

    return dash.no_update, False
