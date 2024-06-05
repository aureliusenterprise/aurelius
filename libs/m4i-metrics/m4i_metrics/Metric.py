from abc import ABC, abstractmethod
from typing import Dict

from .MetricConfig import MetricConfig


class Metric(ABC):
    metric_label: str = 'metric'

    def get_name(self):
        return self.metric_label
    # END get_name

    @abstractmethod
    def calculate(model) -> Dict[str, Dict[str, MetricConfig]]:
        pass
    # END calculate
# END Metric
