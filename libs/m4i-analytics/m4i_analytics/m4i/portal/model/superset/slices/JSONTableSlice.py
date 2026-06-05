from m4i_analytics.m4i.portal.model.superset.slices.AbstractSlice import AbstractSlice


class JSONTableSlice(AbstractSlice):
    VIZ_TYPE = "json_table"

    def _init_params(
        self,
        datasource=None,
        druid_datasource_id=None,
        filters=None,
        granularity_sqla=None,
        having="",
        metrics=None,
        time_grain_sqla=None,
        since="",
        slice_id=None,
        until="now",
        url_params=None,
        viz_type=None,
        where="",
        *arg,
        **kwarg,
    ):
        self.filters = filters if filters is not None else []
        self.granularity_sqla = granularity_sqla
        self.having = having
        self.since = since
        self.time_grain_sqla = time_grain_sqla
        self.metrics = metrics if metrics is not None else []
        self.until = until
        self.where = where

    # END _init_params


# END JSONTableSlice
