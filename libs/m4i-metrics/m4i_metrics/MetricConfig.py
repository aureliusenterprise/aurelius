from typing import Any, Dict, Optional

from .MetricColumnConfig import MetricColumnConfig


class MetricConfig(object):
    data: Optional[Dict[str, MetricColumnConfig]]
    description: Optional[str]
    color_column: Optional[str]
    id_column: Optional[str]
    violation_column: Optional[str]
    docsUrl: Optional[str]

    def __init__(
        self,
        data: Optional[Dict[str, MetricColumnConfig]] = None,
        description: Optional[str] = None,
        color_column: Optional[str] = None,
        id_column: Optional[str] = None,
        violation_column: Optional[str] = None,
        docsUrl: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        Creates a new `MetricConfig`

        :param data: Each entry describes the shape of the dataset and how it should be presented to the user.
            Keyed by dataframe column name.
        :type data: Dict[str, MetricColumnConfig]
        :param description: One or two sentences explaining the meaning of this metric
        :type description: str
        :param color_column: The name of the column which contains the color group ID.
            Used for creating color views.
        :type color_column: str
        :param id_column: The name of the column which contains the concept ID.
            Used for associating exemptions with the violations found.
        :type id_column: str
        :param violation_column: The name of the column which contains a boolean value
            indicating whether or not the current row represents a violation.
        :type violation_column: str
        :param docsUrl: The url which points to the expanded documentation for this metric
        :type description: Optional[str]
        """

        self.data = data
        self.description = description
        self.color_column = color_column
        self.id_column = id_column
        self.violation_column = violation_column
        self.docsUrl = docsUrl

    # END __init__

    def to_dict(self) -> Dict[str, object]:
        result: Dict[str, object] = {
            "data": {key: value.to_dict() for key, value in self.data.items()} if self.data else {},
            "description": self.description,
            "color_column": self.color_column,
            "id_column": self.id_column,
            "docsUrl": self.docsUrl,
        }
        return result

    # END to_dict


# END MetricConfig
