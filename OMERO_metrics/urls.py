from OMERO_metrics.views import *
from django.urls import re_path
from OMERO_metrics.dash_apps import (
    dash_image_foi,
    dash_project,
    dash_dataset_psf_beads,
    dash_image_psf_beads,
    dash_dataset_foi,
    dash_group,
    dash_microscope,
    dash_forms,
    dash_dataset_form,
    dash_feedback,
)

urlpatterns = [
    re_path(r"^$", index, name="OMERO_metrics_index"),
    re_path(
        r"^webgateway_templates/(?P<base_template>[a-z0-9_]+)/",
        web_gateway_templates,
        name="webgateway_templates",
    ),
    re_path(
        r"^webclient_templates/(?P<base_template>[a-z0-9_]+)/",
        webclient_templates,
        name="webclient_templates",
    ),
    re_path(
        r"^project/(?P<project_id>[0-9]+)/",
        center_viewer_project,
        name="project",
    ),
    re_path(
        r"^dataset/(?P<dataset_id>[0-9]+)/",
        center_viewer_dataset,
        name="dataset",
    ),
    re_path(r"^group/", center_viewer_group, name="group"),
    re_path(
        r"^image/(?P<image_id>[0-9]+)/", center_viewer_image, name="image"
    ),
    re_path(
        r"^image_rois/(?P<image_id>[0-9]+)/",
        image_rois,
        name="webtest_image_rois",
    ),
    re_path(r"^microscope", microscope_view, name="microscope"),
    re_path(r"^upload_image", upload_image, name="upload_image"),
]
