from m4i_analytics.graphs.visualisations.model.Layout import Layout


class ManualLayout(Layout):
    @staticmethod
    def get_coordinates(graph, **kwargs):
        return kwargs.get("coords", {})

    # END get_coordinates

    @staticmethod
    def get_name():
        return "manual"

    # END get_name


# END ManualLayout
