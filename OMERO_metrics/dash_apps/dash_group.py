import dash
import pandas as pd
from dash import html, dash_table, dcc
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from OMERO_metrics import views

dashboard_name = "omero_group_dash"
dash_app_group = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
    external_stylesheets=dmc.styles.ALL,
)

dash_app_group.layout = dmc.MantineProvider(
    [
        dmc.Tabs(
            [
                dmc.TabsList(
                    [
                        dmc.TabsTab(
                            "Microscope Health",
                            leftSection=DashIconify(icon="tabler:microscope"),
                            value="microscope_health",
                            color="#189A35",
                            style={
                                "font-size": "1.1rem",
                                "font-weight": "bold",
                                "color": "#189A35",
                            },
                        ),
                        dmc.TabsTab(
                            "History",
                            leftSection=DashIconify(icon="bx:history"),
                            value="history",
                            color="#189A35",
                            style={
                                "font-size": "1.1rem",
                                "font-weight": "bold",
                                "color": "#189A35",
                            },
                        ),
                    ],
                    grow="True",
                    justify="space-around",
                    variant="light",
                    style={"background-color": "white"},
                ),
                dmc.TabsPanel(
                    dmc.Container(
                        [
                            dmc.Card(
                                children=[
                                    dmc.Group(
                                        [
                                            html.Img(
                                                src="/static/OMERO_metrics/images/microscope.png",
                                                style={"width": "100px"},
                                            ),
                                            dmc.Title(
                                                "Microscope Health Dashboard",
                                                c="#189A35",
                                                size="h3",
                                                mb=10,
                                                mt=5,
                                            ),
                                        ],
                                        justify="space-between",
                                        align="center",
                                        mt="md",
                                        mb="xs",
                                    ),
                                    dmc.Divider(mb="sm"),
                                    html.Div(id="microscope_info"),
                                ],
                                withBorder=True,
                                shadow="sm",
                                radius="md",
                                style={
                                    "width": "100%",
                                    "maxWidth": "600px",
                                    "margin": "auto",
                                },
                            ),
                        ],
                        fluid=True,
                        style={
                            "background-color": "white",
                            "margin": "10px",
                            "border-radius": "0.5rem",
                            "padding": "10px",
                        },
                    ),
                    value="microscope_health",
                ),
                dmc.TabsPanel(
                    dmc.Container(
                        children=[
                            dmc.Group(
                                [
                                    dmc.Button(
                                        "Download",
                                        variant="gradient",
                                        gradient={
                                            "from": "teal",
                                            "to": "lime",
                                            "deg": 105,
                                        },
                                        id="download_test",
                                    ),
                                    dcc.Download(id="download"),
                                    dmc.DatePicker(
                                        id="date-picker",
                                        label="Select Date",
                                        valueFormat="DD-MM-YYYY",
                                        leftSection=DashIconify(
                                            icon="clarity:date-line"
                                        ),
                                        type="range",
                                        w="250",
                                    ),
                                    dmc.Select(
                                        "select",
                                        data=[
                                            "File Annotation",
                                            "Map Annotation",
                                        ],
                                        label="Select Annotation Type",
                                        w="250",
                                    ),
                                    dmc.Button(
                                        id="delete-all",
                                        children="Delete All",
                                        variant="gradient",
                                        gradient={
                                            "from": "teal",
                                            "to": "lime",
                                            "deg": 105,
                                        },
                                        w="250",
                                    ),
                                    dmc.Modal(
                                        title="Confirm Delete",
                                        id="confirm_delete",
                                        children=[
                                            dmc.Text(
                                                "Are you sure you want to delete all annotations including ROIs?"
                                            ),
                                            dmc.Space(h=20),
                                            dmc.Group(
                                                [
                                                    dmc.Button(
                                                        "Submit",
                                                        id="modal-submit-button",
                                                    ),
                                                    dmc.Button(
                                                        "Close",
                                                        color="red",
                                                        variant="outline",
                                                        id="modal-close-button",
                                                    ),
                                                ],
                                                justify="flex-end",
                                            ),
                                        ],
                                    ),
                                ],
                                justify="space-around",
                                align="flex-end",
                                style={"margin": "10px"},
                            ),
                            dmc.Space(h=10),
                            dmc.Divider(mb="sm"),
                            dmc.Space(h=20),
                            dmc.Text(
                                "File Annotations",
                                c="#189A35",
                                size="xl",
                            ),
                            html.Div(
                                id="project_file_annotations_table",
                                style={"margin": "10px"},
                            ),
                            dmc.Divider(mb="sm"),
                            dmc.Text(
                                "Map Annotations",
                                c="#189A35",
                                size="xl",
                            ),
                            html.Div(
                                id="project_map_annotations_table",
                                style={"margin": "10px"},
                            ),
                            html.Div(id="notify-container"),
                            html.Div(id="blank-input"),
                            html.Div(id="result"),
                        ],
                        fluid=True,
                        style={
                            "background-color": "white",
                            "margin": "10px",
                            "border-radius": "0.5rem",
                            "padding": "10px",
                        },
                    ),
                    value="history",
                ),
            ],
            value="microscope_health",
        ),
    ]
)


