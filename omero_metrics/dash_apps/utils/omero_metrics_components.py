import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify

from omero_metrics.styles import (
    HEADER_PAPER_STYLE,
    THEME,
)


def alert_handler(
    response_type,
    response_msg,
    response_details=None,
    with_close_button=None,
    duration=None,
):

    if response_type == "success":
        title = "Success!"
        icon = get_icon(icon="radix-icons:check")
        color = "green"
    elif response_type == "authorisation_error":
        title = "Authorisation Error!"
        icon = get_icon(icon="radix-icons:lock-closed")
        color = "red"
    elif response_type == "analysis_error":
        title = "Analysis Error!"
        icon = get_icon(icon="radix-icons:alert")
        color = "orange"
    elif response_type == "unidentified_error":
        title = "Error!"
        icon = get_icon(icon="radix-icons:alert")
        color = "red"

    children = [dmc.Text(response_msg, size="sm")]
    if response_details:
        children.append(dmc.Code(response_details, block=True))

    return [
        dmc.Alert(
            children=children,
            color=color,
            icon=icon,
            title=title,
            radius="md",
            withCloseButton=with_close_button,
            duration=duration,
        )
    ], False


def notification_handler(response_type, response_msg, opened):
    if response_type == "success":
        title = "Success!"
        icon = get_icon(icon="radix-icons:check")
        color = "green"
    elif response_type == "authorisation_error":
        title = "Authorisation Error!"
        icon = get_icon(icon="radix-icons:lock-closed")
        color = "red"
    elif response_type == "unidentified_error":
        title = "Error!"
        icon = get_icon(icon="radix-icons:alert")
        color = "red"

    # A list for dmc.NotificationContainer's `sendNotifications` prop, which
    # replaced the deprecated dmc.Notification component in DMC 2.8.
    notifications = [
        {
            "id": "simple-notify",
            "action": "show",
            "title": title,
            "message": response_msg,
            "icon": icon,
            "color": color,
        }
    ]
    return opened, notifications, False


def get_icon(icon, size=20, color=None):
    return DashIconify(icon=icon, height=size, color=color)


def make_control(text, action_id):
    return dmc.Flex(
        [
            dmc.AccordionControl(text),
            dmc.ActionIcon(
                children=get_icon(icon="lets-icons:check-fill"),
                color="green",
                variant="default",
                n_clicks=0,
                id={"index": action_id},
            ),
        ],
        justify="center",
        align="center",
    )


download_group = dmc.Group(
    [
        dmc.Menu(
            [
                dmc.MenuTarget(
                    dmc.Button(
                        id="activate-download",
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


download_table = dmc.Group(
    [
        dmc.Menu(
            [
                dmc.MenuTarget(
                    dmc.ActionIcon(
                        DashIconify(icon="material-symbols:download", width=20),
                        color=THEME["primary"],
                    )
                ),
                dmc.MenuDropdown(
                    [
                        dmc.MenuItem(
                            "CSV",
                            id="table-download-csv",
                            leftSection=DashIconify(icon="iwwa:file-csv", width=20),
                        ),
                        dmc.MenuItem(
                            "Excel",
                            id="table-download-xlsx",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-excel", width=20
                            ),
                        ),
                        dmc.MenuItem(
                            "JSON",
                            id="table-download-json",
                            leftSection=DashIconify(
                                icon="vscode-icons:file-type-json", width=20
                            ),
                        ),
                    ]
                ),
            ],
            trigger="click",
        ),
        dcc.Download(id="table-download"),
    ]
)


delete_button = dmc.Button(
    id="delete-data",
    children="Delete",
    color="red",
    variant="filled",
    leftSection=DashIconify(icon="ic:round-delete-forever"),
)


def header_component(title, description, tag, load_buttons=True):
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
