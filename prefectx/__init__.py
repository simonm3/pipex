import os
import logging

from .utils import keepalive, setup_dask_logging

log = logging.getLogger(__name__)

# default settings
os.environ.setdefault(
    "PREFECT_LOGGING_SETTINGS_PATH", f"{os.path.dirname(__file__)}/logging.yml"
)
os.environ.setdefault("PREFECT_API_URL", "http://127.0.0.1:4200/api")
os.environ.setdefault("PREFECTX", "function")

# TODO remove when dask bug fixed https://github.com/dask/distributed/issues/5971
os.environ["ENV MALLOC_TRIM_THRESHOLD_"] = "65536"

# used to pass context to a set of tasks
gcontext = {}

def do_nothing(fn=None, **kwargs):
    """dummy decorator e.g. for @task, @flow"""
    return fn if fn else do_nothing


# set behaviour of @task and @flow depending on task_type
task_type = os.environ["PREFECTX"]
if task_type == "function":
    task = do_nothing
    flow = do_nothing
elif task_type == "cache":
    flow = do_nothing
    from .cache import task
elif task_type == "prefect":
    from prefect.flows import flow
    from prefect.tasks import task
elif task_type == "prefect.cache":
    from prefect.flows import flow
    from .prefect import task

    task = task(skip=False)
elif task_type == "prefect.skip":
    from prefect.flows import flow
    from .prefect import task
else:
    raise Exception(f"PREFECTX={task_type} is not valid")
log.info(f"{task_type} will be used to control task flows")

# workarounds
if task_type.startswith("prefect"):
    keepalive()
    setup_dask_logging()
