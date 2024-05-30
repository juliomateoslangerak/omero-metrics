import dash
from dash import dcc, html, dash_table
from django_plotly_dash import DjangoDash
import plotly.express as px
import dash_mantine_components as dmc
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from ..tools.data_preperation import numpyToVTK
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

c1 = "#d8f3dc"
c2 = "#eceff1"
c3 = "#63aa47"

app = DjangoDash('PSF_Beads')

app.layout = dmc.MantineProvider([dmc.Container(
    [dmc.Center(
        dmc.Text("PSF Beads Dashboard",
                 c="#189A35",
                 mb=30,
                 style={"margin-top": "20px", "fontSize": 40},
                 )
    ),
        dmc.Stack(
            [dmc.Grid([dmc.GridCol([dcc.Dropdown(value="Channel 0", id="channel_ddm_psf")], span='auto'),
                       dmc.GridCol([dcc.Dropdown(value="Bead 0", id="bead_ddm_psf")], span='auto')]),

             dmc.Grid([
                 dmc.GridCol([dmc.Title("Image View", c="#189A35", size="h3", mb=10),
                              dcc.Graph(id="image", figure={},
                                        style={'display': 'inline-block', 'width': '100%', 'height': '100%;'}),
                              ], span="6"),
                 dmc.GridCol([
                     dmc.Title("Key Values", c="#189A35", size="h3", mb=10),
                     dash_table.DataTable(
                         id="key_values_psf",
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

             dmc.Grid([
                 dmc.GridCol([dmc.Title("Maximum Intensity Projection", c="#189A35", size="h3", mb=10),
                              dcc.Graph(id="mip", figure={},
                                        style={'display': 'inline-block', 'width': '100%', 'height': '100%;'}),
                              ], span="6"),
                 dmc.GridCol([
                     dmc.Title("Chart", c="#189A35", size="h3", mb=10),
                     dcc.Dropdown(options=['Axis: X', 'Axis: Y', 'Axis: Z'], value="Axis: X", id="axis_ddm_psf"),
                     dcc.Graph(id="mip_chart", figure={},
                               style={'display': 'inline-block', 'width': '100%', 'height': '100%;'}),
                 ], span="6"),

             ]),

             dmc.Stack(
                 [
                     dmc.Title(
                         "Key Measurements", c="#189A35", size="h3", mb=10
                     ),
                     dash_table.DataTable(
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
                         style_table={'overflowX': 'auto'},
                     ),
                 ]
             )
             ]),
    ],
    fluid=True,
)])


@app.expanded_callback(
    dash.dependencies.Output('image', 'figure'),
    dash.dependencies.Output('mip', 'figure'),
    dash.dependencies.Output('channel_ddm_psf', 'options'),
    dash.dependencies.Output('bead_ddm_psf', 'options'),
    dash.dependencies.Output('table1', 'data'),
    dash.dependencies.Output('key_values_psf', 'data'),
    dash.dependencies.Output('mip_chart', 'figure'),

    [dash.dependencies.Input('channel_ddm_psf', 'value'),
     dash.dependencies.Input('bead_ddm_psf', 'value'),
     dash.dependencies.Input('axis_ddm_psf', 'value'), ])
def func_psf_callback(*args, **kwargs):
    #TZYXC
    channel_index = int(args[0].split(" ")[-1])
    bead_index = int(args[1].split(" ")[-1])
    image_o = kwargs['session_state']['image']
    channels = [f"Channel {i}" for i in range(0, image_o.shape[4])]
    stack = image_o[0, :, :, :, channel_index]
    bead_properties_df = kwargs['session_state']['bead_properties_df']
    #------------------------Data Table 1--------------------------------
    df_properties_channel = bead_properties_df[bead_properties_df['channel_nr'] == channel_index][
        ['bead_nr', 'intensity_max',
         'min_intensity_min', 'intensity_std', 'intensity_robust_z_score',
         'considered_intensity_outlier', 'z_fit_r2', 'y_fit_r2', 'x_fit_r2',
         'z_fwhm', 'y_fwhm', 'x_fwhm', 'fwhm_lateral_asymmetry_ratio']].copy()
    df_beads_location = bead_properties_df[bead_properties_df['channel_nr'] == 0][
        ['bead_nr', 'z_centroid', 'y_centroid', 'x_centroid']].copy()
    bead = df_beads_location[df_beads_location['bead_nr'] == bead_index].copy()
    x = bead['x_centroid'].values[0] + 20
    y = bead['y_centroid'].values[0] + 20
    z = bead['z_centroid'].values[0]
    y0 = y - 40
    x0 = x - 40
    image_bead = stack[:, y0:y, x0:x]
    z_ima = stack[z, y0:y, x0:x]
    #image_Z = np.max(stack, axis=0)
    image_X = np.max(image_bead, axis=2)
    image_Y = np.max(image_bead, axis=1)
    image_X = 255 * (image_X / image_X.max())
    image_Y = 255 * (image_Y / image_Y.max())
    image_Z = 255 * (z_ima / z_ima.max())
    mip_X = px.imshow(image_X, zmin=image_X.min(), zmax=image_X.max(), color_continuous_scale="gray")
    mip_Y = px.imshow(image_Y, zmin=image_Y.min(), zmax=image_Y.max(), color_continuous_scale="gray")
    mip_Z = px.imshow(image_Z, zmin=image_Z.min(), zmax=image_Z.max(), color_continuous_scale="gray")
    fig = make_subplots(rows=2, cols=2, specs=[[{}, {}],
                                               [{"colspan": 2}, None]],
                        subplot_titles=("MIP X axis", "MIP Y axis", "MIP Z axis"))
    fig = fig.add_trace(mip_X.data[0], row=1, col=1)
    fig = fig.add_trace(mip_Y.data[0], row=1, col=2)
    fig = fig.add_trace(mip_Z.data[0], row=2, col=1)
    fig = fig.update_layout(title_text="MIP for each axis", )
    axis = args[2].split(" ")[-1].lower()
    df_axis = kwargs['session_state'][f'bead_{axis}_profiles_df']
    df_meta_x = pd.DataFrame(
        data=[[int(col.split("_")[-2]), int(col.split("_")[-4]), col.split("_")[-1], col] for col in
              df_axis.columns], columns=['bead_nb', 'channel_nb', 'type', 'name'])

    cols_x = df_meta_x[((df_meta_x['bead_nb'] == bead_index) & (df_meta_x['channel_nb'] == channel_index))][
        'name'].values
    df_x = df_axis[cols_x].copy()
    fig_ip_x = px.line(df_x)
    beads_opt = [f"Bead {i}" for i in df_beads_location['bead_nr'].values]
    ima_3d = image_o[0, :, :, :, channel_index]
    image_bead = image_bead / image_bead.max()
    lz, ly, lx = image_bead.shape
    Z, Y, X = np.mgrid[:lz, :ly, :lx]
    test_v = go.Figure(data=go.Volume(
        x=Z.flatten(), y=Y.flatten(), z=X.flatten(),
        value=image_bead.flatten(),
        isomin=0.2,
        isomax=0.7,
        opacity=0.1,
        surface_count=25,
    ))
    test_v = test_v.update_layout(scene_xaxis_showticklabels=False,
                                  scene_yaxis_showticklabels=False,
                                  scene_zaxis_showticklabels=False)
    return test_v, fig, channels, beads_opt, bead_properties_df.to_dict('records'), df_properties_channel.to_dict(
        'records'), fig_ip_x
