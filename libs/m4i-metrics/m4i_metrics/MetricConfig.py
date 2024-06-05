from typing import Dict, Optional

from .MetricColumnConfig import MetricColumnConfig


class MetricConfig(object):

    data: Dict[str, MetricColumnConfig]
    description: str
    color_column: Optional[str]
    id_column: Optional[str]
    violation_column: Optional[str]
    docsUrl: Optional[str]

    def __init__(
        self,
        data: Dict[str, MetricColumnConfig],
        description: str,
        color_column: Optional[str] = None,
        id_column: Optional[str] = None,
        violation_column: Optional[str] = None,
        docsUrl: Optional[str] = None
    ):
        """
        Creates a new `MetricConfig`

        :param data: Each entry describes the shape of the dataset and how it should be presented to the user. Keyed by dataframe column name.
        :type data: Dict[str, MetricColumnConfig]
        :param description: One or two sentences explaining the meaning of this metric
        :type description: str
        :param color_column: The name of the column which contains the color group ID. Used for creating color views.
        :type color_column: str
        :param id_column: The name of the column which contains the concept ID. Used for associating exemptions with the violations found.
        :type id_column: str
        :param violation_column: The name of the column which contains a boolean value indication whether or not the current row represents a violation.
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

    def __dict__(self):
        return {
            'data': {key: value.__dict__() for key, value in self.data.items()},
            'description': self.description,
            'color_column': self.color_column,
            'id_column': self.id_column,
            'docsUrl': self.docsUrl
        }
    # END __dict__
# END MetricConfig
