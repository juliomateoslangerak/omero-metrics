import traceback
from time import sleep

import dash
import dash_mantine_components as dmc
from dash import dcc, html
from django_plotly_dash import DjangoDash
from microscopemetrics_schema import datamodel as mm_schema

import omero_metrics.dash_apps.utils.omero_metrics_components as my_components
from omero_metrics.dash_apps.utils import dash_forms_tools as dft
from omero_metrics.styles import (
    CONTAINER_STYLE,
    MANTINE_THEME,
    THEME,
)
from omero_metrics.views import run_analysis_view

active = 0
min_step = 0
max_step = 2


dashboard_name = "omero_dataset_form"
dash_form_dataset = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=[
        "/static/omero_metrics/css/style_app.css",
    ],
)

dash_form_dataset.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        # Header Section
        my_components.header_component(
            "Analysis Dashboard",
            "Configure and run your analysis",
            "Analysis Form",
            load_buttons=False,
        ),
        dmc.Container(
            [
                dmc.LoadingOverlay(
                    id="loading-overlay",
                    overlayProps={
                        "radius": "sm",
                        "blur": 1,
                    },
                ),
                # Live progress of analyses that report it (the chromatic shift
                # analysis forwards Chromagnon's messages). Hidden until a run
                # starts; a clientside poller fills it from the progress log.
                dmc.Paper(
                    id="progress-panel",
                    withBorder=True,
                    radius="md",
                    p="md",
                    shadow="md",
                    style={"display": "none"},
                    children=[
                        dmc.Group(
                            [
                                dmc.Loader(size="sm"),
                                dmc.Text("Analysis progress", fw=500),
                            ],
                            gap="xs",
                            mb="xs",
                        ),
                        html.Pre(
                            id="progress-log",
                            style={
                                "maxHeight": "260px",
                                "overflowY": "auto",
                                "whiteSpace": "pre-wrap",
                                "fontSize": "12px",
                                "margin": 0,
                                "fontFamily": "monospace",
                            },
                        ),
                    ],
                ),
                # Main content
                dmc.Paper(
                    id="main-content",
                    shadow="xs",
                    p="md",
                    radius="md",
                    children=[
                        # Progress indicator
                        dmc.Progress(
                            id="analysis-progress",
                            value=0,
                            color=THEME["primary"],
                            radius="xl",
                            size="sm",
                            mb="xl",
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
                                    description="Define sample parameters",
                                    icon=my_components.get_icon(
                                        icon="material-symbols:science-outline",
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
                                                html.Div(id="sample_container"),
                                            ],
                                        )
                                    ],
                                ),
                                dmc.StepperStep(
                                    id="step_input_data",
                                    label="Data Selection",
                                    description="Choose input images",
                                    icon=my_components.get_icon(
                                        icon="material-symbols:image-search",
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
                                                                            leftSection=my_components.get_icon(
                                                                                icon="material-symbols-light:image",
                                                                            ),
                                                                            styles={
                                                                                "input": {
                                                                                    "borderColor": THEME[
                                                                                        "border"
                                                                                    ]
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
                                                                                    "borderColor": THEME[
                                                                                        "border"
                                                                                    ]
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
                                    leftSection=my_components.get_icon(
                                        icon="material-symbols:arrow-back",
                                    ),
                                    color=THEME["secondary"],
                                ),
                                dmc.Button(
                                    "Next",
                                    id="next-basic-usage",
                                    rightSection=my_components.get_icon(
                                        icon="material-symbols:arrow-forward",
                                    ),
                                    color=THEME["primary"],
                                ),
                            ],
                            justify="space-between",
                            mt="xl",
                        ),
                    ],
                ),
                html.Div(id="analysis-results"),
                html.Div(id="blank"),
                dcc.Interval(
                    id="progress-interval",
                    interval=1000,
                    n_intervals=0,
                    disabled=True,
                ),
                # The dataset id, for the clientside progress poller.
                dcc.Store(id="dataset-id-store"),
            ],
            size="xl",
            p="md",
            style=CONTAINER_STYLE,
        ),
    ],
)

