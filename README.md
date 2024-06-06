OMERO.metrics
=======================

A webapp to follow microscope performance over time.

Installation
============

Install `omero_metrics` in development mode as follows:

    # within your python venv:
    $ cd OMERO-metrics
    $ pip install -e .

Run in your terminal to start the server:

    $ docker compose up -d


Now restart your `omero-web` server and go to
<http://localhost:5080/omero_metrics/> in your browser.


Further Info
============

1.  This app was derived from [cookiecutter-omero-webapp](https://github.com/ome/cookiecutter-omero-webapp).
2.  For further info on depolyment, see [Deployment](https://docs.openmicroscopy.org/latest/omero/developers/Web/Deployment.html)
