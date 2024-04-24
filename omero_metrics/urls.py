from django.urls import include, path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
# Load demo plotlyapps - this triggers their registration
from omero_metrics.dash_apps import * 
from omero_metrics.dash_apps import foi_apps
from omero_metrics.dash_apps import plotly_apps
from omero_metrics.dash_apps import dash_apps
from omero_metrics.dash_apps import dash_image
from omero_metrics.dash_apps import dash_project
from omero_metrics.dash_apps import dash_dataset_psf_beads
# pylint: disable=unused-import
from django_plotly_dash.views import add_to_session
from .views import *

from django.urls import re_path



urlpatterns = [
    # index 'home page' of the app
     re_path(r"^$", index, name="metrics_index"),
     re_path('demo-one', TemplateView.as_view(template_name='metrics/demo_one.html'), name="demo-one"),
     re_path('foi_key_measurement', dash_example_1_view, name="foi_key_measurement"),
     re_path(r'^webgateway_templates/(?P<base_template>[a-z0-9_]+)/',webgateway_templates, name='webgateway_templates'),
     re_path(r'^webclient_templates/(?P<base_template>[a-z0-9_]+)/',webclient_templates, name='webclient_templates'),
     re_path(r'^project/(?P<project_id>[0-9]+)/',center_viewer_project , name='project'),
     re_path(r'^dataset/(?P<dataset_id>[0-9]+)/',center_viewer_dataset , name='dataset'),
     re_path(r'^group/',center_viewer_group , name='group'),
     re_path(r'^image/(?P<image_id>[0-9]+)/',center_viewer_image , name='image'),
     re_path(r'^image_rois/(?P<image_id>[0-9]+)/',image_rois, name='webtest_image_rois'),
]
