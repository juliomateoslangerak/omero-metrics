from django.shortcuts import render
from omeroweb.webclient.decorators import (
    login_required,
    render_response,
)

from .tools import load
from .tools.data_managers import (
    DatasetManager,
)
from .tools.data_preperation import (
    get_dataset_ids_lists,
    processed_data_project_view,
)


@login_required()
def index(request, conn=None, **kwargs):
    experimenter = conn.getUser()
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,
    }
    return render(
        request,
        "OMERO_metrics/templates/OMERO_metrics/index.html",
        context,
    )
