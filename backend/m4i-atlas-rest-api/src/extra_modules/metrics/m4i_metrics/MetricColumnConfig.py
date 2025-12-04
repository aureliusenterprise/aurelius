from typing import Optional


class MetricColumnConfig:

    displayName: Optional[str]
    description: Optional[str]
    isNarrow: Optional[str]
    isStatic: Optional[bool]
    isTimestamp: Optional[bool]

    def __init__(
        self,
        description: Optional[str] = None,
        displayName: Optional[str] = None,
        isNarrow: Optional[bool] = None,
        isStatic: Optional[bool] = None,
        isTimestamp: Optional[bool] = False
    ):
        """
        Creates a new `MetricColumnConfig`

        :param description: An explanation of what the values in this column represent, defaults to None
        :type description: Optional[str]
        :param displayName: The human readable name of this column
        :type displayName: Optional[str]
        :param isNarrow: Whether or not the column should shrink to exactly fit its content
        :type isNarrow: Optional[bool]
        :param isStatic: Whether or not sorting should be disabled for this column
        :type isStatic: Optional[bool]
        :param isTimestamp: Whether or not this column represents a timestamp, defaults to False
        :type isTimestamp: Optional[bool]
        """

        self.displayName = displayName
        self.description = description
        self.isNarrow = isNarrow
        self.isStatic = isStatic
        self.isTimestamp = isTimestamp
    # END __init__

    def __dict__(self):
        return {
            'description': self.description,
            'displayName': self.displayName,
            'isNarrow': self.isNarrow,
            'isStatic': self.isStatic,
            'isTimestamp': self.isTimestamp
        }
    # END __dict__
# END MetricDataConfig
