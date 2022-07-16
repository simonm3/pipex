import os
import logging
import yaml
from .dotdict import dotdict

log = logging.getLogger("pipex")

gcontext = None
gsettings = None


def load_config():
    global gcontext
    global gsettings
    with open(f"{os.path.dirname(__file__)}/config.yml") as f:
        gconfig = yaml.safe_load(f.read())
    gconfig = dotdict(gconfig)
    gcontext = gconfig.get("gcontext", dotdict())
    gsettings = gconfig.get("gsettings", dotdict())
    log.info(gconfig)
    log.info(gcontext)
    log.info(gsettings)


# dummy decorator
def do_nothing(fn=None, **kwargs):
    return fn if fn else do_nothing


# load global context and settings
load_config()
log.info(gcontext)
log.info(gsettings)

# @task behaviour
task_type = os.environ.get("PIPEX", gsettings.pipex)
if task_type == "do_nothing":
    tasks = do_nothing
    flow = do_nothing
elif task_type == "cache":
    from .tasks import task

    flow = do_nothing
elif task_type in ["prefect", "prefect.cache"]:
    from .prefect.tasks import task
    from prefect import flow
else:
    raise Exception(
        f"PIPEX={task_type} is not valid. Must be do_nothing, cache, prefect or prefect.cache"
    )
