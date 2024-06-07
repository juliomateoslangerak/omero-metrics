import dash
from dash import dcc, html, dash_table
import plotly.graph_objs as go
import numpy as np
from django_plotly_dash import DjangoDash
import plotly.express as px
from ..tools.data_preperation import *
import dash_mantine_components as dmc


app_name = 'omero_project_render_dash'

dash_app_project_render = DjangoDash(name=app_name, serve_locally=True,)

dash_app_project_render.layout = dmc.MantineProvider([])


@dash_app_project_render.expanded_callback()
def callback_project_render(*args, **kwargs):
    pass