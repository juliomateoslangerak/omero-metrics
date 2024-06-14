from django.urls import re_path

# import logging
from django.views.generic import (
    TemplateView,
)


from .views import (
    index,
)

urlpatterns = [
    re_path(
        r"^$",
        index,
        name="metrics_index",
    ),
]
