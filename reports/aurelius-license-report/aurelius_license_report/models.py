from pathlib import Path
from typing import TypedDict, Union, Dict, List

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def default_template_path() -> Path:
    """Return the bundled workspace summary template path."""
    return Path(__file__).resolve().parent.parent / "template" / "report.tpl"


def default_project_template_path() -> Path:
    """Return the bundled project detail template path."""
    return Path(__file__).resolve().parent.parent / "template" / "project.tpl"


class LicenseFinding(BaseModel):
    """A single license finding from a Trivy license scan result."""

    model_config = ConfigDict(frozen=True)

    severity: str
    category: str
    pkg_name: str
    name: str
    file_path: Union[str, Path, None] = None
    confidence: Union[float, None] = None
    link: Union[str, None] = None
    text: Union[str, None] = None


class ScanResult(BaseModel):
    """A single target result section from a Trivy license report."""

    model_config = ConfigDict(frozen=True)

    target: str
    type: str
    licenses: List[LicenseFinding] = Field(default_factory=list)


class ProjectSummary(BaseModel):
    """Normalized project-level summary for the workspace report."""

    model_config = ConfigDict(frozen=True)

    finding_count: int
    target_count: int
    name: str
    report_link: str
    severity_counts: Dict[str, int]
    category_counts: Dict[str, int]
    worst_severity: str


class ReportGenerationSettings(BaseSettings):
    """CLI and environment-backed settings for workspace report generation."""

    model_config = SettingsConfigDict(env_prefix="AURELIUS_LICENSE_REPORT_", extra="ignore")

    input_root: Path = Path()
    output: Path = Path("reports/aurelius-license-report/dist/licenses.html")
    project_template: Path = Field(default_factory=default_project_template_path)
    template: Path = Field(default_factory=default_template_path)


class LicenseFindingDict(TypedDict):
    """Serialized form of LicenseFinding as returned by model_dump()."""

    severity: str
    category: str
    pkg_name: str
    name: str
    file_path: Union[str, Path, None]
    confidence: Union[float, None]
    link: Union[str, None]
    text: Union[str, None]


class ScanResultDict(TypedDict):
    """Serialized form of ScanResult as returned by model_dump()."""

    target: str
    type: str
    licenses: List[LicenseFindingDict]
    worst_severity: str
    category_counts: Dict[str, int]


class ProjectSummaryDict(TypedDict):
    """Serialized form of ProjectSummary as returned by model_dump()."""

    finding_count: int
    target_count: int
    name: str
    report_link: str
    severity_counts: Dict[str, int]
    category_counts: Dict[str, int]
    worst_severity: str


class ProjectReportContext(TypedDict):
    """Template context for a per-project license report."""

    generated_at: str
    component_name: str
    workspace_report_link: str
    results: List[ScanResultDict]
    sections_scanned: int
    sections_with_findings: int
    severity_counts: Dict[str, int]
    category_counts: Dict[str, int]
    total_findings: int


class WorkspaceReportContext(TypedDict):
    """Template context for the workspace summary report."""

    generated_at: str
    projects: List[ProjectSummaryDict]
    projects_scanned: int
    projects_with_findings: int
    total_findings: int
    workspace_severity_counts: Dict[str, int]
    workspace_category_counts: Dict[str, int]
