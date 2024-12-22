
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/MontpellierRessourcesImagerie/OMERO-metrics/omero_plugin.yml)
![GitHub License](https://img.shields.io/github/license/MontpellierRessourcesImagerie/OMERO-metrics)

<img alt="OMERO-metrics logo" height="100" src="OMERO_metrics/static/OMERO_metrics/images/metrics_logo.png"/>

This project is financed by [France BioImaging](https://france-bioimaging.org/).

<img alt="FBI logo" height="100" src="docs/slides/media/logo_FBI.png"/>


An OMERO webapp to follow microscope performance over time.

The following instructions are for Linux. Instructions for other OSs will be added soon.

# Installation on your OMERO-web server instance

To be completed

# Try OMERO-metrics using docker

Install docker and docker-compose on your computer following the instructions on the [docker website](https://docs.docker.com/get-docker/).

Clone the repository:
```bash
$ git clone https://github.com/MontpellierRessourcesImagerie/OMERO-metrics.git
$ cd OMERO-metrics
```

Run the following command to start the server:

```bash
$ docker compose up -d
```

Wait for the server to start and then go to <http://localhost:5080/> in your server.

Before trying anything, you need to generate users, and import some data, etc. If you wish, you can do that 
automatically. To do so you need to install the python environment and run a script that will generate some data for you.

```bash
python -m venv my_venv
source my_venv/bin/activate
pip install -e .
cd test/omero-server
python structure_generator.py
```

Go to <http://localhost:5080/> and log in with the following credentials:
- Username: Asterix
- Password: abc123

# Installation for development

Here we explain how to install OMERO-metrics using an OMERO-web server running locally. The main advantage is
that you may edit the code and debug very easily.

## Pre-requirements

You need to make sure that Python (version 3.9, 3.10 or 3.11) is installed in your computer.

## Configuration

Clone the repository and create a virtual environment to run your server in

```bash
git clone https://github.com/MontpellierRessourcesImagerie/OMERO-metrics.git
cd OMERO-metrics
python -m venv my_venv
source my_venv/bin/activate
pip install -e .
```

We created a little bash script that is configuring the setup. You can run it by typing:

```bash
# Add these additional configurations using the terminal:

export OMERODIR=$(pwd)
config append omero.web.apps '"OMERO_metrics"'
config append omero.web.apps '"dpd_static_support"'
config append omero.web.apps '"django_plotly_dash"'
config append omero.web.apps '"bootstrap4"'
config append omero.web.apps '"corsheaders"'
config append omero.web.ui.top_links '["Metrics", "OMERO_metrics_index", {"title": "Open app in new tab", "target": "_blank"}]'
config set omero.web.debug True
config append omero.web.middleware '{"index": 0.5, "class": "corsheaders.middleware.CorsMiddleware"}'
config append omero.web.middleware '{"index": 10, "class": "corsheaders.middleware.CorsPostCsrfMiddleware"}'
config set omero.web.cors_origin_allow_all True
config set omero.web.databases '{"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "/opt/omero/web/mydatabase"}}'
config append omero.web.middleware '{"index": 7, "class": "django_plotly_dash.middleware.ExternalRedirectionMiddleware"}'
config append omero.web.middleware '{"index": 0.5, "class": "whitenoise.middleware.WhiteNoiseMiddleware"}'
config append omero.web.middleware '{"index": 8, "class": "django_plotly_dash.middleware.BaseMiddleware"}'
config append omero.web.middleware '{"index":0.1, "class": "OMERO_metrics.middleware.OmeroAuth"}'
config append omero.web.ui.center_plugins '["Metrics View", "OMERO_metrics/webclient_plugins/center_plugin.metricsview.js.html", "metrics_view_panel"]'
config append omero.web.ui.right_plugins '["ROIs", "OMERO_metrics/webclient_plugins/right_plugin.rois.js.html", "image_roi_tab"]'

# and migrate the database
python manage.py migrate
```

Further Info
============

1.  This app was derived from [cookiecutter-omero-webapp](https://github.com/ome/cookiecutter-omero-webapp).
2.  For further info on depolyment, see [Deployment](https://docs.openmicroscopy.org/latest/omero/developers/Web/Deployment.html)


License
=======

This project, similar to many Open Microscopy Environment (OME) projects, is
licensed under the terms of the AGPL v3.


Copyright
=========

2024 CNRS

