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

from django.shortcuts import render
from omeroweb.webclient.decorators import login_required, render_response


# login_required: if not logged-in, will redirect to webclient
# login page. Then back to here, passing in the 'conn' connection
# and other arguments **kwargs.
@login_required()
def index(request, conn=None, **kwargs):
    # We can load data from OMERO via Blitz Gateway connection.
    # See https://docs.openmicroscopy.org/latest/omero/developers/Python.html
    experimenter = conn.getUser()

    # A dictionary of data to pass to the html template
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,
    }
    # print can be useful for debugging, but remove in production
    # print('context', context)

    # Render the html template and return the http response
    return render(request, "OMERO_metrics/index.html", context)


@login_required()
def web_gateway_templates(request, base_template, **kwargs):
    """Simply return the named template. Similar functionality to
    django.views.generic.simple.direct_to_template"""
    template_name = "OMERO_metrics/web_gateway/%s.html" % base_template
    return render(request, template_name, {})


@login_required()
@render_response()
def webclient_templates(request, base_template, **kwargs):
    """Simply return the named template. Similar functionality to
    django.views.generic.simple.direct_to_template"""
    template_name = "OMERO_metrics/web_gateway/%s.html" % base_template
    return {"template": template_name}


@login_required()
def center_viewer_group(request, conn=None, **kwargs):
    group = conn.getGroupFromContext()
    group_id = group.getId()
    group_name = group.getName()
    group_description = group.getDescription()
    context = {
        "group_id": group_id,
        "group_name": group_name,
        "group_description": group_description,
    }
    return render(
        request, "OMERO_metrics/omero_views/center_view_group.html", context
    )


@login_required()
def image_rois(request, image_id, conn=None, **kwargs):
    """Simply shows a page of ROI thumbnails for the specified image"""
    roi_ids = image_id
    return render(
        request,
        "OMERO_metrics/omero_views/image_rois.html",
        {"roiIds": roi_ids},
    )
