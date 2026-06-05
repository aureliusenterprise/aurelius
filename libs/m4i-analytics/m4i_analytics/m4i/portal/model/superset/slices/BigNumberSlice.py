from m4i_analytics.m4i.portal.model.superset.slices.AbstractSlice import AbstractSlice


class BigNumberSlice(AbstractSlice):
    VIZ_TYPE = "big_number"

    def _init_params(
        self,
        compare_lag=0,
        datasource=None,
        druid_datasource_id=None,
        filters=None,
        granularity_sqla=None,
        having="",
        metric=None,
        metrics=None,
        since="",
        slice_id=None,
        time_grain_sqla=None,
        until="now",
        url_params=None,
        viz_type=None,
        where="",
        y_axis_format=".3s",
        *arg,
        **kwarg,
    ):
        self.compare_lag = compare_lag
        self.filters = filters if filters is not None else []
        self.granularity_sqla = granularity_sqla
        self.having = having
        self.metric = metric
        self.metrics = metrics if metrics is not None else []
        self.since = since
        self.time_grain_sqla = time_grain_sqla
        self.until = until
        self.where = where
        self.y_axis_format = y_axis_format

    # END _init_params


# END BigNumberSlice
