"""Workspace license report package."""

from aurelius_license_report.models import ProjectSummary, ReportGenerationSettings, default_template_path
from aurelius_license_report.report import (
    build_context,
    discover_report_paths,
    empty_category_counts,
    empty_severity_counts,
    generate_workspace_report,
    merge_category_counts,
    merge_severity_counts,
    normalize_category,
    normalize_severity,
    relative_report_link,
    render_report,
    sort_projects,
    summarize_report,
)
from aurelius_license_report.settings import load_settings

__all__ = [
    "ProjectSummary",
    "ReportGenerationSettings",
    "build_context",
    "default_template_path",
    "discover_report_paths",
    "empty_category_counts",
    "empty_severity_counts",
    "generate_workspace_report",
    "load_settings",
    "merge_category_counts",
    "merge_severity_counts",
    "normalize_category",
    "normalize_severity",
    "relative_report_link",
    "render_report",
    "sort_projects",
    "summarize_report",
]
