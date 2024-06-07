import pytest

from omero.testlib import ITest
from omero.gateway import BlitzGateway, ImageWrapper
from omero.model import ExperimenterI, ImageI, EventI
from omero.rtypes import rlong, rstring, rtime

@pytest.fixture(scope='session')
def conn():
    conn = BlitzGateway(username='root', passwd='omero', host='localhost', port=6064)

@pytest.fixture(scope='function')
def unprocessed_dataset(conn: BlitzGateway):
    experimenter = ExperimenterI()
    temp_conn = conn.suConn(username=experimenter.getOmeroUser().getName())
    experimenter.firstName = rstring('first_name')
    experimenter.lastName = rstring('last_name')
    image = ImageI()
    image.id = rlong(1)
    image.description = rstring('description')
    image.name = rstring('name')
    image.acquisitionDate = rtime(1000)  # In milliseconds
    image.details.owner = ExperimenterI(1, False)
    creation_event = EventI()
    creation_event.time = rtime(2000)  # In milliseconds
    image.details.creationEvent = creation_event
    return ImageWrapper(conn=temp_conn, obj=image)

class TestDatasetManager(ITest):
    pass