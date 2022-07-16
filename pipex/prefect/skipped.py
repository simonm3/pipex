from uuid import uuid4

from prefect.futures import PrefectFuture
from prefect.orion.schemas.data import DataDocument
from prefect.orion.schemas.states import Completed

class Skipped(PrefectFuture):
    """returned by tasks that skip the scheduler
    inherits methods called in flows such as wait and result
    does not define a task_runner
    """

    def __init__(self, storeitem):
        self.run_id = uuid4()
        self.asynchronous = False
        self._final_state = Completed(
            data=DataDocument.encode(encoding="cloudpickle", data=storeitem)
        )
        self.storeitem = storeitem

    def get_state(self):
        return self._final_state

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"Skipped({str(self.storeitem)})"

    def _ipython_display_(self):
        print(repr(self))
