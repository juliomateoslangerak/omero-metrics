#
# Copyright (c) 2017 University of Dundee.
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
# from .tools import get_info_dash
from omeroweb.decorators import login_required
from omero_metrics.tools.load import load_image
# from .tools import data_loader

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
    return render(request, "metrics/index.html", context)



@login_required()
def dash_example_1_view(request, conn=None, template_name="metrics/foi_key_measurement.html", **kwargs):
    'Example view that inserts content into the dash context passed to the dash application'
    experimenter = conn.getUser()
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,

    }
    # create some context to send over to Dash:
    dash_context = request.session.get("django_plotly_dash", dict())
    dash_context['django_to_dash_context'] = "I am Dash receiving context from Django"
    request.session['django_plotly_dash'] = dash_context
    return render(request, template_name=template_name, context=context, )


def session_state_view(request, template_name, **kwargs):
    'Example view that exhibits the use of sessions to store state'

    session = request.session

    demo_count = session.get('django_plotly_dash', {})

    ind_use = demo_count.get('ind_use', 0)
    ind_use += 1
    demo_count['ind_use'] = ind_use

    context = {'ind_use' : ind_use}

    session['django_plotly_dash'] = demo_count

    return render(request, template_name=template_name, context=context)



# @login_required()
# def data_view(request, conn=None, **kwargs):
#     g = conn.listGroups()
#     for i in g:
#         group_id=i.getId()
#     conn.SERVICE_OPTS.setOmeroGroup(group_id)
#     data_loader(conn, 10, 'Fake data')
#     return render(request, template_name='metrics/add_data.html', context={})
    