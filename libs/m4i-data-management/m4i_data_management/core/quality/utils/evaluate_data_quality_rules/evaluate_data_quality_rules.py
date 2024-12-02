import logging
from datetime import datetime
from uuid import uuid4 as uuid

from pandas import DataFrame, concat

from ..run_quality_check import run_quality_check

log = logging.getLogger(__name__)


def annotate_results(data: DataFrame, run_id: str, run_date: str):
    result = data.copy()

    result["run_id"] = run_id
    result["run_date"] = run_date

    return result
# END annotate_reults


def evaluate_data_quality_rules(data: DataFrame, rules: DataFrame) -> DataFrame:
    """
    Evaluates the given data quality `rules` over the given `data` and returns the test results as Pandas DataFrame.
    """
    def run_checks():
        for _, rule in rules.iterrows():

            if rule['active'] == 0:
                log.info(f"Skipping inactive business rule {rule['id']}")
                continue
            # END IF

            yield run_quality_check(data, rule)
        # END LOOP
    # END run_checks

    run_id = uuid()
    run_date = datetime.now().isoformat()

    summaries = DataFrame()
    all_compliant = DataFrame()
    all_non_compliant = DataFrame()

    for summary, compliant, non_compliant in run_checks():
        summaries = summaries.append(summary, ignore_index=True)
        all_compliant = concat([all_compliant, compliant], ignore_index=True)
        all_non_compliant = concat([all_non_compliant, non_compliant], ignore_index=True)
    # END LOOP

    return (
        annotate_results(summaries, run_id, run_date),
        annotate_results(all_compliant, run_id, run_date),
        annotate_results(all_non_compliant, run_id, run_date)
    )
# END evaluate_data_quality_rules
