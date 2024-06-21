"""
Test demo application

Most of these tests are simply the loading of the individual files that
constitute the demo. A configuration failure would
cause one or more of these to fail.

Copyright (c) 2018 Gibbs Consulting and others - see CONTRIBUTIONS.md

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

# pylint: disable=protected-access, no-member
import pytest


def mocking_connection():
    "Mocking connection"
    from unittest.mock import MagicMock
    from omero.gateway import BlitzGateway

    conn = MagicMock(spec=BlitzGateway)
    return conn


def connection_mocking(host, port, user, password):
    "Mocking connection to the server"
    from omero.gateway import BlitzGateway

    conn = BlitzGateway(user, password, host=host, port=port)
    return conn


host = "localhost"
port = 4064
user = "Asterix"
password = "abc123"


def test_url_loading():
    "Test loading of a module"
    from omero_metrics.urls import urlpatterns

    assert urlpatterns


def test_demo_loading():
    "Test the import and formation of a dash example app"

    from omero_metrics.dash_apps.dash_dataset_metrics import dash_app_dataset

    assert (
        dash_app_dataset._uid == "omero_dataset_metrics"
    )  # pylint: disable=protected-access


def test_for_the_test(client):
    response = client.get("/metrics_index/")
    assert response.status_code == 200
