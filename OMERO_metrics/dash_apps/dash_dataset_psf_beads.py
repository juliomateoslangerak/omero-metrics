import dash
from dash import dcc, html, dash_table
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc


app = DjangoDash("PSF_Beads")

app.layout = dmc.MantineProvider(
    [
        dmc.Container(
            [
                dmc.Center(
                    dmc.Text(
                        "PSF Beads Dashboard",
                        c="#189A35",
                        style={"fontSize": 20},
                    )
                ),
                dmc.Grid(
                    [
                        dmc.GridCol(
                            [
                                dmc.Title(
                                    "Key Measurements",
                                    c="#189A35",
                                    size="h3",
                                    mb=10,
                                ),
                                dash_table.DataTable(
                                    id="key_values_psf",
                                    page_size=10,
                                    sort_action="native",
                                    sort_mode="multi",
                                    sort_as_null=["", "No"],
                                    sort_by=[
                                        {
                                            "column_id": "pop",
                                            "direction": "asc",
                                        }
                                    ],
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
                                    style_table={"overflowX": "auto"},
                                ),
                            ],
                            span="6",
                        ),
                    ]
                ),
            ],
            fluid=True,
            style={
                "background-color": "#eceff1",
                "margin": "20px",
                "border-radius": "0.5rem",
                "padding": "10px",
            },
        )
    ]
)


@app.expanded_callback(
    dash.dependencies.Output("channel_psf", "options"),
    dash.dependencies.Output("key_values_psf", "data"),
    [
        dash.dependencies.Input("channel_psf", "value"),
    ],
)
def func_psf_callback(*args, **kwargs):
    channel_index = int(args[0].split(" ")[-1])
    km = kwargs["session_state"]["context"]["bead_km_df"]
    km = km.sort_values(by="channel_nr", ascending=True).reset_index(drop=True)
    km = km.pivot_table(columns="channel_name")
    km = km.reset_index(drop=False, names="Measurement")

    channel_names = kwargs["session_state"]["context"]["channel_names"]
    channel_list_psf = [
        {"label": c.name, "value": f"channel {i}"}
        for i, c in enumerate(channel_names.channels)
    ]
    bead_properties_df = kwargs["session_state"]["context"][
        "bead_properties_df"
    ]

    return (
        channel_list_psf,
        bead_properties_df.to_dict("records"),
    )
