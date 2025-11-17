import dash_mantine_components as dmc
from dash import dcc, html, dependencies
from dash_iconify import DashIconify

from time import sleep
from linkml_runtime.dumpers import YAMLDumper, JSONDumper

from omero_metrics.styles import (
    THEME,
    HEADER_PAPER_STYLE,
    BUTTON_STYLE,
)
from omero_metrics import views
from omero_metrics.dash_apps.dash_utils import omero_metrics_components


# COMPONENTS
def notification_provider():
    return dmc.NotificationProvider(position="top-center")


def notifications_container():
    return html.Div(id="notifications_container")


def confirm_delete_modal():
    return dmc.Modal(
        title="Confirm Delete",
        id="confirm-delete-modal",
        children=[
            dmc.Text("Are you sure you want to delete this dataset outputs?"),
            dmc.Space(h=20),
            dmc.Group(
                [
                    dmc.Button(
                        "Delete",
                        id="confirm-delete-button",
                        color="red",
                    ),
                    dmc.Button(
                        "Cancel",
                        id="cancel-delete-button",
                        color="gray",
                        variant="outline",
                    ),
                ],
                justify="flex-end",
            ),
        ],
    )


def dataset_header_paper(title, description, tag, load_buttons=True):
    return dmc.Paper(
        children=[
            dmc.Group(
                [
                    dmc.Group(
                        [
                            html.Img(
                                src="/static/omero_metrics/images/metrics_logo.png",
                                style={
                                    "width": "120px",
                                    "height": "auto",
                                },
                            ),
                            dmc.Stack(
                                [
                                    dmc.Title(
                                        title,
                                        c=THEME["primary"],
                                        size="h2",
                                    ),
                                    dmc.Text(
                                        description,
                                        c=THEME["text"]["secondary"],
                                        size="sm",
                                    ),
                                ],
                                gap="xs",
                            ),
                        ],
                    ),
                    dmc.Group(
                        [
                            download_group,
                            delete_button,
                            dmc.Badge(
                                tag,
                                color=THEME["primary"],
                                variant="dot",
                                size="lg",
                            ),
                        ]
                        if load_buttons
                        else dmc.Badge(
                            tag,
                            color=THEME["primary"],
                            variant="dot",
                            size="lg",
                        )
                    ),
                ],
                justify="space-between",
            ),
        ],
        **HEADER_PAPER_STYLE,
    )


download_group = dmc.Group(
    [
        dmc.Menu(
            [
                dmc.MenuTarget(
                    dmc.Button(
                        id="activate_download",
                        children="Download",
                        leftSection=DashIconify(
                            icon="material-symbols:download", width=20
                        ),
                        rightSection=DashIconify(
                            icon="carbon:chevron-down", width=20
                        ),
                        color=THEME["primary"],
                        variant="outline",
                    )
                ),
                dmc.MenuDropdown(
                    [
                        dmc.MenuItem(
                            "YAML",
                            id="download-yaml",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-yaml", width=20
                            ),
                        ),
                        dmc.MenuItem(
                            "JSON",
                            id="download-json",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-json", width=20
                            ),
                        ),
                        dmc.MenuItem(
                            "Text",
                            id="download-text",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-text", width=20
                            ),
                        ),
                    ]
                ),
            ],
            trigger="click",
        ),
        dcc.Download(id="download"),
    ]
)


delete_button = dmc.Button(
    id="delete_data",
    children="Delete",
    color="red",
    variant="filled",
    leftSection=DashIconify(icon="ic:round-delete-forever"),
)


# CALLBACKS
def register_delete_datasets_callback(app):
    @app.expanded_callback(
        dependencies.Output("confirm-delete-modal", "opened"),
        dependencies.Output("notifications_container", "children"),
        dependencies.Output("confirm-delete-button", "loading"),
        [
            dependencies.Input("delete_data", "n_clicks"),
            dependencies.Input("confirm-delete-button", "n_clicks"),
            dependencies.Input("cancel-delete-button", "n_clicks"),
            dependencies.State("confirm-delete-modal", "opened"),
        ],
        prevent_initial_call=True,
    )
    def delete_dataset(*args, **kwargs):
        triggered_button = kwargs["callback_context"].triggered[0]["prop_id"]
        dataset_id = kwargs["session_state"]["context"][
            "mm_dataset"
        ].data_reference.omero_object_id
        request = kwargs["request"]
        opened = not args[3]
        if triggered_button == "confirm-delete-button.n_clicks" and args[0] > 0:
            sleep(1)
            response_type, response_msg = views.delete_dataset(
                request, dataset_id=dataset_id
            )

            return omero_metrics_components.notification_handler(
                response_type, response_msg, opened
            )
        else:
            return opened, None, False


def register_download_datasets_callback(app):
    @app.expanded_callback(
        dependencies.Output("download", "data"),
        [
            dependencies.Input("download-yaml", "n_clicks"),
            dependencies.Input("download-json", "n_clicks"),
            dependencies.Input("download-text", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def download_dataset_data(*args, **kwargs):
        if not kwargs["callback_context"].triggered:
            raise dash.no_update

        triggered_id = (
            kwargs["callback_context"].triggered[0]["prop_id"].split(".")[0]
        )
        mm_dataset = kwargs["session_state"]["context"]["mm_dataset"]
        file_name = mm_dataset.name
        yaml_dumper = YAMLDumper()
        json_dumper = JSONDumper()
        if triggered_id == "download-yaml":
            return dict(
                content=yaml_dumper.dumps(mm_dataset), filename=f"{file_name}.yaml"
            )

        elif triggered_id == "download-json":
            return dict(
                content=json_dumper.dumps(mm_dataset), filename=f"{file_name}.json"
            )

        elif triggered_id == "download-text":
            return dict(
                content=yaml_dumper.dumps(mm_dataset), filename=f"{file_name}.txt"
            )

        raise dash.no_update
