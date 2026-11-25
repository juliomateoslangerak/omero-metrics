from django.urls import re_path

from omero_metrics.views import (
    center_view_projects,
    chromagnon_apply_progress,
    chromagnon_apply_view,
    dataset_analysis_progress,
    center_viewer_dataset,
    center_viewer_group,
    center_viewer_image,
    center_viewer_project,
    imageJ,
    index,
    microscope_view,
)

urlpatterns = [
    re_path(r"^$", index, name="omero_metrics_index"),
    re_path(r"^group/", center_viewer_group, name="group"),
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
    re_path(r"^image/(?P<image_id>[0-9]+)/", center_viewer_image, name="image"),
    re_path(
        r"^omero_metrics_projects/",
        center_view_projects,
        name="omero_metrics_projects",
    ),
    # This url is for the app in a new tab
    re_path(r"^microscope/", microscope_view, name="microscope"),
    re_path(r"^imageJ_test/", imageJ, name="imageJ_test"),
    # Apply a saved Chromagnon correction to other images (center plugin)
    re_path(r"^chromagnon/$", chromagnon_apply_view, name="chromagnon_apply"),
    re_path(
        r"^chromagnon/progress/(?P<key>[A-Za-z0-9_]+)/",
        chromagnon_apply_progress,
        name="chromagnon_apply_progress",
    ),
    # Live progress of a running analysis, polled by the dataset form
    re_path(
        r"^progress/(?P<dataset_id>[0-9]+)/",
        dataset_analysis_progress,
        name="dataset_analysis_progress",
    ),
]
