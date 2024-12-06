import logging
from typing import Callable

from pandas import DataFrame

from ..cdc import compare_datasets
from ..utils import identity

log = logging.getLogger(__name__)


class Producer:

    get_new: Callable[[], DataFrame]
    get_old: Callable[[], DataFrame]
    name: str
    propagate: Callable[[DataFrame], None]
    dataset_comparator: Callable[[DataFrame, DataFrame], DataFrame]
    transform: Callable[[DataFrame], DataFrame]

    def __init__(
        self,
        get_new: Callable[[], DataFrame],
        get_old: Callable[[], DataFrame],
        propagate: Callable[[DataFrame], None],
        name: str = "Producer",
        dataset_comparator: Callable[[DataFrame, DataFrame], DataFrame] = compare_datasets,
        transform: Callable[[DataFrame], DataFrame] = identity
    ):
        self.get_new = get_new
        self.get_old = get_old
        self.name = name
        self.propagate = propagate
        self.dataset_comparator = dataset_comparator
        self.transform = transform
    # END __init__

    def run(self):
        """
        Runs the producer once and applies the following steps:

        1. Retrieve the new data from the producer data source
        2. Retrieve the old data from the data management platform
        3. Compare the old and new datasets and annotate changes (CDC)
        4. Apply data transformations
        5. Propagate the changes to the data management platform
        """

        log.info(f"Started running producer {self.name}")

        new_data = self.get_new()

        log.info(f"Retrieved {len(new_data.index)} new data records")

        old_data = self.get_old()

        log.info(f"Retrieved {len(old_data.index)} old data records")

        changes = self.dataset_comparator(
            old=old_data,
            new=new_data,
        )

        log.info(f"Found {len(changes.index)} changes")

        if len(changes.index) > 0:
            data = self.transform(changes)

            log.info(f"Transformed {len(data.index)} records")

            self.propagate(data)

            log.info(f"Propagated {len(data.index)} change events")
        # END IF

        log.info(f"Finished running producer {self.name}")
    # END run
# END Producer
