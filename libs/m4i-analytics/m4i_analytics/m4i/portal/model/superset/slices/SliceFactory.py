from m4i_analytics.m4i.portal.model.superset.slices.BarSlice import BarSlice
from m4i_analytics.m4i.portal.model.superset.slices.BigNumberSlice import BigNumberSlice
from m4i_analytics.m4i.portal.model.superset.slices.CalHeatmapSlice import (
    CalHeatmapSlice,
)
from m4i_analytics.m4i.portal.model.superset.slices.ColorViewSlice import ColorViewSlice
from m4i_analytics.m4i.portal.model.superset.slices.DualLineSlice import DualLineSlice
from m4i_analytics.m4i.portal.model.superset.slices.FilterBoxSlice import FilterBoxSlice
from m4i_analytics.m4i.portal.model.superset.slices.HBubbleSlice import HBubbleSlice
from m4i_analytics.m4i.portal.model.superset.slices.JSONTableSlice import JSONTableSlice
from m4i_analytics.m4i.portal.model.superset.slices.ModelTreeNavigatorSlice import (
    ModelTreeNavigatorSlice,
)
from m4i_analytics.m4i.portal.model.superset.slices.ModelViewSlice import ModelViewSlice
from m4i_analytics.m4i.portal.model.superset.slices.PieChartSlice import PieChartSlice
from m4i_analytics.m4i.portal.model.superset.slices.RadarChartSlice import (
    RadarChartSlice,
)
from m4i_analytics.m4i.portal.model.superset.slices.TableSlice import TableSlice
from m4i_analytics.shared.model.Singleton import Singleton


class SliceFactory(Singleton):
    def __init__(self):
        self._slicetypes = [
            BarSlice,
            BigNumberSlice,
            CalHeatmapSlice,
            ColorViewSlice,
            DualLineSlice,
            FilterBoxSlice,
            HBubbleSlice,
            JSONTableSlice,
            ModelTreeNavigatorSlice,
            ModelViewSlice,
            PieChartSlice,
            RadarChartSlice,
            TableSlice,
        ]

    # END __init__

    def create(self, slicetype, **kwargs):
        """
        Generate new instance of the given slice type with the given
        arguments

        :returns: A new instance of the given slice type, or None if
            the given type does not exist. In case of multiple
            matchies, returns the first match found.
        :rtype: AbstractSlice

        :param str viz_type: The type name (as found in superset) of
            the slice type you want to create a new instance of
        :param any kwargs: Arguments to configure the new slice.
        """

        matching_types = [t for t in self._slicetypes if slicetype == t.VIZ_TYPE]
        return matching_types[0](**kwargs) if matching_types else None

    # END create


# END SliceFactory
