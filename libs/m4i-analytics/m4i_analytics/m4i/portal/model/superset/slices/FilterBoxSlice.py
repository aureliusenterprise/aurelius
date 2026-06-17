from m4i_analytics.m4i.portal.model.superset.slices.AbstractSlice import AbstractSlice


class FilterBoxSlice(AbstractSlice):
    VIZ_TYPE = "filter_box"

    def _init_params(
        self,
        datasource=None,
        date_filter=False,
        druid_datasource_id=None,
        filters=None,
        groupby=None,
        granularity_sqla=None,
        having="",
        instant_filtering=True,
        metric=None,
        metrics=None,
        show_druid_time_origin=False,
        show_druid_time_granularity=False,
        show_sqla_time_column=False,
        show_sqla_time_granularity=False,
        since="",
        slice_id=None,
        time_grain_sqla=None,
        until="now",
        url_params=None,
        viz_type=None,
        where="",
        *arg,
        **kwarg,
    ):
        self.granularity_sqla = granularity_sqla
        self.metric = metric
        self.metrics = [metric]
        self.since = since
        self.time_grain_sqla = time_grain_sqla
        self.date_filter = date_filter
        self.filters = filters if filters is not None else []
        self.groupby = groupby if groupby is not None else []
        self.having = having
        self.instant_filtering = instant_filtering
        self.show_druid_time_origin = show_druid_time_origin
        self.show_druid_time_granularity = show_druid_time_granularity
        self.until = until
        self.where = where

    # END _init_params

    def columnNames(self):
        return list(set(super().columnNames() + self.groupby))

    # END directColumnDependencies


# END FilterBoxSlice
