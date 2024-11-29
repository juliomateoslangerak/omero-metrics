
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/MontpellierRessourcesImagerie/OMERO-metrics/omero_plugin.yml)
![GitHub License](https://img.shields.io/github/license/MontpellierRessourcesImagerie/OMERO-metrics)

<img alt="OMERO-metrics logo" height="100" src="OMERO_metrics/static/OMERO_metrics/images/metrics_logo.png"/>

This project is financed by [France BioImaging](https://france-bioimaging.org/).

<img alt="FBI logo" height="100" src="docs/slides/media/logo_FBI.png"/>

OMERO.metrics with Docker
=========================

A webapp to follow microscope performance over time.

Installation
============

Install `OMERO_metrics` in development mode as follows:

    # within your python venv:
    $ cd OMERO-metrics
    $ pip install -e .

Run in your terminal to start the server:

    $ docker compose up -d


Execute this code to generate some test data:

     $ cd OMERO-metrics/
     $ pip install -r requirements.txt
     $ cd test/omero-server
     $ python3 structure_generator.py

Now restart your `omero-web` server and go to
<http://localhost:5080/omero_metrics/> in your browser.

# OMERO-metrics with a local omero-web

This project is related to configuring Django settings for OMERO web application with Plotly Dash components.

## Installation

```
$ cd OMERO-metrics
$ pip install -e .
```

1.  Make sure you have REACT_VERSION=18.2.0 installed and set ENV to REACT_VERSION=18.2.0 (export REACT_VERSION=18.2.0) .

Add these additional configurations using the terminal:

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

```
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

