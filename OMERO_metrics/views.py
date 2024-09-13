from omeroweb.webclient.decorators import login_required, render_response
from .tools.data_managers import DatasetManager, ProjectManager, ImageManager
from django.shortcuts import render
from .forms import UploadFileForm
import numpy as np
from .tools.omero_tools import create_image_from_numpy_array


def test_request(request):
    if request.method == "POST":
        test = request.POST.get("test")
        context = {"test": test}
        return render(request, "OMERO_metrics/test.html", context)


# Imaginary function to handle an uploaded file.
@login_required()
def upload_image(request, conn=None, **kwargs):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            title = form.cleaned_data["title"]
            dataset_id = form.cleaned_data["dataset_id"]
            dataset = conn.getObject("Dataset", int(dataset_id))
            group_id = dataset.getDetails().getGroup().getId()
            conn.SERVICE_OPTS.setOmeroGroup(group_id)
            type = file.name
            ima = np.load(file)
            image = ima.transpose((1, 4, 0, 2, 3))
            ima_wrapper = create_image_from_numpy_array(
                conn, image, title, dataset=dataset
            )
            id = ima_wrapper.getId()
        return render(
            request,
            "OMERO_metrics/success.html",
            {"type": type, "id_dataset": dataset.getId(), "id_image": id},
        )
    else:
        form = UploadFileForm()
    return render(
        request, "OMERO_metrics/upload_image_omero.html", {"form": form}
    )


@login_required()
def index(request, conn=None, **kwargs):
    experimenter = conn.getUser()
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,
    }
    return render(request, "OMERO_metrics/index.html", context)


@login_required()
def dash_example_1_view(
    request,
    conn=None,
    template_name="OMERO_metrics/foi_key_measurement.html",
    **kwargs
):
    """Example view that inserts content into the
    dash context passed to the dash application"""
    experimenter = conn.getUser()
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,
    }
    # create some context to send over to Dash:
    dash_context = request.session.get("django_plotly_dash", dict())
    dash_context["django_to_dash_context"] = (
        "I am Dash receiving context from Django"
    )
    request.session["django_plotly_dash"] = dash_context
    return render(
        request,
        template_name=template_name,
        context=context,
    )


@login_required()
def session_state_view(request, template_name, **kwargs):
    "Example view that exhibits the use of sessions to store state"
    session = request.session
    omero_views_count = session.get("django_plotly_dash", {})
    ind_use = omero_views_count.get("ind_use", 0)
    ind_use += 1
    omero_views_count["ind_use"] = ind_use
    context = {"ind_use": ind_use}
    session["django_plotly_dash"] = omero_views_count
    return render(request, template_name=template_name, context=context)


def web_gateway_templates(request, base_template):
    """Simply return the named template. Similar functionality to
    django.views.generic.simple.direct_to_template"""
    template_name = "OMERO_metrics/web_gateway/%s.html" % base_template
    return render(request, template_name, {})


@login_required()
@render_response()
def webclient_templates(request, base_template, **kwargs):
    """Simply return the named template.
    Similar functionality to
    django.views.generic.simple.direct_to_template"""
    template_name = "OMERO_metrics/web_gateway/%s.html" % base_template
    return {"template": template_name}


@login_required()
def image_rois(request, image_id, conn=None, **kwargs):
    """Simply shows a page of ROI
    thumbnails for the specified image"""
    roi_ids = image_id
    return render(
        request,
        "OMERO_metrics/omero_views/image_rois.html",
        {"roiIds": roi_ids},
    )


@login_required()
def center_viewer_image(request, image_id, conn=None, **kwargs):
    dash_context = request.session.get("django_plotly_dash", dict())
    image_wrapper = conn.getObject("Image", image_id)
    im = ImageManager(conn, image_wrapper)
    im.load_data()
    im.visualize_data()
    dash_context["context"] = im.context
    template = im.template
    request.session["django_plotly_dash"] = dash_context
    return render(request, template_name=template)


@login_required()
def center_viewer_project(request, project_id, conn=None, **kwargs):
    # request["conn"] = conn
    # conn.SERVICE_OPTS.setOmeroGroup("-1")

    project_wrapper = conn.getObject("Project", project_id)
    pm = ProjectManager(conn, project_wrapper)
    pm.load_data()
    pm.is_homogenized()
    pm.load_config_file()
    pm.check_processed_data()
    pm.visualize_data()
    context = pm.context
    template = pm.template
    dash_context = request.session.get("django_plotly_dash", dict())
    dash_context["context"] = context
    # dash_context["context"]["project_id"] = project_id
    request.session["django_plotly_dash"] = dash_context
    return render(request, template_name=template, context=context)


@login_required()
def center_viewer_group(request, conn=None, **kwargs):
    group2 = conn.SERVICE_OPTS.getOmeroGroup()
    group = conn.getGroupFromContext()
    group_id = group.getId()
    group_name = group.getName()
    group_description = group.getDescription()
    context = {
        "group_id": group_id,
        "group_name": group2,
        "group_description": group_description,
    }
    return render(
        request, "OMERO_metrics/omero_views/center_view_group.html", context
    )


@login_required()
def center_viewer_dataset(request, dataset_id, conn=None, **kwargs):
    dash_context = request.session.get("django_plotly_dash", dict())
    dataset_wrapper = conn.getObject("Dataset", dataset_id)
    dm = DatasetManager(conn, dataset_wrapper, load_images=True)
    dm.load_data()
    dm.is_processed()
    dm.visualize_data()
    dash_context["context"] = dm.context
    template = dm.template
    request.session["django_plotly_dash"] = dash_context
    return render(request, template_name=template)


@login_required()
def microscope_view(request, conn=None, **kwargs):
    """Simply shows a page of ROI thumbnails for
    the specified image"""
    return render(request, "OMERO_metrics/microscope.html")


@login_required()
def run_analysis(request, conn=None, **kwargs):
    """Simply shows a page of ROI thumbnails
    for the specified image"""
    return render(request, "OMERO_metrics/run_analysis.html")
