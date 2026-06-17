from m4i_analytics.m4i.portal.model.superset.slices.AbstractSlice import AbstractSlice


class HBubbleSlice(AbstractSlice):
    VIZ_TYPE = "hbubble"

    def _init_params(
        self,
        annotation_layers=None,
        bottom_margin=0,
        color_scheme="bnbColors",
        datasource=None,
        druid_datasource_id=None,
        entity=None,
        filters=None,
        granularity_sqla=None,
        having="",
        left_margin=0,
        limit=0,
        max_bubble_size=0,
        metric=None,
        metric_2=None,
        series=None,
        show_legend=True,
        since="",
        size=None,
        slice_id=None,
        time_grain_sqla=None,
        until="now",
        url_params=None,
        viz_type=None,
        where="",
        x=0,
        x_axis_format=None,
        x_axis_label=None,
        x_axis_showminmax=True,
        x_log_scale=False,
        y=0,
        y_axis_format=".3s",
        y_axis_2_format=".3s",
        y_axis_label=None,
        y_axis_showminmax=True,
        y_log_scale=False,
        *arg,
        **kwarg,
    ):
        self.annotation_layers = annotation_layers
        self.bottom_margin = bottom_margin
        self.color_scheme = color_scheme
        self.entity = entity
        self.filters = filters
        self.granularity_sqla = granularity_sqla
        self.having = having
        self.left_margin = left_margin
        self.limit = limit
        self.max_bubble_size = max_bubble_size
        self.metric = metric
        self.metric_2 = metric_2
        self.metrics = [metric, metric_2, entity]
        self.series = series
        self.since = since
        self.time_grain_sqla = time_grain_sqla
        self.where = where
        self.x = x
        self.x_axis_format = x_axis_format
        self.x_axis_label = x_axis_label
        self.x_log_scale = x_log_scale
        self.x_axis_showminmax = x_axis_showminmax
        self.color_scheme = color_scheme
        self.granularity_sqla = granularity_sqla
        self.show_legend = show_legend
        self.size = size
        self.time_grain_sqla = time_grain_sqla
        self.until = until
        self.y = y
        self.y_axis_label = y_axis_label
        self.y_axis_showminmax = y_axis_showminmax
        self.y_log_scale = y_log_scale

    # END _init_params


# END HBubbleSlice
