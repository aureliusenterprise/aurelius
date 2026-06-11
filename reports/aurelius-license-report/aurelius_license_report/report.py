import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Union, cast

from jinja2 import Environment, FileSystemLoader, select_autoescape

from aurelius_license_report.constants import (
    CATEGORY_LEVELS,
    SEVERITY_LEVELS,
    SEVERITY_RANKS,
    SKIP_PATH_PARTS,
)
from aurelius_license_report.models import (
    LicenseFinding,
    ProjectReportContext,
    ProjectSummary,
    ProjectSummaryDict,
    ReportGenerationSettings,
    ScanResult,
    ScanResultDict,
    WorkspaceReportContext,
)

REPORT_FILENAME = "licenses.html"
JsonObject = Dict[str, object]
JsonObjectList = List[JsonObject]


def discover_report_paths(input_root: Path) -> List[Path]:
    """Find workspace license JSON files while skipping dependency caches."""
    report_paths = []
    for path in input_root.rglob("licenses.json"):
        if any(part in SKIP_PATH_PARTS for part in path.parts):
            continue
        report_paths.append(path)
    return sorted(report_paths)


def empty_severity_counts() -> Dict[str, int]:
    """Create a zeroed severity counter covering all supported levels."""
    return dict.fromkeys(SEVERITY_LEVELS, 0)


def empty_category_counts() -> Dict[str, int]:
    """Create a zeroed category counter covering all supported levels."""
    return dict.fromkeys(CATEGORY_LEVELS, 0)


def normalize_severity(value: object) -> str:
    """Map incoming severity values into the supported workspace labels."""
    severity = str(value or "UNKNOWN").upper()
    if severity in SEVERITY_RANKS:
        return severity
    return "UNKNOWN"


def normalize_category(value: object) -> str:
    """Map incoming category values into the supported workspace labels."""
    category = str(value or "unknown").strip().lower()
    if category in CATEGORY_LEVELS:
        return category
    return "other"


def merge_severity_counts(left: Dict[str, int], right: Dict[str, int]) -> Dict[str, int]:
    """Merge two severity count dictionaries."""
    return {severity: left.get(severity, 0) + right.get(severity, 0) for severity in SEVERITY_LEVELS}


def merge_category_counts(left: Dict[str, int], right: Dict[str, int]) -> Dict[str, int]:
    """Merge two category count dictionaries."""
    return {category: left.get(category, 0) + right.get(category, 0) for category in CATEGORY_LEVELS}


def relative_report_link(report_path: Path, output_path: Path) -> str:
    """Compute a relative link from the workspace report to a project HTML report."""
    return Path(os.path.relpath(report_path, output_path.parent)).as_posix()


def string_or_empty(value: object) -> str:
    """Return a string value or a safe empty default for missing fields."""
    if isinstance(value, str):
        return value
    return ""


def optional_string(value: object) -> Union[str, None]:
    """Return an optional string when the raw JSON field is present and typed correctly."""
    if isinstance(value, str) and value:
        return value
    return None


def optional_number(value: object) -> Union[float, None]:
    """Return an optional numeric value for confidence fields."""
    if isinstance(value, (int, float)):
        return float(value)
    return None


def is_license_result(raw_result: JsonObject) -> bool:
    """True when a Trivy result section represents license findings."""
    return string_or_empty(raw_result.get("Class")) == "license"


def build_license_findings(raw_result: JsonObject) -> List[LicenseFinding]:
    """Parse and sort license findings from a Trivy result entry."""
    findings = [
        LicenseFinding(
            severity=normalize_severity(finding.get("Severity")),
            category=normalize_category(finding.get("Category")),
            pkg_name=string_or_empty(finding.get("PkgName")),
            name=string_or_empty(finding.get("Name")),
            file_path=optional_string(finding.get("FilePath")),
            confidence=optional_number(finding.get("Confidence")),
            link=optional_string(finding.get("Link")),
            text=optional_string(finding.get("Text")),
        )
        for finding in cast("JsonObjectList", raw_result.get("Licenses") or [])
    ]
    return sorted(
        findings, key=lambda lic: (-SEVERITY_RANKS[lic.severity], lic.category, lic.pkg_name, lic.name)
    )


def build_scan_result(raw_result: JsonObject, severity_counts: Dict[str, int]) -> Tuple[ScanResultDict, int]:
    """Build one rendered scan section and update aggregate severity counters."""
    licenses = build_license_findings(raw_result)
    section_worst_severity = "UNKNOWN"
    section_category_counts = empty_category_counts()

    for finding in licenses:
        severity_counts[finding.severity] += 1
        section_category_counts[finding.category] += 1
        if SEVERITY_RANKS[finding.severity] > SEVERITY_RANKS[section_worst_severity]:
            section_worst_severity = finding.severity

    scan_result = cast(
        "ScanResultDict",
        {
            **ScanResult(
                target=string_or_empty(raw_result.get("Target")),
                type=string_or_empty(raw_result.get("Type")),
                licenses=licenses,
            ).model_dump(),
            **{"worst_severity": section_worst_severity, "category_counts": section_category_counts},
        },
    )
    return scan_result, len(licenses)


