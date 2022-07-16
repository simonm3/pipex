Purpose
=======

Pipeline cache that works standalone or with prefect2

***** Work in progress. Not fully tested and subject to change ****

install
=======

```
pip install pipex
```

Usage
=====

Set PIPEX environment variable to determine behaviour of @task and @flow:
-------------------------------------------------------------------------

PIPEX="do_nothing"

    * ignore @task/@flow. just run functions directly


PIPEX="cache"

    * target template filled on task submit e.g. to include filename
    * Skip tasks where output file exists
    * Load data from files
    * Save output to file based on target template
    * Return target location rather than data
        - avoids passing unnecessary data in multiprocessing
        - avoids using ram to store data
        - avoids loading data unnecessarily e.g. chain of tasks that are complete
    * Manually remove files to force a rerun of selected tasks

PIPEX="prefect"

    * use prefect directly. ignore any extra kwargs.

PIPEX="prefect.cache"

    * combine cache and prefect
    
@task parameters for cache and prefect.cache
--------------------------------------------

    * default: @task(target="{path}/{funcname}/{base}", store=Filestore, save=True)
    * target=template string for where output is stored. Can include modules e.g. [os, datetime]
    * path=set at runtime
    * base=set at runtime
    * store=any class inherited from Store e.g. to store in a database. default is pickle file. 
    * save=False. return data instead of saving. lets function save own output.

Why not prefect2 cache?
=======================

Prefect2 has own cache system based on hash of input parameters. However location of cache files is fixed and not configurable. It is also hidden so you cannot view individual cache files nor delete them to force a rerun. 

Sometimes you have thousands of tasks and want to view a selection of interim outputs; make iterative changes to pipeline steps; rerun only what needs rerunning. Repeat this until all task runs have succeeeded. This requires pipex cache where you can specify file locations with meaningful names.

Other
=====

* dask bug fix re memory
* keepalive for long running tasks (bug reported but perhaps setting for this?)
* setup dask logging from extra loggers
* task name template filled on submit e.g. to include "base" which could be a filename
* updated logging settings e.g. show lineno for tasks
