import dash
from dash import dcc, html, dash_table
from django_plotly_dash import DjangoDash
import plotly.express as px
import dash_mantine_components as dmc
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

c1 = "#d8f3dc"
c2 = "#eceff1"
c3 = "#63aa47"

app = DjangoDash('PSF_Beads')

app.layout = dmc.MantineProvider(
    children=[dmc.Container([
        html.Div(id='blank-input', children=[]),
        html.Div(children=[dcc.Graph(id="image", figure={})]),
        html.Div(children=[dcc.Graph(id="mip", figure={})]),
        html.Div(children=[dash_table.DataTable(
            id="table1",
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
        ), ]),
        html.Div(children=[dash_table.DataTable(
            id="table2",
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
        ), ]),
        html.Div(children=[dash_table.DataTable(
            id="table3",
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
        ), ]),
        html.Div(children=[dash_table.DataTable(
            id="table4",
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
        ), ]),
    ])])


@app.expanded_callback(
dash.dependencies.Output('image', 'figure'),
    dash.dependencies.Output('mip', 'figure'),
    dash.dependencies.Output('table1', 'data'),
    dash.dependencies.Output('table2', 'data'),
    dash.dependencies.Output('table3', 'data'),
    dash.dependencies.Output('table4', 'data'),
    [dash.dependencies.Input('blank-input', 'children'), ])
def func_psf_callback(*args, **kwargs):
    #TZYXC
    image_o = kwargs['session_state']['image']
    image = image_o[0, 30, :, :, 0]
    stack = image_o[0, :, :, :, 0]
    image_Z = px.imshow(np.max(stack, axis=0), zmin=image.min(), zmax=image.max(), color_continuous_scale="gray")
    image_X = px.imshow(np.max(stack, axis=2), zmin=image.min(), zmax=image.max(), color_continuous_scale="gray")
    image_Y = px.imshow(np.max(stack, axis=1), zmin=image.min(), zmax=image.max(), color_continuous_scale="gray")
    bead_properties_df = kwargs['session_state']['bead_properties_df']
    bead_x_profiles_df = kwargs['session_state']['bead_x_profiles_df']
    bead_y_profiles_df = kwargs['session_state']['bead_y_profiles_df']
    bead_z_profiles_df = kwargs['session_state']['bead_z_profiles_df']
    fig1 = px.imshow(image, zmin=image.min(), zmax=image.max(), color_continuous_scale="gray")
    #fig = make_subplots(rows=2, cols=2, specs=[[{}, {}], [{"colspan": 2}, None]],
    #                    subplot_titles=("MIP X axis", "MIP Y axis", "MIP Z axis"))
    fig = go.Figure().set_subplots(2, 2, horizontal_spacing=0.1)
    fig = fig.add_trace(image_X, row=1, col=1)
    fig = fig.add_trace(image_Y, row=1, col=2)
    fig = fig.add_trace(image_Z, row=2, col=1)
    fig = fig.update_layout(showlegend=False, title_text="Maximum Intensity Projection")
    return fig1, fig, bead_properties_df.to_dict('records'), bead_x_profiles_df.to_dict('records'), bead_y_profiles_df.to_dict('records'), bead_z_profiles_df.to_dict('records')
