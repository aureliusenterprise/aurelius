from m4i_analytics.m4i.portal.model.superset.slices.AbstractSlice import AbstractSlice


class RadarChartSlice(AbstractSlice):
    VIZ_TYPE = "radar_chart"

    def _init_params(
        self,
        all_columns_x=None,
        datasource=None,
        druid_datasource_id=None,
        filters=None,
        granularity_sqla=None,
        groupby=None,
        having="",
        limit=0,
        metrics=None,
        slice_id=None,
        since="",
        time_grain_sqla=None,
        until="now",
        url_params=None,
        viz_type=None,
        where="",
        *arg,
        **kwarg,
    ):
        self.all_columns_x = all_columns_x
        self.datasource = datasource
        self.filters = filters if filters else []
        self.granularity_sqla = granularity_sqla
        self.groupby = groupby if groupby else []
        self.having = having
        self.limit = limit
        self.metrics = metrics if metrics else []
        self.slice_id = slice_id
        self.since = since
        self.time_grain_sqla = time_grain_sqla
        self.until = until
        self.viz_type = viz_type
        self.where = where

    # END _init_params

    def columnNames(self):
        return list(set(super().columnNames() + [self.all_columns_x] + self.groupby))

    # END directColumnDependencies


# END RadarChartSlice
