from django.urls import include, path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
# Load demo plotlyapps - this triggers their registration
import omero_metrics.dash_apps.plotly_apps
import omero_metrics.dash_apps.dash_apps
# pylint: disable=unused-import
from django_plotly_dash.views import add_to_session
from .views import dash_example_1_view, session_state_view  #,data_view


from django.urls import re_path

from . import views

from . import views

urlpatterns = [
    # index 'home page' of the app
     re_path(r"^$", views.index, name="metrics_index"),
     re_path('demo-one', TemplateView.as_view(template_name='metrics/demo_one.html'), name="demo-one"),
     re_path('foi_key_measurement', dash_example_1_view, name="foi_key_measurement"),
     # path('data-test', data_view, name="data-test"),
]
