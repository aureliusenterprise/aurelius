import { Component, OnDestroy, OnInit } from '@angular/core';
import { UntypedFormGroup } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { faChartPie } from '@fortawesome/free-solid-svg-icons';
import { BranchSelect, ProjectSelect, ProvenanceSelect } from '@models4insight/components';
import { Branch, ModelProvenance, Project } from '@models4insight/repository';
import { BranchesService } from '@models4insight/services/branch';
import { ProjectService } from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { EMPTY, Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { GenerateReportService } from './generate-report.service';

@Component({
  selector: 'models4insight-project',
  templateUrl: 'generate-report.component.html',
  styleUrls: ['generate-report.component.scss']
})
export class GenerateReportComponent implements OnInit, OnDestroy {
  readonly faChartPie = faChartPie;

  readonly form: UntypedFormGroup;

  branches$: Observable<Branch[]>;
  projects$: Observable<Project[]>;
  versions$: Observable<ModelProvenance[]>;

  constructor(
    private readonly branchesService: BranchesService,
    private readonly generateReportService: GenerateReportService,
    private readonly projectService: ProjectService,
    private readonly route: ActivatedRoute,
    private readonly router: Router
  ) {
    const projectSelect = new ProjectSelect(),
      branchSelect = new BranchSelect(),
      versionSelect = new ProvenanceSelect();

    branchSelect.valueChanges.pipe(untilDestroyed(this)).subscribe(branch => {
      this.generateReportService.loadVersions(projectSelect.value, branch);
      versionSelect.reset();
    });

    this.form = new UntypedFormGroup({
      project: projectSelect,
      branch: branchSelect,
      version: versionSelect
    });
  }

  ngOnInit() {
    this.versions$ = this.generateReportService.versions;

    // Initially patch the form controls based on query param values
    this.route.queryParamMap
      .pipe(untilDestroyed(this))
      .subscribe(queryParamMap =>
        this.projectService.setCurrentProject(queryParamMap.get('project'))
      );

    this.route.queryParamMap
      .pipe(
        switchMap(queryParamMap =>
          queryParamMap.has('branch')
            ? this.branchesService.getBranchById(queryParamMap.get('branch'))
            : EMPTY
        ),
        untilDestroyed(this)
      )
      .subscribe(branch => {
        this.form.patchValue({ branch }, { emitEvent: false });
        this.generateReportService.loadVersions(
          this.form.value.project,
          branch
        );
      });

    this.route.queryParamMap
      .pipe(
        switchMap(queryParamMap =>
          queryParamMap.has('version')
            ? this.generateReportService.get([
                'versionsByTimestamp',
                queryParamMap.get('version')
              ])
            : EMPTY
        ),
        untilDestroyed(this)
      )
      .subscribe(version =>
        this.form.patchValue({ version }, { emitEvent: false })
      );
  }

  ngOnDestroy() {}

  generateReport() {
    const { project, branch, version } = this.form.value;
    if (version) {
      this.router.navigate(['report'], {
        relativeTo: this.route.parent.parent,
        queryParams: {
          project: project.id,
          branch: branch.id,
          version: version.start_date
        }
      });
    }
  }
}