def summarize_report(report_path: Path, input_root: Path, output_path: Path) -> ProjectSummary:
    """Convert one Trivy JSON report into a workspace summary row."""
    report_data = json.loads(report_path.read_text(encoding="utf-8"))
    raw_results = cast("JsonObjectList", report_data.get("Results") or [])

    severity_counts = empty_severity_counts()
    category_counts = empty_category_counts()
    finding_count = 0
    target_count = 0
    worst_severity = "UNKNOWN"

    for raw_result in raw_results:
        if not is_license_result(raw_result):
            continue
        target_count += 1
        for finding in cast("JsonObjectList", raw_result.get("Licenses") or []):
            finding_count += 1
            severity = normalize_severity(finding.get("Severity"))
            category = normalize_category(finding.get("Category"))
            severity_counts[severity] += 1
            category_counts[category] += 1
            if SEVERITY_RANKS[severity] > SEVERITY_RANKS[worst_severity]:
                worst_severity = severity

    project_root = report_path.parent
    project_name = project_root.relative_to(input_root).as_posix()
    detail_report = output_path.parent / project_name / REPORT_FILENAME

    return ProjectSummary(
        finding_count=finding_count,
        target_count=target_count,
        name=project_name,
        report_link=relative_report_link(detail_report, output_path),
        severity_counts=severity_counts,
        category_counts=category_counts,
        worst_severity=worst_severity,
    )


def build_context(projects: List[ProjectSummary]) -> WorkspaceReportContext:
    """Build the template context for the workspace report page."""
    workspace_severity_counts = empty_severity_counts()
    workspace_category_counts = empty_category_counts()
    total_findings = 0
    projects_with_findings = 0

    for project in projects:
        workspace_severity_counts = merge_severity_counts(workspace_severity_counts, project.severity_counts)
        workspace_category_counts = merge_category_counts(workspace_category_counts, project.category_counts)
        total_findings += project.finding_count
        if project.finding_count > 0:
            projects_with_findings += 1

    return {
        "generated_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "projects": [cast("ProjectSummaryDict", project.model_dump()) for project in projects],
        "projects_scanned": len(projects),
        "projects_with_findings": projects_with_findings,
        "total_findings": total_findings,
        "workspace_severity_counts": workspace_severity_counts,
        "workspace_category_counts": workspace_category_counts,
    }


def render_report(
    context: Union[WorkspaceReportContext, ProjectReportContext], template_path: Path, output_path: Path
) -> None:
    """Render an HTML report to disk."""
    environment = Environment(
        autoescape=select_autoescape(["html", "xml"]),
        loader=FileSystemLoader(str(template_path.parent)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = environment.get_template(template_path.name)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template.render(report=context), encoding="utf-8")


def sort_projects(projects: List[ProjectSummary]) -> List[ProjectSummary]:
    """Sort projects by worst severity and then by total findings."""
    return sorted(
        projects,
        key=lambda project: (-SEVERITY_RANKS[project.worst_severity], -project.finding_count, project.name),
    )


def build_project_context(
    report_path: Path, workspace_report_link: str = f"../{REPORT_FILENAME}"
) -> ProjectReportContext:
    """Parse a Trivy JSON report into detailed template context for a project report."""
    report_data = json.loads(report_path.read_text(encoding="utf-8"))
    raw_results = cast("JsonObjectList", report_data.get("Results") or [])

    metadata = cast("JsonObject", report_data.get("Metadata") or {})
    component_name = metadata.get("Reference") or report_data.get("ArtifactName", report_path.parent.name)

    results: List[ScanResultDict] = []
    severity_counts = empty_severity_counts()
    category_counts = empty_category_counts()
    finding_count = 0

    for raw_result in raw_results:
        if not is_license_result(raw_result):
            continue
        result, section_total = build_scan_result(raw_result, severity_counts)
        finding_count += section_total
        category_counts = merge_category_counts(category_counts, result["category_counts"])
        results.append(result)

    sections_with_findings = sum(1 for result in results if result["licenses"])

    return {
        "generated_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "component_name": str(component_name),
        "workspace_report_link": workspace_report_link,
        "results": results,
        "sections_scanned": len(results),
        "sections_with_findings": sections_with_findings,
        "severity_counts": severity_counts,
        "category_counts": category_counts,
        "total_findings": finding_count,
    }


def generate_project_reports(settings: ReportGenerationSettings) -> None:
    """Generate per-project HTML reports for each discovered licenses.json."""
    input_root = settings.input_root.resolve()
    dist_root = settings.output.resolve().parent
    template_path = settings.project_template.resolve()

    for report_path in discover_report_paths(input_root):
        project_name = report_path.parent.relative_to(input_root).as_posix()
        output_path = dist_root / project_name / REPORT_FILENAME
        workspace_report_path = dist_root / REPORT_FILENAME
        workspace_report_link = relative_report_link(workspace_report_path, output_path)
        render_report(build_project_context(report_path, workspace_report_link), template_path, output_path)


def generate_workspace_report(settings: ReportGenerationSettings) -> None:
    """Generate the workspace license report using resolved settings."""
    input_root = settings.input_root.resolve()
    output_path = settings.output.resolve()
    template_path = settings.template.resolve()

    projects = sort_projects(
        [
            summarize_report(report_path, input_root, output_path)
            for report_path in discover_report_paths(input_root)
        ]
    )
    render_report(build_context(projects), template_path, output_path)
