from omero_metrics.views import (
    index,
    microscope_view,
    center_viewer_project,
    center_viewer_dataset,
    center_viewer_group,
    center_viewer_image,
    imageJ,
    center_view_projects,
)
from django.urls import re_path
from omero_metrics.dash_apps import (
    dash_feedback,
    dash_group,
    dash_project,
    dash_microscope,
)
from omero_metrics.dash_apps.dash_forms import (
    dash_group_form,
    dash_project_form,
    dash_dataset_form,
)
from omero_metrics.dash_apps.dash_analyses.dash_foi import (
    dash_dataset_foi,
    dash_image_foi,
)
from omero_metrics.dash_apps.dash_analyses.dash_psf_beads import (
    dash_dataset_psf_beads,
    dash_image_psf_beads,
)
from omero_metrics.dash_apps.dash_multiple_projects import dash_projects

urlpatterns = [
    re_path(r"^$", index, name="omero_metrics_index"),
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
        r"^omero_metrics_projects/",
        center_view_projects,
        name="omero_metrics_projects",
    ),
    # This url is for the app in a new tab
    re_path(r"^microscope/", microscope_view, name="microscope"),
    re_path(r"^imageJ_test/", imageJ, name="imageJ_test"),
]
