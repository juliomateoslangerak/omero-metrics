from django.shortcuts import render
from omeroweb.webclient.decorators import (
    login_required,
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
        "OMERO_metrics/index.html",
        context,
    )
