import datetime
import inspect
import logging
import os
from functools import partial

from . import gcontext, gsettings
from .store import Filestore, Store

log = logging.getLogger("prefect.pipex")


# TODO what else could be useful in target fstring?
FSTRING_MODULES = [os, datetime]


def f(fstring, kwargs):
    """evaluate fstring at runtime including limited set of modules"""
    modules = {module.__name__: module for module in FSTRING_MODULES}
    return eval(f"f'{fstring}'", modules, kwargs)


class Task:
    """
    class decorator. use @task function to create
    return target if exists; load inputs from Stores; save output to target; return Store(target)

    :param target: template string for target file
    :para store: what to return. default=FileStore. None=raw data.
    """

    def __init__(self, fn, target=None, store=None):
        self.fn = fn
        # target will be filled at runtime using args/kwargs, funcname, gcontext
        self.target = target or gsettings["target_template"]
        self.store = store or Filestore

    def __call__(self, *args, **kwargs):
        target = self.fill_template(self.target, *args, **kwargs)
        if self.store:
            target = self.store(target)
            if target.exists():
                return target
        data = self.run(*args, **kwargs)
        if self.store:
            target.save(data)
            return target
        return data

    def fill_template(self, template, *args, **kwargs):
        """fill template using args/kwargs, funcname, gcontext"""
        sig = inspect.signature(self.fn)
        context = {
            k: v.default
            for k, v in sig.parameters.items()
            if v.default is not inspect.Parameter.empty
        }
        arguments = sig.bind(*args, **kwargs).arguments
        context.update(**arguments)
        context = {k: str(v) for k, v in context.items()}
        context.update(funcname=self.fn.__name__)
        context.update(gcontext)
        target = f(template, context)

        return target

    def run(self, *args, **kwargs):
        # load Store inputs automatically
        args = [v.load() if isinstance(v, Store) else v for v in args]
        kwargs = {k: v.load() if isinstance(v, Store) else v for k, v in kwargs.items()}

        # execute function
        data = self.fn(*args, **kwargs)

        return data


def task(
    fn=None,
    target: str = None,
    store: Store = Filestore,
    **kwargs,
):
    """
    decorator to wrap function with cache
    return target if exists; load inputs from Stores; save output to target; return Store(target)

    :param target: template string for target file
    :param store: what to return. default=FileStore. None=raw data.
    :param kwargs: ignored e.g. ignores any kwargs used only by prefect or pipex.prefect
    """
    if fn:
        del kwargs
        return Task(**locals())
    else:
        # enable default parameters to be set before decorator called
        del fn
        del kwargs
        return partial(task, **locals())
