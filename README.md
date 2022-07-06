
***** Work in progress. Not fully tested and subject to change ****

Purpose
=======

This contains extensions to prefect2. As prefect2 is still in beta it may incorporate this functionality in future but for now these are workarounds.


File caching
------------

Prefect2 does have caching but the location of cache files is opaque. Sometimes you have thousands of tasks and want to view a selection of interim outputs; make iterative changes to pipeline steps; rerun only what needs rerunning. 

* Skip tasks where output file exists
* Load data from files
* Save output to file
* target template filled on task submit e.g. to include filename

Can run:

* with "do nothing" @task/@flow decorators to test code without any pipeline management
* with file caching only but not using prefect2
* using prefect2 but without forwarding completed tasks to the scheduler

Other
-----

* dask bug fix re memory
* keepalive for long running tasks (perhaps setting for this?)
* setup dask logging fro extra loggers
* do nothing decorators so functions can be tested without prefect
* task name template filled on submit e.g. to include filename
* logging settings e.g. show lineno for tasks
* various test flows

install
=======

```
git clonedd
cd prefectx
pip install -e .
```

Usage
=====

Decorate functions with @task or @flow.
Decorator behaviour is determined by PREFECTX environment variable.

PREFECTX="prefect.skiptask" [default]

    * cache output
    * @flow is imported from prefect
    * @task caches output; creates prefect task
    * tasks run on prefect
    * sets default PREFECT_API_URL="http://127.0.0.1:4200/api". Set to None if not running Orion.
    * completed tasks are not sent to prefect scheduler

PREFECTX="cache"

    * @task caches output
    * @flow does nothing
    * tasks run without prefect
    * completed tasks are skipped

can set task to override defaults e.g. task=task(target="working/{funcname}/{base}", store=Filestore) [default]

    * target is a template for where output is stored
    * base is set at runtime
    * store is where output is saved. default is pickle file. can be any class inherited from Store e.g. to store in a database

====================================================================================

Testing
=======

Set PREFECTX to the following for testing

function                accept data; return data. @task and @flow do nothing
cache                   check target exists; load Items; save output; return Item
                        save=False. return data instead of saving
                        can be tested and used without prefect but has compatible api
prefect                 accept data; return future
                        @task and @flow imported from prefect.
prefect.cachetask       cachetask + prefect
                        send all tasks to prefect
prefect.skiptask        cachetask + prefect
                        skip the scheduler for completed tasks.