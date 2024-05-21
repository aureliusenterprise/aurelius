from flink_tasks import SynchronizeAppSearchError
from flink_tasks.model.app_search_document import AppSearchDocument


class SynchronizeAppSearchWithPayloadError(SynchronizeAppSearchError):
    """Exception raised when elastic search results are not full, but contain partial results."""

    def __init__(self, message: str, partial_result: list[AppSearchDocument]) -> None:
        super().__init__(message)
        self.partial_result = partial_result

    def __str__(self) -> str:
        return f"{super().__str__()}, Partial result: {self.partial_result}"
