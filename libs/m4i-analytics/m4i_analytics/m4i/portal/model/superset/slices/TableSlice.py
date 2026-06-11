from m4i_analytics.m4i.portal.model.superset.slices.AbstractSlice import AbstractSlice


class TableSlice(AbstractSlice):
    VIZ_TYPE = "table"

    def _init_params(
        self,
        all_columns=None,
        all_columns_x=None,
        all_columns_y=None,
        annotation_layers=None,
        bar_stacked=None,
        bottom_margin=None,
        cache_timeout=None,
        canvas_image_rendering=None,
        charge=None,
        code=None,
        collapsed_fieldsets=None,
        color_scheme=None,
        columns=None,
        combine_metric=None,
        compare_lag=None,
        compare_suffix=None,
        contribution=None,
        country_fieldtype=None,
        datasource=None,
        date_filter=None,
        domain_granularity=None,
        donut=None,
        druid_datasource_id=None,
        entity=None,
        filters=None,
        granularity=None,
        granularity_sqla=None,
        groupby=None,
        having="",
        include_search=False,
        include_time=False,
        instant_filtering=False,
        labels_outside=None,
        left_margin=None,
        limit=None,
        line_interpolation=None,
        linear_color_scheme=None,
        link_length=None,
        mapbox_style=None,
        markup_type=None,
        max_bubble_size=None,
        metric=None,
        metric_2=None,
        metrics=None,
        min_periods=None,
        normalize_across=None,
        num_period_compare=None,
        number_format=None,
        order_bars=None,
        order_by_cols=None,
        order_desc=True,
        page_length=0,
        pandas_aggfunc=None,
        period_ratio_type=None,
        pie_label_type=None,
        pivot_margins=None,
        reduce_x_ticks=None,
        resample_fillmethod=None,
        resample_how=None,
        resample_rule=None,
        rich_tooltip=None,
        rolling_periods=None,
        rolling_type=None,
        rotation=None,
        row_limit=None,
        secondary_metric=None,
        series=None,
        show_bar_value=None,
        show_brush=None,
        show_bubbles=None,
        show_controls=None,
        show_druid_time_granularity=None,
        show_druid_time_origin=None,
        show_legend=None,
        show_markers=None,
        show_sqla_time_column=None,
        show_sqla_time_granularity=None,
        since="",
        size=None,
        size_from=None,
        size_to=None,
        slice_id=None,
        slice_name=None,
        subdomain_granularity=None,
        subheader=None,
        table_filter=False,
        table_timestamp_format=None,
        time_compare=None,
        time_grain_sqla=None,
        timeseries_limit_metric=None,
        until="now",
        url_params=None,
        viz_type=None,
        where="",
        whisker_options=None,
        x=None,
        x_axis_bounds=None,
        x_axis_format=None,
        x_axis_label=None,
        x_axis_showminmax=None,
        x_log_scale=None,
        xscale_interval=None,
        y=None,
        y_axis_bounds=None,
        y_axis_format=None,
        y_axis_label=None,
        y_axis_showminmax=None,
        y_log_scale=None,
        yscale_interval=None,
        *arg,
        **kwarg,
    ):
        self.all_columns = all_columns if all_columns else []
        self.collapsed_fieldsets = collapsed_fieldsets
        self.filters = filters if filters else []
        self.granularity_sqla = granularity_sqla
        self.groupby = groupby if groupby else []
        self.having = having
        self.include_search = include_search
        self.include_time = include_time
        self.metrics = (metrics if metrics else []) + [combine_metric, metric, metric_2, secondary_metric]
        self.order_by_cols = order_by_cols if order_by_cols else []
        self.order_desc = order_desc
        self.page_length = page_length
        self.row_limit = row_limit
        self.since = since
        self.table_filter = table_filter
        self.table_timestamp_format = table_timestamp_format
        self.time_grain_sqla = time_grain_sqla
        self.timeseries_limit_metric = timeseries_limit_metric
        self.until = until
        self.where = where

    # END _init_params

    def columnNames(self):
        return list(set(super().columnNames() + self.groupby + self.order_by_cols + self.all_columns))

    # END directColumnDependencies


# END TableSlice
