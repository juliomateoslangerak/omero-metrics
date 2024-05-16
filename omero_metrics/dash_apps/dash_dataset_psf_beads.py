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
    image_Z = np.max(stack, axis=0)
    image_X = np.max(stack, axis=2)
    image_Y = np.max(stack, axis=1)
    image_X = 255 * (image_X / image_X.max())
    image_Y = 255 * (image_Y / image_Y.max())
    image_Z = 255 * (image_Z / image_Z.max())
    bead_properties_df = kwargs['session_state']['bead_properties_df']
    bead_x_profiles_df = kwargs['session_state']['bead_x_profiles_df']
    bead_y_profiles_df = kwargs['session_state']['bead_y_profiles_df']
    bead_z_profiles_df = kwargs['session_state']['bead_z_profiles_df']
    fig1 = px.imshow(image, zmin=image.min(), zmax=image.max(), color_continuous_scale="gray")
    mip_X = px.imshow(image_X, zmin=image_X.min(), zmax=image_X.max(), color_continuous_scale="gray")
    mip_Y = px.imshow(image_Y, zmin=image_Y.min(), zmax=image_Y.max(), color_continuous_scale="gray")
    mip_Z = px.imshow(image_Z, zmin=image_Z.min(), zmax=image_Z.max(), color_continuous_scale="gray")
    fig = make_subplots(rows=2, cols=2, specs=[[{}, {}],
                                               [{"colspan": 2}, None]],
                        subplot_titles=("MIP X axis", "MIP Y axis", "MIP Z axis"))
    fig = fig.add_trace(mip_X.data[0], row=1, col=1)
    fig = fig.add_trace(mip_Y.data[0], row=1, col=2)
    fig = fig.add_trace(mip_Z.data[0], row=2, col=1)
    fig = fig.update_layout(title_text="Maximum Intensity Projection")
    return fig1, fig, bead_properties_df.to_dict('records'), bead_x_profiles_df.to_dict(
        'records'), bead_y_profiles_df.to_dict('records'), bead_z_profiles_df.to_dict('records')


def fun_rm(fig):
    fig = fig.update_layout(coloraxis_showscale=False)
    fig = fig.update_xaxes(showticklabels=False)
    fig = fig.update_yaxes(showticklabels=False)
    return fig