dft.register_growing_list_callbacks(dash_form_dataset)


@dash_form_dataset.expanded_callback(
    dash.dependencies.Output("setup-text", "children"),
    [dash.dependencies.Input("blank", "children")],
)
def update_setup(_blank, *, session_state):
    input_parameters = session_state["context"]["input_parameters"][
        "input_parameters"
    ]
    input_parameters_object = getattr(mm_schema, input_parameters["type"])
    input_parameters_mm = input_parameters_object(**input_parameters["fields"])

    return dft.render_fieldset(
        input_parameters_mm, disabled=True, form_id="input_parameters_form"
    )


@dash_form_dataset.expanded_callback(
    dash.dependencies.Output("sample_container", "children"),
    [dash.dependencies.Input("blank", "children")],
)
def update_sample(_blank, *, session_state):
    sample = session_state["context"]["input_parameters"]["sample"]
    mm_sample = getattr(mm_schema, sample["type"])
    mm_sample = mm_sample(**sample["fields"])

    return dft.render_fieldset(mm_sample, disabled=True, form_id="sample_form")


@dash_form_dataset.expanded_callback(
    dash.dependencies.Output("framework-multi-select", "data"),
    dash.dependencies.Output("framework-multi-select", "value"),
    [dash.dependencies.Input("blank", "children")],
)
def list_images_multi_selector(_blank, *, session_state):
    list_images = session_state["context"]["list_images"]
    return list_images, [list_images[i]["value"] for i, _ in enumerate(list_images)]


@dash_form_dataset.expanded_callback(
    dash.dependencies.Output("framework-multi-select", "error"),
    [dash.dependencies.Input("framework-multi-select", "value")],
)
def multi_selector_callback(value):
    return "Select at least 1." if len(value) < 1 else ""


