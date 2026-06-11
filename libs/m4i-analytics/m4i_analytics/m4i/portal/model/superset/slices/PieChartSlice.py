from m4i_analytics.m4i.portal.model.superset.slices.AbstractSlice import AbstractSlice


class PieChartSlice(AbstractSlice):
    VIZ_TYPE = "pie"

    def _init_params(
        self,
        annotation_layers=None,
        bar_stacked=False,
        bottom_margin="auto",
        color_pn=None,
        color_scheme="bnbColors",
        contribution=False,
        datasource=None,
        datasource_id=None,
        druid_datasource_id=None,
        date_filter=None,
        extra_filters=None,
        filters=None,
        granularity_sqla=None,
        groupby=None,
        having="",
        instant_filtering=False,
        limit=50,
        line_interpolation="linear",
        metric=None,
        metrics=None,
        num_period_compare="",
        order_desc=True,
        period_ratio_type="growth",
        resample_fillmethod=None,
        resample_how=None,
        resample_rule=None,
        rich_tooltip=True,
        rolling_type="None",
        show_bar_value=False,
        show_brush=False,
        show_controls=False,
        show_druid_time_granularity=False,
        show_druid_time_origin=False,
        show_legend=True,
        show_sqla_time_column=False,
        show_sqla_time_granularity=False,
        since="",
        slice_id=None,
        time_compare=None,
        time_grain_sqla=None,
        timeseries_limit_metric=None,
        until="now",
        url_params=None,
        reduce_x_ticks=False,
        viz_type=None,
        where="",
        x_axis_format="",
        x_axis_label="",
        x_axis_showminmax=True,
        y_axis_bounds=None,
        y_axis_format=".3s",
        y_axis_label="",
        y_log_scale=False,
        *arg,
        **kwarg,
    ):
        self.annotation_layers = annotation_layers if annotation_layers else []
        self.bar_stacked = bar_stacked
        self.bottom_margin = bottom_margin
        self.color_scheme = color_scheme
        self.contribution = contribution
        self.date_filter = date_filter
        self.extra_filters = extra_filters if extra_filters else []
        self.filters = filters if filters else []
        self.granularity_sqla = granularity_sqla
        self.groupby = groupby if groupby else []
        self.having = having
        self.instant_filtering = instant_filtering
        self.limit = limit
        self.line_interpolation = line_interpolation
        self.metric = metric
        self.metrics = [metric] if metric else []
        self.num_period_compare = num_period_compare
        self.order_desc = order_desc
        self.period_ratio_type = period_ratio_type
        self.resample_fillmethod = resample_fillmethod
        self.resample_how = resample_how
        self.resample_rule = resample_rule
        self.rich_tooltip = rich_tooltip
        self.rolling_type = rolling_type
        self.show_bar_value = show_bar_value
        self.show_brush = show_brush
        self.show_controls = show_controls
        self.show_druid_time_granularity = show_druid_time_granularity
        self.show_druid_time_origin = show_druid_time_origin
        self.show_legend = show_legend
        self.show_sqla_time_column = show_sqla_time_column
        self.show_sqla_time_granularity = show_sqla_time_granularity
        self.since = since
        self.time_compare = time_compare
        self.time_grain_sqla = time_grain_sqla
        self.timeseries_limit_metric = timeseries_limit_metric
        self.until = until
        self.reduce_x_ticks = reduce_x_ticks
        self.where = where
        self.x_axis_format = x_axis_format
        self.x_axis_label = x_axis_label
        self.x_axis_showminmax = x_axis_showminmax
        self.y_axis_bounds = y_axis_bounds if y_axis_bounds else [None, None]
        self.y_axis_label = y_axis_label
        self.y_log_scale = y_log_scale

    # END _init_params

    def columnNames(self):
        return list(set(super().columnNames() + self.groupby))

    # END directColumnDependencies


# END PieChartSlice
