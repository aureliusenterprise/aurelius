from pathlib import Path

from aurelius_license_report import (
    ProjectSummary,
    build_context,
    default_template_path,
    discover_report_paths,
    empty_category_counts,
    empty_severity_counts,
    merge_category_counts,
    merge_severity_counts,
    normalize_category,
    normalize_severity,
    relative_report_link,
    render_report,
    sort_projects,
    summarize_report,
)
from aurelius_license_report.models import ReportGenerationSettings
from aurelius_license_report.report import (
    build_project_context,
    generate_project_reports,
    generate_workspace_report,
)


def test__discover_report_paths_skips_ignored_directories(tmp_path: Path) -> None:
    """Test that discover_report_paths skips ignored directories like node_modules."""
    included = tmp_path / "apps" / "service-a" / "licenses.json"
    skipped = tmp_path / "node_modules" / "service-b" / "licenses.json"

    included.parent.mkdir(parents=True)
    skipped.parent.mkdir(parents=True)
    included.write_text("{}", encoding="utf-8")
    skipped.write_text("{}", encoding="utf-8")

    assert discover_report_paths(tmp_path) == [included]


def test__normalize_helpers_map_values() -> None:
    """Test that normalization helpers correctly map input values."""
    assert normalize_severity("high") == "HIGH"
    assert normalize_severity("invalid") == "UNKNOWN"
    assert normalize_category("restricted") == "restricted"
    assert normalize_category("unexpected") == "other"


def test__summarize_report_counts_only_license_class(tmp_path: Path) -> None:
    """Test that summarize_report counts only license class results."""
    input_root = tmp_path
    project_root = input_root / "apps" / "service-a"
    report_path = project_root / "licenses.json"
    output_path = input_root / "reports" / "dist" / "licenses.html"

    project_root.mkdir(parents=True)
    report_path.write_text(
        """
        {
          "Results": [
            {
              "Class": "os-pkgs",
              "Licenses": [{"Severity": "HIGH", "Category": "restricted"}]
            },
            {
              "Class": "license",
              "Target": "OS Packages",
              "Licenses": [
                {"Severity": "HIGH", "Category": "restricted"},
                {"Severity": "LOW", "Category": "notice"}
              ]
            }
          ]
        }
        """.strip(),
        encoding="utf-8",
    )

    summary = summarize_report(report_path, input_root, output_path)

    assert summary.name == "apps/service-a"
    assert summary.finding_count == 2
    assert summary.target_count == 1
    assert summary.worst_severity == "HIGH"
    assert summary.report_link == "apps/service-a/licenses.html"
    assert summary.severity_counts == {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 0, "LOW": 1, "UNKNOWN": 0}
    assert summary.category_counts["restricted"] == 1
    assert summary.category_counts["notice"] == 1


def test__sort_projects_orders_by_severity_then_finding_count() -> None:
    """Test that sort_projects orders projects by severity level then finding count."""
    low_counts = empty_severity_counts()
    low_counts["LOW"] = 1
    low_categories = empty_category_counts()

    high_counts = empty_severity_counts()
    high_counts["HIGH"] = 2
    high_categories = empty_category_counts()

    critical_counts = empty_severity_counts()
    critical_counts["CRITICAL"] = 1
    critical_categories = empty_category_counts()

    projects = [
        ProjectSummary(
            finding_count=1,
            target_count=1,
            name="apps/low",
            report_link="apps/low/licenses.html",
            severity_counts=low_counts,
            category_counts=low_categories,
            worst_severity="LOW",
        ),
        ProjectSummary(
            finding_count=2,
            target_count=1,
            name="apps/high",
            report_link="apps/high/licenses.html",
            severity_counts=high_counts,
            category_counts=high_categories,
            worst_severity="HIGH",
        ),
        ProjectSummary(
            finding_count=1,
            target_count=1,
            name="apps/critical",
            report_link="apps/critical/licenses.html",
            severity_counts=critical_counts,
            category_counts=critical_categories,
            worst_severity="CRITICAL",
        ),
    ]

    assert [project.name for project in sort_projects(projects)] == ["apps/critical", "apps/high", "apps/low"]


def test__count_merges_cover_all_levels() -> None:
    """Test that count merge functions properly combine counts from multiple sources."""
    left_severity = empty_severity_counts()
    left_severity["HIGH"] = 2
    right_severity = empty_severity_counts()
    right_severity["LOW"] = 1

    merged_severity = merge_severity_counts(left_severity, right_severity)
    assert merged_severity["HIGH"] == 2
    assert merged_severity["LOW"] == 1

    left_category = empty_category_counts()
    left_category["restricted"] = 3
    right_category = empty_category_counts()
    right_category["notice"] = 2

    merged_category = merge_category_counts(left_category, right_category)
    assert merged_category["restricted"] == 3
    assert merged_category["notice"] == 2


def test__relative_report_link_computes_path_from_workspace_to_project() -> None:
    """Test that relative_report_link correctly computes relative paths."""
    report_path = Path("dist/apps/service-a/licenses.html")
    output_path = Path("dist/workspace/licenses.html")

    link = relative_report_link(report_path, output_path)

    assert link == "../apps/service-a/licenses.html"


