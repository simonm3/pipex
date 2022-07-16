import datetime
import logging
import os
from copy import deepcopy
from functools import partial
from typing import Any, Callable, Dict, Iterable, Optional, Union

from prefect.context import TaskRunContext
import prefect

from ..tasks import Task
from ..store import Filestore, Store
from .utils import init_prefect
from .skipped import Skipped

log = logging.getLogger(__name__)


class CacheFunc(Task):
    """decorator to wrap embedded function
    resolve target in CacheTask.__call__ before submission not Func.__call__ at remote execution time.
    """

    def __call__(self, *args, **kwargs):
        data = self.run(*args, **kwargs)
        if self.store:
            self.target.save(data)
            return self.target
        return data


class CacheTask(prefect.tasks.Task):
    def __init__(self, fn, **kwargs):
        """extension to prefect.Task to cache outputs as files using target template"""
        target = kwargs.pop("target")
        store = kwargs.pop("store", Filestore)
        self.skip = kwargs.pop("skip", True)
        self.name_template = kwargs.pop("name_template", None)

        # init then assign function to avoid functools.update_wrapper
        super().__init__(fn, **kwargs)
        self.fn = CacheFunc(fn, target=target, store=store)

    def __call__(self, *args, wait_for=None, **kwargs):
        target = self.fn.fill_template(self.fn.target, *args, **kwargs)
        if self.fn.store:
            target = self.fn.store(target)

        # check if complete
        if self.skip and target.exists():
            future = Skipped(target)
        else:
            # copy to allow multiple calls in ConcurrentTaskRunner
            copy1 = deepcopy(self)
            # fill func task template onSubmit not onExecute
            copy1.fn.target = target
            if self.name_template:
                copy1.name = self.fn.fill_template(self.name_template, *args, **kwargs)
            future = copy1.submit(*args, wait_for=wait_for, **kwargs)

        return future

    def submit(self, *args, wait_for, **kwargs):
        return super().__call__(*args, wait_for=wait_for, **kwargs)


def task(
    # prefect.task
    fn=None,
    name: str = None,
    description: str = None,
    tags: Iterable[str] = None,
    cache_key_fn: Callable[["TaskRunContext", Dict[str, Any]], Optional[str]] = None,
    cache_expiration: datetime.timedelta = None,
    retries: int = 0,
    retry_delay_seconds: Union[float, int] = 0,
    # additional cache
    target: str = None,
    store: Store = Filestore,
    # additional prefect.cache
    name_template: str = None,
    skip: bool = True,
):
    """
    decorator to create CacheTask. This will return target if exists; load input data from Stores; save output to target; return Store(target). runs tasks on prefect2.

    :param name_template: task name template. can be a template string
    :param target: template string for target file
    :para store: class inherited from Store. default=Filestore
    :param skip: skip the scheduler for completed tasks
    """
    if fn:
        if os.environ.get("PIPEX") == "prefect":
            # drop any extra kwargs
            del target
            del store
            del name_template
            del skip
            return prefect.task(**locals())
        return CacheTask(**locals())
    else:
        # enable default parameters to be set before decorator called
        del fn
        return partial(task, **locals())


init_prefect()
