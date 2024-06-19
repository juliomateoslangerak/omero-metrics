#!/usr/bin/env python
#
# Copyright (c) 2024 University of Dundee.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from . import views
from django.urls import re_path
from .views import (
    web_gateway_templates,
    webclient_templates,
    center_viewer_group,
    image_rois,
)

urlpatterns = [
    # index 'home page' of the app
    re_path(r"^$", views.index, name="OMERO_metrics_index"),
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
    re_path(r"^group/", center_viewer_group, name="group"),
    re_path(
        r"^image_rois/(?P<image_id>[0-9]+)/",
        image_rois,
        name="webtest_image_rois",
    ),
]
