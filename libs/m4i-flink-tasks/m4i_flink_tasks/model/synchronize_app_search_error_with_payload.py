from typing import List
from m4i_flink_tasks import SynchronizeAppSearchError
from m4i_flink_tasks.model.app_search_document import AppSearchDocument


class SynchronizeAppSearchWithPayloadError(SynchronizeAppSearchError):
    """Exception raised when elastic search results are not full, but contain partial results."""

    def __init__(self, message: str, partial_result: List[AppSearchDocument] = None) -> None:
        super().__init__(message)
        self.partial_result = partial_result if partial_result is not None else []
        # Store the original message separately for pickling
        self._message = message

    def __reduce__(self):
        """Support for pickling by returning constructor args."""
        # Use the original message, not str(self) which includes partial_result
        return (self.__class__, (self._message, []))

    def __str__(self) -> str:
        return f"{self._message}, Partial result count: {len(self.partial_result)}"
