*********
API Guide
*********

**Table of Contents**

.. contents::
    :local:
    :depth: 2
    :backlinks: none

Here's the API synopsis::

    # Schedule creation and access
    GET /schedules
    HEAD /schedules
    POST /schedules

    # Fundamental operations on a schedule
    GET /schedules/{id}
    HEAD /schedules/{id}
    DELETE /schedules/{id}
    PUT /schedules/{id}
    PATCH /schedules/{id}

    # More explicit endpoints for schedule modification
    # Can also be achieved by PUT/PATCH /schedules/{id}
    PUT /schedules/{id}/name
    PUT /schedules/{id}/arguments
    PUT /schedules/{id}/schedule
    POST /schedules/{id}/enable
    POST /schedules/{id}/disable
    POST /schedules/{id}/cancel

=========
Schedules
=========

A schedule is the most primitive resource handled by Cloud Crony. It
defines a task, how often it occurs, and how to execute it.

--------------
GET /schedules
--------------

A summary view of all tasks.

.. code-block:: http

    HTTP/1.1 200 OK
    Connection: keep-alive
    Content-Length: 9001

.. code-block:: json

    [
        {
            "id": 12345,
            "href": {
                "link": "https://example.com/schedules/12345",
                "rel": "link"
            },
            "name": "My Secondary Task",
            "location": "https://cloudstorage.com/tasks/seconds.py",
            "schedule": "15 * * * * * *",
            "enabled": true
         },
         {
             ...
         }
    ]

---------------
POST /schedules
---------------

This is scheduled task creation.

The schedule is the most interesting field. It is specified in
extended `cron format`_::

    ---------------- seconds: 0-59
    | -------------- minutes: 0-59
    | | ------------ hours: 0-23
    | | | ---------- day of month: 1-31
    | | | | -------- month: 1-12
    | | | | | ------ weekday: 0-6 [Monday == 0]
    | | | | | | ---- year: now - 2999+
    | | | | | | |
    * * * * * * *

Tasks are defined by a location and a list of arguments. Task scripts
are downloaded to the local environment and executed using the
arugments. The execution semantics are very similar to Python's
`subprocess.Popen`_.

A progress_hook is a script that is run that can report the progress
of the scheduled task. If the progress_hook is left unspecified, then
the progress of the task when queried will appear as either "unknown"
or "completed". If it is specified, the progress will be presented as
an integer from 0 - 100. The syntax for specifying a progress_hook is
the task syntax.

Request:

.. code-block:: json

    {
        "name": "My Secondary Task",
        "task": {
            "location": "https://cloudstorage.com/tasks/seconds.py",
            "args": [
                "--option=tacos", "-v", "-v", "-x", "100"
            ]
        },
        "progress_hook": null,
        "schedule": "15 * * * * * *",
        "enabled": true
    }

If cron syntax is too cryptic for you, the following alternative format is supported for schedules:

.. code-block:: json

    {
        "name": "My Secondary Task",
        "task": {
            "location": "https://cloudstorage.com/tasks/seconds.py",
            "args": [
                "--option=tacos", "-v", "-v", "-x", "100"
            ]
        },
        "progress_hook": null,
        "schedule": {
            "seconds": "15",
            "minutes": "*",
            "hours": "*",
            "day_of_month": "*",
            "month": "*",
            "weekday": "*",
            "year": "*"
        }
        "enabled": true
    }

Response:

.. code-block:: http

    HTTP/1.1 200 OK

-------------------
GET /schedules/{id}
-------------------

This allows you to retrieve more detailed information about a specific
scheduled task.

.. code-block:: http

    HTTP/1.1 200 OK
    Connection: keep-alive
    Content-Length: 9001

.. code-block:: json

    {
        "id": 12345,
        "href": {
            "link": "https://example.com/schedules/12345",
            "rel": "link"
        },
        "name": "My Secondary Task",
        "task": {
            "location": "https://cloudstorage.com/tasks/seconds.py",
            "args": [],
        },
        "schedule": "15 * * * * * *",
        "enabled": true,
        "progress": 23,
        "state": "running",
        "next": "2013-12-28T14:54:37.938283"
    }

----------------------
DELETE /schedules/{id}
----------------------

This allows you to remove a scheduled task from Cloud Crony. If the
task happens to be running at the time that this is issued, one of two
things will happen. If the parameter **immediate** is set, then the task
will be terminated immediately and removed from the queue. Otherwise,
the task will be allowed to complete and will then be removed from the
scheduling queue.

-------------------------
PUT/PATCH /schedules/{id}
-------------------------

Allows for an existing schedule to be modified. The following
attributes can be changed::

    name
    arguments
    schedule
    enabled

These correspond to the individual endpoints given in the synopsis. If
a running task is modified, it's next invocation will be affected by
the modification.

---------------------------
POST /schedules/{id}/cancel
---------------------------

Terminates a running task. If the task is not running, this will still
return an OK, since the end result is the same.

.. _cron format: https://en.wikipedia.org/wiki/Cron#Format
.. _subprocess.Popen: http://docs.python.org/2/library/subprocess.html#subprocess.Popen