@dash_app_group.expanded_callback(
    dash.dependencies.Output("microscope_info", "children"),
    dash.dependencies.Input("blank-input", "children"),
)
def render_content(*args, **kwargs):
    group_name = kwargs["session_state"]["context"]["group_name"]
    group_id = kwargs["session_state"]["context"]["group_id"]
    group_description = kwargs["session_state"]["context"]["group_description"]
    result = dmc.Stack(
        [
            dmc.Text("Microscope Information", c="#189A35", size="xl"),
            dmc.Text(f"Group Name: {group_name}", size="xs"),
            dmc.Text(f"Group ID: {group_id}", size="xs"),
            dmc.Text(f"Group Description: {group_description}", size="xs"),
        ],
        align="flex-start",
        gap="xs",
    )
    return result


# @dash_app_group.expanded_callback(
#     dash.dependencies.Output("blank-input", "children"),
#     dash.dependencies.Input("blank-input", "children"),
# )
# def update_filter_bar(*args, **kwargs):
#     table_df = kwargs["session_state"]["context"]["table_df"]
#
#     return args[0]


@dash_app_group.expanded_callback(
    dash.dependencies.Output("project_file_annotations_table", "children"),
    dash.dependencies.Output("project_map_annotations_table", "children"),
    dash.dependencies.Input("blank-input", "children"),
)
def load_table_project(*args, **kwargs):
    file_ann = kwargs["session_state"]["context"]["file_ann"]
    file_ann_subset = file_ann[
        file_ann.columns[~file_ann.columns.str.contains("ID")]
    ]
    file_ann_table = dash_table.DataTable(
        id="datatable-interactivity",
        columns=[{"name": i, "id": i} for i in file_ann_subset.columns],
        data=file_ann_subset.to_dict("records"),
        sort_action="native",
        sort_mode="multi",
        row_selectable="multi",
        page_action="native",
        page_current=0,
        page_size=5,
        style_table={
            "overflowX": "auto",
            "borderRadius": "0.5rem",
            "fontFamily": "'Arial', 'Helvetica', sans-serif",
            "borderCollapse": "collapse",
            "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
            "margin": "20px 0",
            "borderLeft": "none",
            "borderRight": "none",
        },
        style_cell={
            "whiteSpace": "normal",
            "height": "30px",
            "minWidth": "100px",
            "width": "100px",
            "maxWidth": "100px",
            "textAlign": "left",
            "textOverflow": "ellipsis",
            "fontSize": "12px",
            "fontFamily": "'Arial', 'Helvetica', sans-serif",
            "color": "#333",
            "fontWeight": "500",
            "padding": "10px",
            "border": "1px solid #ddd",
            "borderLeft": "none",
            "borderRight": "none",
        },
        style_header={
            "backgroundColor": "#189A35",
            "fontWeight": "bold",
            "fontSize": "16px",
            "paddingTop": "12px",
            "paddingBottom": "12px",
            "color": "white",
            "border": "1px solid #ddd",
            "borderLeft": "none",
            "borderRight": "none",
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#f9f9f9",
            },
            {
                "if": {"row_index": "even"},
                "backgroundColor": "#ffffff",
            },
        ],
    )
    map_ann = kwargs["session_state"]["context"]["map_ann"]
    map_ann_subset = map_ann[
        map_ann.columns[~map_ann.columns.str.contains("ID")]
    ]
    map_table = dash_table.DataTable(
        id="datatable-interactivity",
        columns=[{"name": i, "id": i} for i in map_ann_subset.columns],
        data=map_ann_subset.to_dict("records"),
        sort_action="native",
        sort_mode="multi",
        row_selectable="multi",
        page_action="native",
        page_current=0,
        page_size=5,
        style_table={
            "overflowX": "auto",
            "borderRadius": "0.5rem",
            "fontFamily": "'Arial', 'Helvetica', sans-serif",
            "borderCollapse": "collapse",
            "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
            "margin": "20px 0",
            "borderLeft": "none",
            "borderRight": "none",
        },
        style_cell={
            "whiteSpace": "normal",
            "height": "30px",
            "minWidth": "100px",
            "width": "100px",
            "maxWidth": "100px",
            "textAlign": "left",
            "textOverflow": "ellipsis",
            "fontSize": "12px",
            "fontFamily": "'Arial', 'Helvetica', sans-serif",
            "color": "#333",
            "fontWeight": "500",
            "padding": "10px",
            "border": "1px solid #ddd",
            "borderLeft": "none",
            "borderRight": "none",
        },
        style_header={
            "backgroundColor": "#189A35",
            "fontWeight": "bold",
            "fontSize": "16px",
            "paddingTop": "12px",
            "paddingBottom": "12px",
            "color": "white",
            "border": "1px solid #ddd",
            "borderLeft": "none",
            "borderRight": "none",
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#f9f9f9",
            },
            {
                "if": {"row_index": "even"},
                "backgroundColor": "#ffffff",
            },
        ],
    )
    return file_ann_table, map_table


