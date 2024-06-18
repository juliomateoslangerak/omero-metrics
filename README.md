
[![Actions Status](https://github.com/Wapaa/OMERO-project/workflows/OMERO/badge.svg)](https://github.com/Wapaa/OMERO-project/actions)


OMERO.OMERO_metrics
==================================

OMERO example minimal web app.

Installation
============

This section assumes that an OMERO.web is already installed.

Installing from Pypi
--------------------

Install the app using [pip](<https://pip.pypa.io/en/stable/>) .

Ensure that you are running ``pip`` from the Python environment
where ``omero-web`` is installed. Depending on your install, you may need to
call ``pip`` with, for example: ``/path/to_web_venv/venv/bin/pip install ...``

::

    $ pip install -U OMERO-project


Development mode
----------------

Install `OMERO-project` in development mode as follows:

    # within your python venv:
    $ cd OMERO-project
    $ pip install -e .

After installation either from [Pypi](https://pypi.org/) or in development mode, you need to configure the application.
To add the application to the `omero.web.apps` settings, run the following command:

Note the usage of single quotes around double quotes:

    $ omero config append omero.web.apps '"OMERO_project"'

Optionally, add a link "Omero Web app" at the top of the webclient to
open the index page of this app:

    $ omero config append omero.web.ui.top_links '["Omero Web app", "OMERO_project_index", {"title": "Open Omero Web app in new tab", "target": "_blank"}]'


Now restart your `omero-web` server and go to
<http://localhost:4080/OMERO_project/> in your browser.


Further Info
============

1. This app was derived from [cookiecutter-omero-webapp](https://github.com/ome/cookiecutter-omero-webapp).
2. For further info on deployment, see [Deployment](https://docs.openmicroscopy.org/latest/omero/developers/Web/Deployment.html)


License
=======

This project, similar to many Open Microscopy Environment (OME) projects, is
licensed under the terms of the AGPL v3.


Copyright
=========

2024 University of Dundee

