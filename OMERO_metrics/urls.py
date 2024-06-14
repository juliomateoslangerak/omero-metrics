from django.urls import re_path

# import logging
from django.views.generic import (
    TemplateView,
)


from .views import (
    index,
    dash_example_1_view,
    web_gateway_templates,
    webclient_templates,
    center_viewer_project,
    center_viewer_dataset,
    center_viewer_group,
    center_viewer_image,
    image_rois,
)

urlpatterns = [
    re_path(
        r"^$",
        index,
        name="metrics_index",
    ),
]
