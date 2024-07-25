import dash_mantine_components as dmc
from dash import dcc, html
import plotly.graph_objs as go
import numpy as np


def layout_utility(image, df, channels):
    fig = go.FigureWidget()
