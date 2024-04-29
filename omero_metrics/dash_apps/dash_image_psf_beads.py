import uuid
import random
from datetime import datetime
import pandas as pd
from django.core.cache import cache
from django.utils.translation import gettext, gettext_lazy
import dash
from dash import Dash, dcc, html, Input, Output, callback,dash_table
from dash.dependencies import MATCH, ALL
import plotly.graph_objs as go
import dpd_components as dpd
from dash.exceptions import PreventUpdate
from django_plotly_dash import DjangoDash
from django_plotly_dash.consumers import send_to_pipe_channel
import plotly.express as px
import dash_mantine_components as dmc


c1 = "#d8f3dc"
c2 = "#eceff1"
c3 = "#63aa47"



app = DjangoDash('PSF_Beads_image')

app.layout = dmc.MantineProvider(
     children=[dmc.Container([
      html.Div(id='blank-input', children=[]),
      dmc.Center(
                dmc.Text(
                "PSF Beads Dashboard for Image",
         
                mb=30,
                style={"margin-top": "20px", "fontSize": 40},
            )
        ),

])
])
