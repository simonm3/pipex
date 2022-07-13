import os
import logging

from .utils import keepalive, setup_dask_logging

log = logging.getLogger("prefectx")

# default settings
os.environ.setdefault(
    "PREFECT_LOGGING_SETTINGS_PATH", f"{os.path.dirname(__file__)}/logging.yml"
)

# TODO remove when dask bug fixed https://github.com/dask/distributed/issues/5971
os.environ["ENV MALLOC_TRIM_THRESHOLD_"] = "65536"

# used to pass global context to a set of tasks
gcontext = {}

# dummy decorator
def do_nothing(fn=None, **kwargs):
    return fn if fn else do_nothing


# set behaviour of @task depending on task_type
task_type = os.environ.get("PREFECTX", "prefect.skip")
if task_type == "function":
    task = do_nothing
elif task_type == "cache":
    from .cache import task
elif task_type == "prefect":
    from prefect.tasks import task
elif task_type == "prefect.cache":
    from .prefect import task

    task = task(skip=False)
elif task_type == "prefect.skip":
    from .prefect import task
else:
    raise Exception(f"PREFECTX={task_type} is not valid")
log.info(f"{task_type} will be used to control task flows")

# set behaviour of @flow depending on task_type
if task_type.startswith("prefect"):
    from prefect.flows import flow
else:
    flow = do_nothing

# workarounds
if task_type.startswith("prefect"):
    keepalive()
    # TODO
    # setup_dask_logging()
