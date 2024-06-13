from django.views.generic import TemplateView
from omero_metrics.dash_apps import foi_apps, plotly_apps, dash_apps, dash_image, dash_project, dash_dataset_psf_beads, dash_image_psf_beads, dash_dataset_metrics
from .views import *
from django.urls import re_path

urlpatterns = [
    re_path(r"^$", index, name="metrics_index"),
    re_path(r'^demo-one', TemplateView.as_view(template_name='metrics/demo_one.html'), name="demo-one"),
    re_path(r'^foi_key_measurement', dash_example_1_view, name="foi_key_measurement"),
    re_path(r'^webgateway_templates/(?P<base_template>[a-z0-9_]+)/', web_gateway_templates, name='webgateway_templates'),
    re_path(r'^webclient_templates/(?P<base_template>[a-z0-9_]+)/', webclient_templates, name='webclient_templates'),
    re_path(r'^project/(?P<project_id>[0-9]+)/', center_viewer_project, name='project'),
    re_path(r'^dataset/(?P<dataset_id>[0-9]+)/', center_viewer_dataset, name='dataset'),
    re_path(r'^group/', center_viewer_group, name='group'),
    re_path(r'^image/(?P<image_id>[0-9]+)/', center_viewer_image, name='image'),
    re_path(r'^image_rois/(?P<image_id>[0-9]+)/', image_rois, name='webtest_image_rois'),
    #re_path(r'^(?P<data_type>[a-z]+)/(?P<image_id>[0-9]+)/, session_state_view, name='session_state'),
]
