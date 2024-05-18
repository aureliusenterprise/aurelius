import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { UntypedFormBuilder, UntypedFormGroup } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { faQuestionCircle } from '@fortawesome/free-solid-svg-icons';
import { BranchSelect, CalendarHeatmapComponent, defaultBranchSelectContext, defaultDescriptionInputContext, DescriptionInput, DescriptionInputContext, FileDropzone, SelectContext } from '@models4insight/components';
import { Branch, ModelCommitContentTypeEnum, ModelProvenance, ModelProvenanceSummary, PermissionLevel, Project } from '@models4insight/repository';
import { CommitModelService, RetrieveModelService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { RECENT_ACTIVITY_BATCH_SIZE } from './project-home.resolver';
import { ProjectHomeService } from './project-home.service';

const branchSelectContext: SelectContext = {
  ...defaultBranchSelectContext,
  inputClasses: ['is-large']
};

const descriptionContext: DescriptionInputContext = {
  ...defaultDescriptionInputContext,
  label: 'Comment',

  placeholder: 'Comment',
  requiredErrorMessage: 'Please provide a comment for your upload'
};

@Component({
  selector: 'models4insight-project-home',
  templateUrl: 'project-home.component.html',
  styleUrls: ['project-home.component.scss']
})
export class ProjectHomeComponent implements OnInit, OnDestroy {
  readonly branchSelectContext = branchSelectContext;
  readonly descriptionContext = descriptionContext;
  readonly PermissionLevel = PermissionLevel;

  readonly faQuestionCircle = faQuestionCircle;

  branches$: Observable<Branch[]>;
  groupNames$: Observable<string[]>;
  heatmapData$: Observable<CalendarHeatmapComponent['data']>;
  heatmapDomain$: Observable<CalendarHeatmapComponent['domain']>;
  heatmapLegend$: Observable<CalendarHeatmapComponent['legend']>;
  heatmapRange$: Observable<CalendarHeatmapComponent['range']>;
  heatmapStart$: Observable<CalendarHeatmapComponent['start']>;
  heatmapSubdomain$: Observable<CalendarHeatmapComponent['subdomain']>;
  isUpdatingBranch$: Observable<boolean>;
  project$: Observable<Project>;
  provenanceSummary$: Observable<ModelProvenanceSummary[]>;
  latest$: Observable<ModelProvenance[]>;
  usernames$: Observable<string[]>;

  gettingStartedForm: UntypedFormGroup;
  isSubmitted = false;
  itemsPerPage = RECENT_ACTIVITY_BATCH_SIZE;

  constructor(
    private readonly commitModelService: CommitModelService,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly formBuilder: UntypedFormBuilder,
    private readonly projectService: ProjectService,
    private readonly projectHomeService: ProjectHomeService,
    private readonly retrieveModelService: RetrieveModelService
  ) {}

  ngOnInit() {
    this.heatmapData$ = this.projectHomeService.select([
      'heatmapContext',
      'data'
    ]);
    this.heatmapDomain$ = this.projectHomeService.select([
      'heatmapContext',
      'domain'
    ]);
    this.heatmapLegend$ = this.projectHomeService.select([
      'heatmapContext',
      'legend'
    ]);
    this.heatmapRange$ = this.projectHomeService.select([
      'heatmapContext',
      'range'
    ]);
    this.heatmapStart$ = this.projectHomeService.select([
      'heatmapContext',
      'start'
    ]);
    this.heatmapSubdomain$ = this.projectHomeService.select([
      'heatmapContext',
      'subdomain'
    ]);
    this.project$ = this.projectService.selectCurrentProject();
    this.latest$ = this.projectHomeService.select('latestActivity');

    this.gettingStartedForm = this.formBuilder.group({
      file: new FileDropzone(['archimate']),
      branch: new BranchSelect(),
      comment: new DescriptionInput()
    });
  }

  ngOnDestroy() {}

  onDone() {
    this.isSubmitted = true;
    if (this.gettingStartedForm.valid) {
      this.commitModel();
    }
  }

  exploreModel(branchName: string, version?: number) {
    this.router.navigate(['explore'], {
      relativeTo: this.route.parent.parent,
      queryParams: {
        branchName: branchName,
        version: version
      }
    });
  }

  mergeFromBranch(branchName: string) {
    this.router.navigate(['branches'], {
      relativeTo: this.route.parent.parent,
      queryParams: { fromBranch: branchName }
    });
  }

  mergeToBranch(branchName: string) {
    this.router.navigate(['branches'], {
      relativeTo: this.route.parent.parent,
      queryParams: { toBranch: branchName }
    });
  }

  retrieveModel(
    provenance: ModelProvenance,
    contentType: ModelCommitContentTypeEnum = ModelCommitContentTypeEnum.ARCHIMATE
  ) {
    this.retrieveModelService.retrieveModel(
      provenance.branch,
      contentType,
      provenance.start_date
    );
  }

  commitModel() {
    const { branch, comment, file } = this.gettingStartedForm.value;
    this.commitModelService.commitModel(branch.name, comment, file);
  }

  @ViewChild(CalendarHeatmapComponent, { static: false }) set calendarHeatmap(
    calendarHeatmap: CalendarHeatmapComponent
  ) {
    if (calendarHeatmap) {
      calendarHeatmap.clicked
        .pipe(untilDestroyed(calendarHeatmap))
        .subscribe(date => {
          this.router.navigate(['retrieve'], {
            relativeTo: this.route.parent.parent,
            queryParams: {
              from: date.getTime(),
              to: date.getTime() + (60 * 60 * 24 * 1000 - 1)
            }
          });
        });
    }
  }
}
