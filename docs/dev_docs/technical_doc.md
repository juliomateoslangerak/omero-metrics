
OMERO-metrics is an omero web app. It was initially generated using the cookiecutter https://github.com/ome/cookiecutter-omero-webapp

For visualization, we are using the help of dash and django-plotly-dash. 
We are using also microscope-metrics and microscopemetrics-schema developped previously by Julio. 


# Documentations
https://django-plotly-dash.readthedocs.io/en/latest/
https://dash.plotly.com/
https://www.dash-mantine-components.com/

# New Analysis Type

![image](https://hackmd.io/_uploads/B1LUvmDN1e.png)
 
To add a new analysis type, you create a folder under OMERO_metrics/dash_apps/dash_analysis
 
create two python files, one for the dataset view and the other for the iage view. 

 

# Running Debug Mode on Pycharm
To run the debug mode and run omero locally using a django test server. 

```bash
$ git clone https://github.com/MontpellierRessourcesImagerie/OMERO-metrics.git
$ cd OMERO-metrics
$ python -m venv my_venv
$ source my_venv/bin/activate
$ pip install -e .
```
![image](https://hackmd.io/_uploads/SyfAPZDE1x.png)


We created a bash script to configure omero. You can run it by typing:

```bash
$ ./configuration_omero.sh /path/to/omeroweb /path/to/mydatabase
````
where `/path/to/omeroweb` is the path to the omero-web installation or path and `/path/to/mydatabase` is the path to the OMERO-metrics sqlite database.


```bash
export REACT_VERSION=18.2.0
export OMERODIR=$(pwd)
omero config set omero.web.server_list '[["localhost", 6064, "omero_server"]]'
omero web start
````

Make sure under etc directory you have ice.config. If it doesn't exist, you create it by adding the following:

```
omero.host=localhost
omero.port=6064
omero.rootpass=omero
```

Note: for the pytest to work the omero.web.server_list should start exactly with the server configured under ice.config. Otherwise, the test won't pass. 


For more information about ice.config. Click [Here](https://github.com/ome/openmicroscopy/blob/develop/etc/ice.config).

## Running Pytest on Pycharm for OMERO-metrics

Try to look for this small menu in the image to run and configure 
![image](https://hackmd.io/_uploads/Hk4L0-vVkx.png)

Click on "Edit Configureations" the following window will open to configure your pytest and debug mode:

![image](https://hackmd.io/_uploads/H1JT1fDEJe.png)

Click on add new run configuration and click on pytest:

![image](https://hackmd.io/_uploads/BJX-gfDNkx.png)

Now, we need to add our configurations: 
The path to the pytest script you want to run
Working directory should be the rrot project OMERO-metrics. and add for Env variables : DJANGO_SETTINGS_MODULE=omeroweb.settings;REACT_VERSION=18.2.0;OMERODIR=~/OMERO-metrics;ICE_CONFIG=~/OMERO-metrics/etc/ice.config

![image](https://hackmd.io/_uploads/HJDjgfvN1g.png)

That's it, now run your test.


## Debug Mode:

We will do the same like pytest but instead of adding pytest we will add Django Server:

![image](https://hackmd.io/_uploads/B1-UMfD4Jl.png)

When you click on the Django server, this is the view that you will see. You will need first to enable Django Support for the project and add some configurations.

![image](https://hackmd.io/_uploads/ByvwnfvV1g.png)

The Django root project should be ~/omeroweb
manage script is manage.py and settings is settings.py

![image](https://hackmd.io/_uploads/ByC6nfDNkx.png)


the final step is to confugure back your configuration file o run a django server locally:
add these Env variables and run your omero web client instance locally DJANGO_SETTINGS_MODULE=omeroweb.settings;REACT_VERSION=18.2.0;OMERODIR=~/OMERO-metrics;ICE_CONFIG=~/OMERO-metrics/etc/ice.config

![image](https://hackmd.io/_uploads/Hk7a6GwE1l.png)

