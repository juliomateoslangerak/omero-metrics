from django.urls import re_path
from .views import (
    index,
)

urlpatterns = [
    re_path(
        r"^$",
        index,
        name="OMERO_metrics_index",
    ),
]
