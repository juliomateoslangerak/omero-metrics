import dash
from dash import dcc, html, dash_table
from django_plotly_dash import DjangoDash
import plotly.express as px
import dash_mantine_components as dmc

dashboard_name = 'omero_dataset_metrics'
dash_app_dataset = DjangoDash(name=dashboard_name)

dash_app_dataset.layout = dmc.MantineProvider([dmc.Container(
    [
        dmc.Center(
            dmc.Text(
                id='title',
                c="#189A35",
                style={"fontSize": 30},
            )
        ),
        dmc.Grid(
            [dmc.GridCol(
                [
                    html.H3("Select Channel", style={"color": "#63aa47"}),
                    dcc.Dropdown(value="Channel 0", id="channel_ddm"),
                ],
                span="auto",

            ),
            ],
            style={"margin-top": "20px", "margin-bottom": "20px", "border": "1px solid #63aa47",
                   "padding": "10px", "border-radius": "0.5rem", "background-color": "white", }
        ),
        dmc.Stack(
            [
                dmc.Grid([
                    dmc.GridCol([dmc.Title("Intensity Map", c="#189A35", size="h3", mb=10),
                                 dcc.Graph(id="dataset_image_graph", figure={},
                                           style={'display': 'inline-block', 'width': '100%', 'height': '100%;'}),
                                 ], span="6"),
                    dmc.GridCol([
                        dmc.Title("Key Measurements", c="#189A35", size="h3", mb=10, mt=10),
                        dash_table.DataTable(
                            id="table",
                            page_size=10,
                            sort_action="native",
                            sort_mode="multi",
                            sort_as_null=["", "No"],
                            sort_by=[{"column_id": "pop", "direction": "asc"}],
                            editable=False,
                            style_cell={
                                "textAlign": "left",
                                "fontSize": 10,
                                "font-family": "sans-serif",
                            },
                            style_header={
                                "backgroundColor": "#189A35",
                                "fontWeight": "bold",
                                "fontSize": 15,
                            },
                            style_table={'overflowX': 'auto'},
                        ),

                    ], span="6"),

                ]),

                dmc.Stack(
                    [
                        dmc.Title(
                            "Intensity Profile", c="#189A35", size="h3", mb=10
                        ),
                        dcc.Graph(id="intensity_profile", figure={},
                                  style={'display': 'inline-block', 'width': '100%', 'height': '100%;'}),
                    ]
                )
            ]),
    ],
    fluid=True, style={"background-color": "#eceff1", "margin": "20px", "border-radius": "0.5rem", "padding": "10px"}
)])


@dash_app_dataset.expanded_callback(dash.dependencies.Output('dataset_image_graph', 'figure'),
                                    dash.dependencies.Output('channel_ddm', 'options'),
                                    dash.dependencies.Output('title', 'children'),
                                    dash.dependencies.Output('table', 'data'),
                                    dash.dependencies.Output('intensity_profile', 'figure'),
                                    [dash.dependencies.Input('channel_ddm', 'value')])
def dataset_callback_intensity_map(*args, **kwargs):
    title = kwargs['session_state']['context']['title']
    table = kwargs['session_state']['context']['key_values_df']
    images = kwargs['session_state']['context']['image']
    df_intensity_profiles = kwargs['session_state']['context']['intensity_profiles']
    labels = table.columns[1:].to_list()
    imaaa = images[0, 0, :, :, int(args[0][-1])] / 255
    channel_list = [{'label': labels[i], 'value': f"channel {i}"} for i in range(len(labels))]
    fig = px.imshow(imaaa, zmin=imaaa.min(), zmax=imaaa.max(), color_continuous_scale="gray")
    C = 'Ch0' + args[0][-1]
    df_profile = df_intensity_profiles[df_intensity_profiles.columns[df_intensity_profiles.columns.str.startswith(C)]].copy()
    df_profile.columns = df_profile.columns.str.replace("Ch\d{2}_", "", regex=True)
    df_profile.columns = df_profile.columns.str.replace("_", " ", regex=True)
    df_profile.columns = df_profile.columns.str.title()
    extracted_table_cols = channel_list[int(args[0][-1])]['label']
    table_filtered = table[['Measurements', extracted_table_cols]]
    fig_ip = px.line(df_profile, x=df_profile.index, y=df_profile.columns, title="Intensity Profile")
    return fig, channel_list, title, table_filtered.to_dict('records'), fig_ip
