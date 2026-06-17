from abc import ABC, abstractmethod
from typing import Any, Dict


class Metric(ABC):
    metric_label: str = "metric"
    id: str = ""
    label: str = ""

    def get_name(self) -> str:
        return self.metric_label

    # END get_name

    @abstractmethod
    def calculate(self, model: Any) -> Dict[str, Any]:
        pass

    # END calculate


# END Metric
