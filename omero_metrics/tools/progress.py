"""Lightweight, file-backed progress log for long-running analyses.

Dash callbacks are blocking request/response cycles, so a running analysis cannot
push intermediate output to the browser directly. Instead the analysis appends
progress lines to a per-dataset file here, and a ``dcc.Interval`` in the form
polls :func:`read` to display them live.

A file (rather than in-memory state) is used deliberately: OMERO.web runs several
sync gunicorn worker *processes*, so the blocking analysis request and the polling
requests are usually served by different processes. A file on the container
filesystem is shared across all of them; a module global would not be.
"""

import os
import tempfile

# Keep the tail bounded so the browser payload and the file stay small even for a
# very chatty run.
_MAX_LINES = 400


def _dir() -> str:
    path = os.path.join(tempfile.gettempdir(), "omero_metrics_progress")
    os.makedirs(path, exist_ok=True)
    return path


def path(dataset_id) -> str:
    """Absolute path of the progress log for ``dataset_id``."""
    return os.path.join(_dir(), f"{dataset_id}.log")


def clear(dataset_id) -> None:
    """Truncate the progress log (call at the start of a run)."""
    try:
        open(path(dataset_id), "w").close()
    except OSError:
        pass


def make_echo_func(dataset_id):
    """Return a Chromagnon-compatible ``echo(msg, **kwargs)`` that appends to disk.

    Chromagnon calls the echo sink with a message string and arbitrary keyword
    arguments (e.g. ``skip_notify=True``); the keywords are ignored here.
    """
    log_path = path(dataset_id)

    def echo(msg="", **_kwargs):
        try:
            with open(log_path, "a") as f:
                f.write(f"{msg}\n")
        except OSError:
            pass

    return echo


def read(dataset_id, max_lines: int = _MAX_LINES) -> str:
    """Return the last ``max_lines`` of the progress log (newest at the bottom).

    Returns an empty string when no log exists yet.
    """
    try:
        with open(path(dataset_id)) as f:
            lines = f.readlines()
    except OSError:
        return ""
    return "".join(lines[-max_lines:]).rstrip("\n")