def test__build_project_context_parses_license_results(tmp_path: Path) -> None:
    """Test that build_project_context correctly parses license results from JSON."""
    report_path = tmp_path / "licenses.json"
    report_path.write_text(
        """
        {
          "Metadata": {"Reference": "my-service:latest"},
          "Results": [
            {
              "Class": "license",
              "Target": "OS Packages",
              "Type": "debian",
              "Licenses": [
                {
                  "Severity": "HIGH",
                  "Category": "restricted",
                  "PkgName": "apt",
                  "Name": "GPL-2.0-only",
                  "FilePath": "",
                  "Confidence": 1,
                  "Link": ""
                },
                {
                  "Severity": "LOW",
                  "Category": "notice",
                  "PkgName": "curl",
                  "Name": "MIT",
                  "FilePath": "",
                  "Confidence": 1,
                  "Link": ""
                }
              ]
            },
            {
              "Class": "lang-pkgs",
              "Target": "Python",
              "Type": "python-pkg",
              "Packages": []
            }
          ]
        }
        """.strip(),
        encoding="utf-8",
    )

    context = build_project_context(report_path)

    assert context["component_name"] == "my-service:latest"
    assert context["sections_scanned"] == 1
    assert context["sections_with_findings"] == 1
    assert context["total_findings"] == 2
    assert context["severity_counts"]["HIGH"] == 1
    assert context["severity_counts"]["LOW"] == 1
    assert context["category_counts"]["restricted"] == 1
    assert context["category_counts"]["notice"] == 1


def test__build_context_aggregates_workspace_summary() -> None:
    """Test that build_context properly aggregates workspace-level summaries."""
    low_counts = empty_severity_counts()
    low_counts["LOW"] = 1
    low_categories = empty_category_counts()
    low_categories["notice"] = 1

    high_counts = empty_severity_counts()
    high_counts["HIGH"] = 2
    high_categories = empty_category_counts()
    high_categories["restricted"] = 2

    projects = [
        ProjectSummary(
            finding_count=1,
            target_count=1,
            name="apps/service-a",
            report_link="apps/service-a/licenses.html",
            severity_counts=low_counts,
            category_counts=low_categories,
            worst_severity="LOW",
        ),
        ProjectSummary(
            finding_count=2,
            target_count=1,
            name="apps/service-b",
            report_link="apps/service-b/licenses.html",
            severity_counts=high_counts,
            category_counts=high_categories,
            worst_severity="HIGH",
        ),
    ]

    context = build_context(projects)

    assert context["projects_scanned"] == 2
    assert context["projects_with_findings"] == 2
    assert context["total_findings"] == 3
    assert context["workspace_severity_counts"]["HIGH"] == 2
    assert context["workspace_category_counts"]["restricted"] == 2


def test__render_report_outputs_empty_state_when_no_projects_exist(tmp_path: Path) -> None:
    """Test that render_report outputs an empty state message when no projects exist."""
    output_path = tmp_path / "reports" / "dist" / "workspace" / "licenses.html"

    render_report(build_context([]), default_template_path(), output_path)

    rendered = output_path.read_text(encoding="utf-8")
    assert "No project reports discovered" in rendered
    assert "License Report" in rendered


def test__generate_project_reports_creates_html_for_each_report(tmp_path: Path) -> None:
    """Test that generate_project_reports creates HTML reports for each project."""
    input_root = tmp_path / "workspace"
    output_dir = tmp_path / "dist"

    service_a = input_root / "apps" / "service-a"
    service_b = input_root / "docker" / "base"

    for service in [service_a, service_b]:
        service.mkdir(parents=True)
        (service / "licenses.json").write_text(
            """
            {
              "Results": [
                {
                  "Class": "license",
                  "Target": "OS Packages",
                  "Type": "debian",
                  "Licenses": [{"Severity": "LOW", "Category": "notice", "PkgName": "x", "Name": "MIT"}]
                }
              ]
            }
            """.strip(),
            encoding="utf-8",
        )

    settings = ReportGenerationSettings(input_root=input_root, output=output_dir / "licenses.html")

    generate_project_reports(settings)

    assert (output_dir / "apps" / "service-a" / "licenses.html").exists()
    assert (output_dir / "docker" / "base" / "licenses.html").exists()


def test__generate_workspace_report_creates_summary_page(tmp_path: Path) -> None:
    """Test that generate_workspace_report creates a summary page for all projects."""
    input_root = tmp_path / "workspace"
    service_a = input_root / "apps" / "service-a"
    service_a.mkdir(parents=True)

    (service_a / "licenses.json").write_text(
        """
        {
          "Results": [
            {
              "Class": "license",
              "Target": "OS Packages",
              "Type": "debian",
              "Licenses": [{
                "Severity": "HIGH",
                "Category": "restricted",
                "PkgName": "a",
                "Name": "GPL-2.0-only"
              }]
            }
          ]
        }
        """.strip(),
        encoding="utf-8",
    )

    output_file = tmp_path / "reports" / "licenses.html"
    settings = ReportGenerationSettings(input_root=input_root, output=output_file)

    generate_workspace_report(settings)

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "License Report" in content
    assert "apps/service-a" in content
