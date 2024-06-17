from django.shortcuts import render
from omeroweb.webclient.decorators import (
    login_required,
)


@login_required()
def index(request, conn=None, **kwargs):
    experimenter = conn.getUser()

    # A dictionary of data to pass to the html template
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,
    }
    return render(request, "omero_metrics/index.html", context)