@dash_form_dataset.expanded_callback(
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
def update_review_form(
    _next_clicks, form_content, multi_selector, input_parameters, current
):

    selectors = dmc.MultiSelect(
        label="Images selected",
        data=[f"Image ID: {i}" for i in multi_selector],
        value=multi_selector,
        clearable=False,
        w="auto",
        disabled=True,
        leftSection=my_components.get_icon(icon="material-symbols-light:image"),
        rightSection=my_components.get_icon(icon="radix-icons:chevron-down"),
    )
    if current == 1:
        return (
            selectors,
            dft.disable_all_fields_dash_form(form_content),
            input_parameters,
        )
    else:
        return dash.no_update


@dash_form_dataset.expanded_callback(
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
def stepper_callback(
    _back_clicks,
    _next_clicks,
    multi_selector,
    current,
    sample_form_content,
    *,
    callback_context,
):
    button_id = callback_context.triggered[0]["prop_id"]
    step = current if current is not None else active
    next_text = "Next"
    next_color = THEME["primary"]
    if button_id == "back-basic-usage.n_clicks":
        step = step - 1 if step > min_step else step
    else:
        if step == 0 and not dft.validate_form(sample_form_content):
            step = 0
        elif step == 1 and len(multi_selector) < 1:
            step = 1
        else:
            if step >= 1:
                next_text = "Run Analysis"
                next_color = THEME["primary"]
            step = step + 1 if step < max_step else step
    return step, next_text, next_color


dash_form_dataset.clientside_callback(
    """
    function updateLoadingState(n_clicks, current) {
        if (current == 2) {
            return true
        } else {
            return false
        }
    }
    """,
    dash.dependencies.Output("loading-overlay", "visible", allow_duplicate=True),
    dash.dependencies.Input("next-basic-usage", "n_clicks"),
    dash.dependencies.State("stepper-basic-usage", "active"),
    prevent_initial_call=True,
)


@dash_form_dataset.expanded_callback(
    dash.dependencies.Output("main-content", "children"),
    dash.dependencies.Output("loading-overlay", "visible"),
    [
        dash.dependencies.Input("next-basic-usage", "n_clicks"),
        dash.dependencies.State("framework-multi-select", "value"),
        dash.dependencies.State("stepper-basic-usage", "active"),
        dash.dependencies.State("comment", "value"),
    ],
    prevent_initial_call=True,
)
def run_analysis(
    _next_clicks, list_images, current, comment, *, session_state, request
):
    dataset_id = session_state["context"]["dataset_id"]
    if current == 2:
        sleep(1)
        input_parameters = session_state["context"]["input_parameters"][
            "input_parameters"
        ]
        sample = session_state["context"]["input_parameters"]["sample"]
        try:
            input_parameters_object = getattr(mm_schema, input_parameters["type"])
            mm_input_parameters = input_parameters_object(
                **input_parameters["fields"]
            )
            sample_object = getattr(mm_schema, sample["type"])
            mm_sample = sample_object(**sample["fields"])

            response_type, response_msg, response_details = run_analysis_view(
                request=request,
                dataset_id=dataset_id,
                mm_sample=mm_sample,
                list_images=list_images,
                mm_input_parameters=mm_input_parameters,
                comment=comment,
            )

            return my_components.alert_handler(
                response_type, response_msg, response_details
            )

        except Exception as e:
            return my_components.alert_handler(
                "unidentified_error", f"{e}", traceback.format_exc()
            )[:1]
    return dash.no_update, False


dash_form_dataset.clientside_callback(
    """
    function updateProgress(active) {
        return active * 50;
    }
    """,
    dash.dependencies.Output("analysis-progress", "value"),
    dash.dependencies.Input("stepper-basic-usage", "active"),
)


@dash_form_dataset.expanded_callback(
    dash.dependencies.Output("dataset-id-store", "data"),
    [dash.dependencies.Input("blank", "children")],
)
def store_dataset_id(_blank, *, session_state):
    return session_state["context"].get("dataset_id")


# Poll the progress log of the running analysis. A clientside fetch to a plain
# Django view (views.dataset_analysis_progress), not a Dash callback: a Dash
# callback would wait behind the blocking run_analysis callback of the same
# django-plotly-dash session and could not report progress live.
dash_form_dataset.clientside_callback(
    """
    async function(n, datasetId) {
        if (!datasetId) { return window.dash_clientside.no_update; }
        try {
            const r = await fetch("/omero_metrics/progress/" + datasetId + "/",
                                  {credentials: "same-origin"});
            if (!r.ok) { return window.dash_clientside.no_update; }
            const text = await r.text();
            requestAnimationFrame(function() {
                const el = document.getElementById("progress-log");
                if (el) { el.scrollTop = el.scrollHeight; }
            });
            return text;
        } catch (e) {
            return window.dash_clientside.no_update;
        }
    }
    """,
    dash.dependencies.Output("progress-log", "children"),
    dash.dependencies.Input("progress-interval", "n_intervals"),
    dash.dependencies.State("dataset-id-store", "data"),
)


# Show the panel and start polling when the run starts (the same click that
# shows the loading overlay). Keyed on next-basic-usage rather than on
# loading-overlay.visible, which did not trigger the callback.
dash_form_dataset.clientside_callback(
    """
    function(n_clicks, current) {
        if (current == 2) {
            requestAnimationFrame(function() {
                var el = document.getElementById("progress-panel");
                if (el) { el.scrollIntoView({behavior: "smooth", block: "center"}); }
            });
            // Above the LoadingOverlay (z-index 400).
            return [false, {position: "relative", zIndex: 1000}];
        }
        return [true, {display: "none"}];
    }
    """,
    dash.dependencies.Output("progress-interval", "disabled"),
    dash.dependencies.Output("progress-panel", "style"),
    dash.dependencies.Input("next-basic-usage", "n_clicks"),
    dash.dependencies.State("stepper-basic-usage", "active"),
    prevent_initial_call=True,
)


# Hide the panel and stop polling when the run has finished (run_analysis
# replaces the main content with the result).
dash_form_dataset.clientside_callback(
    """
    function(content) {
        return [true, {display: "none"}];
    }
    """,
    dash.dependencies.Output("progress-interval", "disabled", allow_duplicate=True),
    dash.dependencies.Output("progress-panel", "style", allow_duplicate=True),
    dash.dependencies.Input("main-content", "children"),
    prevent_initial_call=True,
)
