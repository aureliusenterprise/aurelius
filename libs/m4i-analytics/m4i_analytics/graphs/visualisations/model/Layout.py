from abc import ABC, abstractmethod


class Layout(ABC):
    @staticmethod
    @abstractmethod
    def get_coordinates(graph, **kwargs):
        raise NotImplementedError("The get_coordinates method has not been implemented for this layout!")

    # END get_coordinates

    @staticmethod
    @abstractmethod
    def get_name():
        raise NotImplementedError("The name property has not been implemented for this layout!")

    # END get_name


# END Layout