@dash_app_group.expanded_callback(
    dash.dependencies.Output("confirm_delete", "opened"),
    dash.dependencies.Output("notify-container", "children"),
    [
        dash.dependencies.Input("delete-all", "n_clicks"),
        dash.dependencies.Input("modal-submit-button", "n_clicks"),
        dash.dependencies.Input("modal-close-button", "n_clicks"),
        dash.dependencies.State("confirm_delete", "opened"),
    ],
    prevent_initial_call=True,
)
def delete_all_callback(*args, **kwargs):
    triggered_button = kwargs["callback_context"].triggered[0]["prop_id"]
    group_id = kwargs["session_state"]["context"]["group_id"]
    if triggered_button == "modal-submit-button.n_clicks" and args[0] > 0:
        message = "You have clicked the submit button"
    elif triggered_button == "modal-close-button.n_clicks" and args[1] > 0:
        message = "You have clicked the close button"
    else:
        message = "delete all button clicked"
    opened = not args[3]
    return opened, message


@dash_app_group.expanded_callback(
    dash.dependencies.Output("download", "data"),
    dash.dependencies.Input("download_test", "n_clicks"),
    prevent_initial_call=True,
)
def download_file(*args, **kwargs):
    request = kwargs["request"]
    url = views.download_file(request, file_id=691)
    msg = "File downloaded"
    df = pd.read_csv(url)
    return dcc.send_data_frame(df.to_csv, "mydf.csv")
