from m4i_analytics.m4i.portal.model.superset.slices.AbstractSlice import AbstractSlice


class CalHeatmapSlice(AbstractSlice):
    VIZ_TYPE = "cal_heatmap"

    def _init_params(
        self,
        datasource=None,
        domain_granularity=None,
        druid_datasource_id=None,
        filters=None,
        granularity_sqla=None,
        having="",
        metric=None,
        metrics=None,
        since="",
        slice_id=None,
        subdomain_granularity=None,
        time_grain_sqla=None,
        until="now",
        url_params=None,
        viz_type=None,
        where="",
        *arg,
        **kwarg,
    ):
        self.domain_granularity = domain_granularity
        self.filters = filters if filters is not None else []
        self.granularity_sqla = granularity_sqla
        self.having = having
        self.metric = metric
        self.metrics = metrics if metrics is not None else []
        self.since = since
        self.subdomain_granularity = subdomain_granularity
        self.time_grain_sqla = time_grain_sqla
        self.until = until
        self.where = where

    # END _init_params


# END CalHeatmapSlice
