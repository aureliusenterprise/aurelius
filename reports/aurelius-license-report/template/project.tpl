<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>{{ report.component_name }} - License Report</title>
		<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css">
		<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">
		<style>
			:root {
				--brand-teal: #16c7a0;
				--brand-teal-dark: #11ab8a;
				--brand-green: #45d18b;
				--brand-blue: #2f6dff;
				--brand-blue-light: #1db8e7;
				--brand-indigo: #2a3f8f;
				--brand-primary: #16c7a0;
				--brand-primary-hover: #11ab8a;
				--report-shadow: 0 20px 50px color-mix(in srgb, var(--bulma-text-strong) 14%, transparent);
			}
			* {
				margin: 0;
			}
			body {
				min-height: 100vh;
				display: flex;
				flex-direction: column;
				color: var(--bulma-text);
				background:
					radial-gradient(
						circle at top left,
						color-mix(in srgb, var(--brand-blue-light) 20%, transparent),
						transparent 35%
					),
					linear-gradient(
						180deg,
						color-mix(in srgb, var(--bulma-scheme-main) 90%, var(--brand-blue-light) 10%) 0%,
						var(--bulma-scheme-main) 24%,
						color-mix(in srgb, var(--bulma-scheme-main) 92%, var(--brand-green) 8%) 100%
					);
			}
			.navbar {
				background-color: var(--bulma-scheme-main);
				padding: 0.75rem 1.5rem;
				border-bottom: 1px solid var(--bulma-border);
				box-shadow: inset 0 -1px 0 color-mix(in srgb, var(--brand-blue-light) 35%, transparent);
			}
			.navbar-brand .navbar-item {
				color: inherit;
				font-weight: 700;
				font-size: 1.1rem;
				letter-spacing: -0.02em;
				transition: color 0.2s ease;
			}
			.navbar .navbar-item,
			.navbar .navbar-link {
				color: inherit;
			}
			.navbar .navbar-item:hover,
			.navbar .navbar-link:hover {
				color: var(--brand-teal);
				background-color: transparent;
			}
			.navbar .navbar-item.is-active {
				color: var(--brand-teal) !important;
			}
			.brand-name {
				color: inherit;
			}
			.hero-gradient {
				background: linear-gradient(
					90deg,
					color-mix(in srgb, var(--brand-blue) 32%, var(--bulma-scheme-main)),
					color-mix(in srgb, var(--brand-green) 24%, var(--bulma-scheme-main))
				);
				border-bottom: 1px solid color-mix(in srgb, var(--brand-blue-light) 30%, var(--bulma-border));
			}
			.hero-gradient .title,
			.hero-gradient .subtitle,
			.hero-gradient .timestamp {
				color: var(--bulma-text-strong);
			}
			.section {
				padding: 1.25rem 0.75rem;
			}
			.summary-card {
				border-radius: 16px;
				border: 1px solid var(--bulma-border);
				box-shadow: var(--report-shadow);
				background: color-mix(in srgb, var(--bulma-scheme-main) 92%, transparent);
				padding: 1rem 1.25rem;
				height: 100%;
			}
			.summary-visual-card {
				padding: 1.1rem 1.25rem 1.2rem;
			}
			.summary-count {
				font-size: 2rem;
				font-weight: 700;
				line-height: 1;
				color: var(--bulma-text-strong);
			}
			.summary-label {
				font-size: 0.85rem;
				text-transform: uppercase;
				letter-spacing: 0.04em;
				font-weight: 600;
				color: var(--bulma-text);
			}
			.summary-visual-header {
				display: flex;
				justify-content: space-between;
				align-items: baseline;
				gap: 1rem;
				margin-bottom: 0.85rem;
			}
			.summary-visual-title {
				font-size: 0.95rem;
				font-weight: 700;
				color: var(--bulma-text-strong);
			}
			.summary-visual-note {
				font-size: 0.82rem;
				color: var(--bulma-text);
			}
			.severity-bar {
				display: flex;
				width: 100%;
				height: 0.8rem;
				border-radius: 999px;
				overflow: hidden;
				background: color-mix(in srgb, var(--bulma-border) 55%, var(--bulma-scheme-main));
				box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--bulma-border) 75%, transparent);
			}
			.severity-segment {
				height: 100%;
				min-width: 0;
				flex: 0 0 auto;
			}
			.tone-critical {
				background: color-mix(in srgb, var(--bulma-danger) 46%, var(--brand-indigo) 54%);
			}
			.tone-high {
				background: color-mix(in srgb, var(--bulma-danger) 88%, var(--bulma-scheme-main));
			}
			.tone-medium {
				background: color-mix(in srgb, var(--bulma-warning) 78%, var(--bulma-scheme-main));
			}
			.tone-low {
				background: color-mix(in srgb, var(--bulma-success) 74%, var(--bulma-scheme-main));
			}
			.tone-unknown {
				background: color-mix(in srgb, var(--bulma-border) 72%, var(--bulma-scheme-main));
			}
			.tone-restricted {
				background: color-mix(in srgb, var(--bulma-danger) 88%, var(--bulma-scheme-main));
			}
			.tone-reciprocal {
				background: color-mix(in srgb, var(--bulma-warning) 78%, var(--bulma-scheme-main));
			}
			.tone-notice {
				background: color-mix(in srgb, var(--bulma-success) 74%, var(--bulma-scheme-main));
			}
			.confidence-dot-high {
				background: color-mix(in srgb, var(--bulma-success) 74%, var(--bulma-scheme-main));
			}
			.confidence-dot-medium {
				background: color-mix(in srgb, var(--bulma-warning) 78%, var(--bulma-scheme-main));
			}
			.confidence-dot-low {
				background: color-mix(in srgb, var(--bulma-danger) 88%, var(--bulma-scheme-main));
			}
			.legend-row {
				display: flex;
				flex-wrap: wrap;
				gap: 0.45rem;
			}
			.legend-chip {
				display: inline-flex;
				align-items: center;
				gap: 0.35rem;
				padding: 0.2rem 0.45rem;
				border-radius: 999px;
				font-size: 0.72rem;
				font-weight: 700;
				background: color-mix(in srgb, var(--bulma-scheme-main) 90%, transparent);
				border: 1px solid color-mix(in srgb, var(--bulma-border) 72%, transparent);
				color: var(--bulma-text-strong);
			}
			.legend-swatch {
				width: 0.55rem;
				height: 0.55rem;
				border-radius: 999px;
				flex: 0 0 auto;
			}
			.report-card {
				border-radius: 16px;
				box-shadow: var(--report-shadow);
				border: 1px solid var(--bulma-border);
				background: color-mix(in srgb, var(--bulma-scheme-main) 92%, transparent);
				overflow: hidden;
			}
			.report-card .card-header {
				background: linear-gradient(
					90deg,
					color-mix(in srgb, var(--brand-blue) 20%, var(--bulma-scheme-main)),
					color-mix(in srgb, var(--brand-green) 12%, var(--bulma-scheme-main))
				);
				border-bottom: 1px solid var(--bulma-border);
				padding: 1.25rem 1.5rem;
			}
			.report-card .card-header-main {
				display: flex;
				justify-content: space-between;
				align-items: center;
				gap: 1rem;
				width: 100%;
			}
			.report-card .section-controls {
				display: inline-flex;
				align-items: center;
				gap: 0.6rem;
				margin-left: auto;
			}
			.report-card .count-cluster {
				display: inline-flex;
				align-items: center;
				gap: 0.35rem;
			}
			.report-card .count-pill {
				display: inline-flex;
				align-items: center;
				gap: 0.25rem;
				padding: 0.2rem 0.45rem;
				border-radius: 999px;
				font-size: 0.72rem;
				font-weight: 700;
				background: color-mix(in srgb, var(--bulma-scheme-main) 90%, transparent);
				border: 1px solid color-mix(in srgb, var(--bulma-border) 72%, transparent);
				color: var(--bulma-text-strong);
			}
			.report-card .section-toggle {
				border: none;
				background: transparent;
				color: var(--bulma-text-strong);
				cursor: pointer;
				width: 2rem;
				height: 2rem;
				border-radius: 999px;
				display: inline-flex;
				align-items: center;
				justify-content: center;
				transition: background-color 0.2s ease, color 0.2s ease;
			}
			.report-card .section-toggle:hover {
				background: color-mix(in srgb, var(--brand-blue-light) 18%, transparent);
				color: var(--brand-teal);
			}
			.report-card .section-toggle i {
				transition: transform 0.2s ease;
			}
			.report-card.section-collapsed .section-toggle i {
				transform: rotate(-90deg);
			}
			.report-card.section-collapsed .section-body {
				display: none;
			}
			.report-card .card-content {
				padding: 0;
			}
			.table {
				width: 100%;
			}
			.table th {
				border-bottom: 2px solid var(--brand-teal);
				font-size: 0.78rem;
				text-transform: uppercase;
				letter-spacing: 0.05em;
				color: var(--bulma-text-strong);
			}
			.table thead tr {
				background: linear-gradient(
					90deg,
					color-mix(in srgb, var(--brand-blue) 14%, transparent),
					color-mix(in srgb, var(--brand-green) 10%, transparent)
				);
			}
			.table td,
			.table th {
				vertical-align: middle;
				padding: 0.9rem 1rem;
			}
			.table tr:hover {
				background-color: color-mix(in srgb, var(--brand-blue-light) 10%, var(--bulma-scheme-main));
			}
			.pkg-name {
				font-family: "Courier New", Courier, monospace;
				font-weight: 700;
				color: var(--bulma-text-strong);
				word-break: break-word;
			}
			.empty-state {
				text-align: center;
				padding: 2rem 1.5rem;
			}
			.footer {
				padding: 1.5rem;
				margin-top: auto;
			}
			.timestamp {
				font-size: 0.85rem;
			}
			.workspace-back-link {
				margin-top: 0.85rem;
			}
			.target-name {
				font-size: 1.5rem;
				margin-bottom: 1rem;
			}
			.pkg-link {
				text-decoration: underline;
				color: var(--brand-teal);
			}
			.pkg-link:hover {
				color: var(--brand-teal-dark);
			}
			@media screen and (max-width: 768px) {
				.summary-visual-header {
					flex-direction: column;
					align-items: flex-start;
				}
				.table thead {
					display: none;
				}
				.table,
				.table tbody,
				.table tr,
				.table td {
					display: block;
					width: 100%;
				}
				.table tr {
					border-bottom: 1px solid var(--bulma-border);
					padding: 0.5rem 0;
				}
				.table td {
					padding-top: 0.55rem;
					padding-bottom: 0.55rem;
				}
				.table td::before {
					content: attr(data-label);
					display: block;
					font-size: 0.75rem;
					font-weight: 700;
					text-transform: uppercase;
					letter-spacing: 0.04em;
					color: var(--bulma-text-strong);
					margin-bottom: 0.2rem;
				}
			}
			@media (prefers-color-scheme: dark) {
				html:not([data-theme="light"]) {
					--report-shadow: 0 14px 34px color-mix(in srgb, #000 36%, transparent);
				}
				html:not([data-theme="light"]) .hero-gradient .title,
				html:not([data-theme="light"]) .hero-gradient .subtitle,
				html:not([data-theme="light"]) .hero-gradient .timestamp {
					text-shadow: 0 1px 2px rgba(0, 0, 0, 0.46);
				}
			}
		</style>
		<script>
			document.addEventListener("DOMContentLoaded", function() {
				document.querySelectorAll(".section-toggle").forEach(function(toggleButton) {
					toggleButton.addEventListener("click", function() {
						var cardId = this.getAttribute("data-card");
						if (!cardId) {
							return;
						}

						var card = document.getElementById(cardId);
						if (!card) {
							return;
						}

						var collapsed = card.classList.toggle("section-collapsed");
						this.setAttribute("aria-expanded", collapsed ? "false" : "true");
						this.setAttribute("title", collapsed ? "Expand section" : "Collapse section");
					});
				});
			});
		</script>
	</head>
	<body>
		<section class="hero hero-gradient is-medium">
			<div class="hero-body">
				<div class="container">
					<h1 class="title is-1 icon-text">
						<span class="icon is-large">
							<i class="fas fa-scale-balanced"></i>
						</span>
						<span>License Report</span>
					</h1>
					<h2 class="subtitle is-4 target-name">
						<span>{{ report.component_name }}</span>
					</h2>
					<div class="workspace-back-link">
						<a href="{{ report.workspace_report_link }}" class="button is-medium is-link is-light">
							<span class="icon"><i class="fas fa-arrow-left"></i></span>
							<span>Back to Workspace Report</span>
						</a>
					</div>
				</div>
			</div>
		</section>

		<section class="section">
			<div class="container">
				{% set severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN'] %}
				{% set category_order = ['restricted', 'reciprocal', 'notice', 'unknown'] %}
				{% set project_findings = report.severity_counts.values() | sum %}

				<div class="summary-card level">
					<div class="level-item has-text-centered">
						<div>
							<p class="title">{{ report.sections_scanned }}</p>
							<p class="heading">License Targets</p>
						</div>
					</div>
					<div class="level-item has-text-centered">
						<div>
							<p class="title">{{ report.total_findings }}</p>
							<p class="heading">Total Licenses</p>
						</div>
					</div>
				</div>

				<div class="summary-card summary-visual-card mb-5">
					<div class="summary-visual-header">
						<div>
							<p class="summary-visual-title">Severity Distribution</p>
							<p class="summary-visual-note">Distribution of licenses by severity level.</p>
						</div>
						<p class="summary-label mb-0">{{ project_findings }} total findings</p>
					</div>
					<div class="severity-bar mb-3">
						{% for severity in severity_order %}
						{% set count = report.severity_counts.get(severity, 0) %}
						{% if count > 0 and project_findings > 0 %}
						<div class="severity-segment tone-{{ severity.lower() }}" style="flex: {{ count }} 0 0;"></div>
						{% endif %}
						{% endfor %}
					</div>
					<div class="legend-row">
						{% for severity in severity_order %}
						{% set count = report.severity_counts.get(severity, 0) %}
						{% if count > 0 %}
						<span class="legend-chip"><span class="legend-swatch tone-{{ severity.lower() }}"></span>{{ severity }} {{ count }}</span>
						{% endif %}
						{% endfor %}
					</div>
				</div>

				<div class="summary-card summary-visual-card mb-5">
					<div class="summary-visual-header">
						<div>
							<p class="summary-visual-title">Category Distribution</p>
							<p class="summary-visual-note">Distribution of licenses by category.</p>
						</div>
						<p class="summary-label mb-0">{{ project_findings }} total findings</p>
					</div>
					<div class="severity-bar mb-3">
						{% for category in category_order %}
						{% set count = report.category_counts.get(category, 0) %}
						{% if count > 0 and project_findings > 0 %}
						<div class="severity-segment tone-{{ category }}" style="flex: {{ count }} 0 0;"></div>
						{% endif %}
						{% endfor %}
					</div>
					<div class="legend-row">
						{% for category in category_order %}
						{% set count = report.category_counts.get(category, 0) %}
						{% if count > 0 %}
						<span class="legend-chip"><span class="legend-swatch tone-{{ category }}"></span>{{ category | capitalize }} {{ count }}</span>
						{% endif %}
						{% endfor %}
					</div>
				</div>

				{% if report.results %}
					{% for result in report.results %}
						<div class="report-card card section-collapsed mb-5" id="result-{{ loop.index }}">
							<div class="card-header">
								<div class="card-header-main">
									<div>
										<p class="title is-4 mb-2">{{ result.target }}</p>
										<p class="subtitle is-6 mb-1">{{ result.type }}</p>
										<p class="subtitle is-6 mb-0">Sorted by severity (highest first)</p>
									</div>
									<div class="section-controls">
										<span class="tag is-medium{% if result.worst_severity == 'LOW' %} is-success{% elif result.worst_severity == 'MEDIUM' %} is-warning{% elif result.worst_severity == 'HIGH' %} is-danger{% elif result.worst_severity == 'CRITICAL' %} severity-critical{% elif result.worst_severity == 'UNKNOWN' %} is-success{% else %} severity-unknown{% endif %}">
											{{ result.worst_severity }}
										</span>
										<span class="count-cluster">
											<span class="count-pill{% if result.licenses | length == 0 %} is-muted{% endif %}">{{ result.licenses | length }}</span>
										</span>
										<button
											 class="section-toggle"
											 type="button"
											 data-card="result-{{ loop.index }}"
											 aria-expanded="false"
											 title="Expand section"
										>
											<span class="icon"><i class="fas fa-chevron-down"></i></span>
										</button>
									</div>
								</div>
							</div>

							<div class="card-content section-body">
								{% if result.licenses %}
									<div style="overflow-x: auto;">
										<table class="table is-fullwidth is-striped mb-0">
											<thead>
												<tr>
													<th>Package</th>
													<th>License</th>
													<th>Severity</th>
													<th>Category</th>
													<th>Confidence</th>
												</tr>
											</thead>
											<tbody>
												{% for finding in result.licenses %}
													<tr>
														<td data-label="Package" class="pkg-name">
															{% if finding.link %}
																<a href="{{ finding.link }}" target="_blank" rel="noopener noreferrer" class="pkg-link">{{ finding.pkg_name }}</a>
															{% else %}
																{{ finding.pkg_name }}
															{% endif %}
														</td>
														<td data-label="License">{{ finding.name }}</td>
														<td data-label="Severity">
															<span class="tag is-medium {{ 'is-success' if finding.severity == 'LOW' else 'is-warning' if finding.severity == 'MEDIUM' else 'is-danger' if finding.severity == 'HIGH' else 'severity-critical' if finding.severity == 'CRITICAL' else 'severity-unknown' }}">{{ finding.severity }}</span>
														</td>
														<td data-label="Category">
															<span class="legend-chip"><span class="legend-swatch tone-{{ finding.category }}"></span>{{ finding.category | capitalize }}</span>
														</td>
														<td data-label="Confidence">
															{% if finding.confidence is not none %}
																{% set confidence_level = 'high' if finding.confidence >= 0.90 else 'low' if finding.confidence < 0.50 else 'medium' %}
																<span class="legend-chip"><span class="legend-swatch confidence-dot-{{ confidence_level }}"></span>{{ confidence_level | capitalize }}</span>
															{% else %}
																-
															{% endif %}
														</td>
													</tr>
												{% endfor %}
											</tbody>
										</table>
									</div>
								{% else %}
									<div class="empty-state">
										<span class="icon is-large has-text-success">
											<i class="fas fa-check-circle fa-3x"></i>
										</span>
										<p class="title is-5 mt-3">No findings in this target</p>
									</div>
								{% endif %}
							</div>
						</div>
					{% endfor %}
				{% else %}
					<div class="report-card card">
						<div class="card-content has-text-centered">
							<div class="empty-state">
								<span class="icon is-large has-text-success">
									<i class="fas fa-check-circle fa-3x"></i>
								</span>
								<p class="title is-4 mt-4 mb-2">No license targets discovered</p>
								<p class="subtitle is-6 mb-0">No license scan results available for this project.</p>
							</div>
						</div>
					</div>
				{% endif %}
			</div>
		</section>

		<footer class="footer">
			<div class="container">
				<div class="level has-text-grey is-mobile">
					<div class="level-left is-size-7">
						<span class="level-item">
							Source: {{ report.component_name }}
						</span>
						<span class="level-item">
							{{ report.generated_at }}
						</span>
					</div>
					<div class="level-right is-size-6">
						<span class="level-item icon-text">
							<figure class="image is-32x32">
								<img src="data:image/png;base64,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" alt="Aurelius Enterprise" class="brand-logo">
							</figure>
							<span class="brand-name"><strong>Aurelius Enterprise</strong></span>
						</span>
					</div>
				</div>
			</div>
		</footer>
	</body>
</html>
