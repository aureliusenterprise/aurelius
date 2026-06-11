import logging
from datetime import datetime
from typing import Tuple
from uuid import uuid4 as uuid

from pandas import DataFrame, Series

from ..calculate_quality_score import calculate_quality_score
from ..run_quality_rule_expression import run_quality_rule_expression

log = logging.getLogger(__name__)


def annotate_detailed_results(
    data: DataFrame,
    business_rule_id: str,
    data_field_qualified_name: str,
    data_quality_rule_description: str,
    data_quality_rule_dimension: str,
    result_id: str,
    test_date: str,
) -> DataFrame:
    result = data.copy()

    result["business_rule_id"] = business_rule_id
    result["data_field_qualified_name"] = data_field_qualified_name
    result["data_quality_rule_description"] = data_quality_rule_description
    result["data_quality_rule_dimension"] = data_quality_rule_dimension
    result["result_id"] = result_id
    result["test_date"] = test_date

    return result


# annotate_detailed_results


def run_quality_check(data: DataFrame, rule: Series) -> Tuple[dict, DataFrame, DataFrame]:
    business_rule_id: str = str(rule["id"])
    data_field_qualified_name: str = str(rule["data_field_qualified_name"])
    data_quality_rule_description: str = str(rule["data_quality_rule_description"])
    data_quality_rule_dimension: str = str(rule["data_quality_rule_dimension"])
    result_id: str = str(uuid())
    rule_expression: str = str(rule["expression"])
    test_date = datetime.now().isoformat()

    result: dict = {
        "business_rule_id": business_rule_id,
        "data_field_qualified_name": data_field_qualified_name,
        "dq_score": 0.0,
        "data_quality_rule_description": data_quality_rule_description,
        "data_quality_rule_dimension": data_quality_rule_dimension,
        "expression": rule_expression,
        "expression_version": rule["expression_version"],
        "result_id": result_id,
        "status": "no_success",
        "test_date": test_date,
    }

    compliant_rows = DataFrame()
    non_compliant_rows = DataFrame()

    try:
        log.info(f"Running the expression for business rule {rule['id']}")

        dq_score_per_row = run_quality_rule_expression(data, rule_expression)

        dq_score = calculate_quality_score(dq_score_per_row)

        compliant = dq_score_per_row[dq_score_per_row == 1]
        compliant_rows = data[data.index.isin(compliant.index)]  # type: ignore[index]

        non_compliant = dq_score_per_row[dq_score_per_row < 1]
        non_compliant_rows = data[data.index.isin(non_compliant.index)]  # type: ignore[index]

        log.info(
            f"Data quality score for rule {rule['id']} is {dq_score}, "
            f"with {len(compliant.index)} rows compliant and "  # type: ignore[arg-type]
            f"{len(non_compliant.index)} rows non-compliant"  # type: ignore[arg-type]
        )

        result = {**result, "dq_score": dq_score, "status": "success"}
    except Exception as e:
        log.exception(e)
    # END TRY

    return (
        result,
        annotate_detailed_results(
            data=compliant_rows,  # type: ignore[arg-type]
            business_rule_id=business_rule_id,
            data_field_qualified_name=data_field_qualified_name,
            data_quality_rule_description=data_quality_rule_description,
            data_quality_rule_dimension=data_quality_rule_dimension,
            result_id=result_id,
            test_date=test_date,
        ),
        annotate_detailed_results(
            data=non_compliant_rows,  # type: ignore[arg-type]
            business_rule_id=business_rule_id,
            data_field_qualified_name=data_field_qualified_name,
            data_quality_rule_description=data_quality_rule_description,
            data_quality_rule_dimension=data_quality_rule_dimension,
            result_id=result_id,
            test_date=test_date,
        ),
    )


# END run_quality_check
