
***** Work in progress. Not fully tested and subject to change ****

Purpose
=======

This contains extensions to prefect2. As prefect2 is still in beta it may incorporate this functionality in future but for now these are workarounds.

Do nothing
----------

To use functions decorated with @task or @flow without prefect:

    * replace "from prefect import task, flow" with "from prefectx import task, flow"

To use prefect set environment variable PREFECTX="prefect" or other values as below.

This avoids having to remove @task decorators to not use prefect e.g for testing

File caching
------------

Prefect2 has caching but the location of cache files is opaque. Sometimes you have thousands of tasks and want to view a selection of interim outputs; make iterative changes to pipeline steps; rerun only what needs rerunning. Repeat this until all task runs have succeeeded. This is achieved here using the filesystem to save outputs with meaningful names.

* target template filled on task submit e.g. to include filename
* Skip tasks where output file exists
* Load data from files
* Save output to file
* Can manually remove files to force a rerun of selected tasks

Other
-----

* dask bug fix re memory
* keepalive for long running tasks (bug reported but perhaps setting for this?)
* setup dask logging from extra loggers
* task name template filled on submit e.g. to include "base" which could be a filename
* my logging settings e.g. show lineno for tasks
* various test flows

install
=======

```
git clone
cd prefectx
pip install -e .
```

Usage
=====

Decorate functions with @task or @flow
Set PREFECTX environment variable to determine behaviour of @task and @flow

@task parameters
----------------

    * default: @task(target="working/{funcname}/{base}", store=Filestore, save=True)
    * target=template string for where output is stored. Can include modules e.g. [os, datetime]
    * base=set at runtime
    * store=any class inherited from Store e.g. to store in a database. default is pickle file. 
    * save=False. return data instead of saving. lets function save own output.


PREFECTX environment variable
-----------------------------

PREFECTX="function" ### DEFAULT ###
    * @task and @flow do nothing
    * function accepts data; returns data
    * used to test functions before using cache or prefect.cache

PREFECTX="cache"

    * @task check target exists; load Items; save output; return Item
    * @flow does nothing
    * tasks run without prefect
    * completed tasks are skipped
    * used for serial procesing e.g. tasks that cannot be parallel and/or require high RAM

PREFECTX="prefect.skip"

    * @task creates prefect task. function will check target exists; load Items; save output; return Item
    * @flow is imported from prefect
    * tasks run on prefect
    * completed tasks skip the prefect scheduler
    * default PREFECT_API_URL="http://127.0.0.1:4200/api"
    * used for multiprcessing e.g. tasks that are CPU constrained and low RAM

PREFECTX="prefect.cache"

    * as "prefect.skip" but completed tasks are sent to prefect scheduler

PREFECTX="prefect"

    * use prefect directly

