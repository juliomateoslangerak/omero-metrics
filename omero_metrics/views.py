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
    processed_data_project_view
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
        "metrics/index.html",
        context,
    )


@login_required()
def dash_example_1_view(
        request,
        conn=None,
        template_name="metrics/foi_key_measurement.html",
        **kwargs
):
    "Example view that inserts content into the \
    dash context passed to the dash application"
    experimenter = conn.getUser()
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,
    }
    # create some context to send over to Dash:
    dash_context = request.session.get(
        "django_plotly_dash", dict()
    )
    dash_context[
        "django_to_dash_context"
    ] = "I am Dash receiving context from Django"
    request.session[
        "django_plotly_dash"
    ] = dash_context
    return render(
        request,
        template_name=template_name,
        context=context,
    )


@login_required()
def session_state_view(
        request, template_name, **kwargs
):
    "Example view that exhibits the use of sessions to store state"
    session = request.session
    omero_views_count = session.get(
        "django_plotly_dash", {}
    )
    ind_use = omero_views_count.get(
        "ind_use", 0
    )
    ind_use += 1
    omero_views_count["ind_use"] = (
        ind_use
    )
    context = {"ind_use": ind_use}
    session["django_plotly_dash"] = (
        omero_views_count
    )
    return render(
        request,
        template_name=template_name,
        context=context,
    )


def web_gateway_templates(
        request, base_template
):
    """Simply return the named template. Similar functionality to
    django.views.generic.simple.direct_to_template
    """
    template_name = (
        "metrics/web_gateway/%s.html"
        % base_template
    )
    return render(
        request, template_name, {}
    )


@login_required()
@render_response()
def webclient_templates(
        request, base_template, **kwargs
):
    """Simply return the named template. Similar functionality to
    django.views.generic.simple.direct_to_template
    """
    template_name = (
        "metrics/web_gateway/%s.html"
        % base_template
    )
    return {"template": template_name}


@login_required()
def image_rois(
        request,
        image_id,
        conn=None,
        **kwargs
):
    """Simply shows a page of ROI thumbnails for the specified image"""
    roi_ids = image_id
    return render(
        request,
        "metrics/omero_views/image_rois.html",
        {"roiIds": roi_ids},
    )


@login_required()
def center_viewer_image(
        request,
        image_id,
        conn=None,
        **kwargs
):
    dash_context = request.session.get(
        "django_plotly_dash", dict()
    )
    image_wrapper = conn.getObject(
        "Image", image_id
    )
    dm = DatasetManager(
        conn, image_wrapper
    )
    dm.load_data()
    dm.is_processed()
    dm.visualize_data()
    dash_context["context"] = dm.context
    template = dm.template
    request.session[
        "django_plotly_dash"
    ] = dash_context
    return render(
        request, template_name=template
    )


@login_required()
def center_viewer_project(
        request,
        project_id,
        conn=None,
        **kwargs
):
    project_wrapper = conn.getObject(
        "Project", project_id
    )

    (
        processed_datasets,
        unprocessed_datasets,
    ) = get_dataset_ids_lists(
        conn, project_wrapper
    )
    df = processed_data_project_view(
        processed_datasets
    )
    dash_context = request.session.get(
        "django_plotly_dash", dict()
    )
    dash_context["data"] = df
    request.session[
        "django_plotly_dash"
    ] = dash_context
    collections_mm_p = (
        load.load_project(
            conn, project_id
        )
    )
    context = {
        "project_id": project_id,
        "collections_mm_p": collections_mm_p,
    }
    return render(
        request,
        "metrics/omero_views/center_view_project.html",
        context,
    )


@login_required()
def center_viewer_group(
        request, conn=None, **kwargs
):
    group = conn.getGroupFromContext()
    group_id = group.getId()
    group_name = group.getName()
    group_description = (
        group.getDescription()
    )
    context = {
        "group_id": group_id,
        "group_name": group_name,
        "group_description": group_description,
    }
    return render(
        request,
        "metrics/omero_views/center_view_group.html",
        context,
    )


@login_required()
def center_viewer_dataset(
        request,
        dataset_id,
        conn=None,
        **kwargs
):
    dash_context = request.session.get(
        "django_plotly_dash", dict()
    )
    dataset_wrapper = conn.getObject(
        "Dataset", dataset_id
    )
    dm = DatasetManager(
        conn, dataset_wrapper
    )
    dm.load_data()
    dm.is_processed()
    dm.visualize_data()
    dash_context["context"] = dm.context
    template = dm.template
    request.session[
        "django_plotly_dash"
    ] = dash_context
    return render(
        request, template_name=template
    )
