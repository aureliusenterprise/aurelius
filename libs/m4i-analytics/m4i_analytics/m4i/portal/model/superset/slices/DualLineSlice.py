from m4i_analytics.m4i.portal.model.superset.slices.AbstractSlice import AbstractSlice


class DualLineSlice(AbstractSlice):
    VIZ_TYPE = "dual_line"

    def _init_params(
        self,
        annotation_layers=None,
        color_scheme="bnbColors",
        datasource=None,
        domain_granularity=None,
        druid_datasource_id=None,
        filters=None,
        granularity_sqla=None,
        having="",
        metric=None,
        metric_2=None,
        since="",
        slice_id=None,
        subdomain_granularity=None,
        time_grain_sqla=None,
        until="now",
        url_params=None,
        viz_type=None,
        where="",
        x_axis_format=None,
        y_axis_format=".3s",
        y_axis_2_format=".3s",
        *arg,
        **kwarg,
    ):
        self.annotation_layers = annotation_layers if annotation_layers is not None else []
        self.color_scheme = color_scheme
        self.domain_granularity = domain_granularity
        self.filters = filters if filters is not None else []
        self.granularity_sqla = granularity_sqla
        self.having = having
        self.metric = metric
        self.metric_2 = metric_2
        self.metrics = [metric, metric_2]
        self.since = since
        self.time_grain_sqla = time_grain_sqla
        self.where = where
        self.x_axis_format = x_axis_format
        self.color_scheme = color_scheme
        self.granularity_sqla = granularity_sqla
        self.subdomain_granularity = subdomain_granularity
        self.time_grain_sqla = time_grain_sqla
        self.until = until

    # END _init_params


# END DualLineSlice
