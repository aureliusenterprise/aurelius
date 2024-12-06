import logging
from typing import Callable

from pandas import DataFrame

from .utils import annotate_results_with_metadata, evaluate_data_quality_rules

log = logging.getLogger(__name__)


class Quality():

    get_data: Callable[[], DataFrame]
    get_metadata: Callable[[], DataFrame]
    get_rules: Callable[[], DataFrame]
    name: str
    propagate: Callable[[DataFrame, DataFrame, DataFrame], None]

    def __init__(
        self,
        get_data: Callable[[], DataFrame],
        get_rules: Callable[[], DataFrame],
        get_metadata: Callable[[], DataFrame],
        propagate: Callable[[DataFrame, DataFrame, DataFrame], None],
        name: str = "Quality"
    ):
        self.get_data = get_data
        self.get_metadata = get_metadata
        self.get_rules = get_rules
        self.name = name
        self.propagate = propagate
    # END __init__

    def run(self):
        """
        Runs the quality check once and applies the following steps:

        1. Retrieve the data from the quality data source
        2. Retrieve the data quality rules
        3. Apply the data quality rules to the dataset, which results in an overall data quality summary as well as a list of compliant and non-compliant rows
        4. Retrieve the metadata for the data quality rules from the data dictionary
        5. Annotate the data quality results with metadata from the data dictionary
        6. Propagate the data quality test results
        """

        log.info(f"Started running quality {self.name}")

        data = self.get_data()

        log.info(f"Retrieved {len(data.index)} records")

        rules = self.get_rules()

        log.info(f"Retrieved {len(rules.index)} data quality rules")

        summary, compliant, non_compliant = evaluate_data_quality_rules(
            data=data,
            rules=rules
        )

        log.info(
            f"Evaluated {len(summary.index)} data quality rules; found {len(compliant.index)} compliant rows and {len(non_compliant.index)} non-compliant rows"
        )

        metadata = self.get_metadata()

        log.info(
            f"Retrieved {len(metadata.index)} rows of metadata from the data dictionary"
        )

        summary = annotate_results_with_metadata(summary, metadata)
        compliant = annotate_results_with_metadata(compliant, metadata)
        non_compliant = annotate_results_with_metadata(non_compliant, metadata)

        log.info(
            f"Annotated {len(summary.index) + len(compliant.index) + len(non_compliant.index)} results with metadata from the data dictionary"
        )

        self.propagate(summary, compliant, non_compliant)

        log.info(
            f"Propagated {len(summary.index)} data quality test summaries and {len(compliant.index) + len(non_compliant)} test details"
        )

        log.info(f"Finished running quality {self.name}")
    # END run
# END Quality
