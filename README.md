
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/MontpellierRessourcesImagerie/OMERO-metrics/omero_plugin.yml)
![GitHub License](https://img.shields.io/github/license/MontpellierRessourcesImagerie/OMERO-metrics)

<img alt="OMERO-metrics logo" height="100" src="omero_metrics/static/omero_metrics/images/metrics_logo.png"/>

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
git clone https://github.com/MontpellierRessourcesImagerie/OMERO-metrics.git
cd OMERO-metrics
```

Run the following command to start the server:

```bash
docker compose up -d
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
./configuration_omero.sh /path/to/omeroweb /path/to/mydatabase
```

where `/path/to/omeroweb` is the path to the OMERO-web directory and `/path/to/mydatabase` is the path to the omero_metrics sqlite database.

```bash
export REACT_VERSION=18.2.0
export OMERODIR=$(pwd)
omero config set omero.web.server_list '[["localhost", 6064, "omero_server"]]'
omero web start
```

# Some Useful Links To Download ZeroC-Ice

```python
#zeroc-ice @ https://github.com/glencoesoftware/zeroc-ice-py-macos-universal2/releases/download/20240131/zeroc_ice-3.6.5-cp311-cp311-macosx_11_0_universal2.whl
#zeroc-ice @ https://github.com/glencoesoftware/zeroc-ice-py-linux-x86_64/releases/download/20240202/zeroc_ice-3.6.5-cp311-cp311-manylinux_2_28_x86_64.whl
```

## Further Info

1.  This app was derived from [cookiecutter-omero-webapp](https://github.com/ome/cookiecutter-omero-webapp).
2.  For further info on deployment, see [Deployment](https://docs.openmicroscopy.org/latest/omero/developers/Web/Deployment.html)


## License

This project, similar to many Open Microscopy Environment (OME) projects, is
licensed under the terms of the AGPL v3.


## Copyright

2024 CNRS

