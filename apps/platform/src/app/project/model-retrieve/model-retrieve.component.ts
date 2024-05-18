import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';
import { defaultSimpleSearchInputContext, SimpleSearchInputContext } from '@models4insight/components';
import { BranchSummary, ModelCommitContentTypeEnum, ModelProvenance, PermissionLevel, Project } from '@models4insight/repository';
import { RetrieveModelService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import { MODEL_RETRIEVE_BATCH_SIZE } from './model-retrieve.resolver';
import { ModelRetrieveService } from './model-retrieve.service';
import { ProvenanceTableComponent } from './provenance-table/provenance-table.component';

const searchInputContext: SimpleSearchInputContext = {
  ...defaultSimpleSearchInputContext,
  placeholder: 'User, branch, comment...'
};

@Component({
  selector: 'models4insight-model-retrieve',
  templateUrl: './model-retrieve.component.html',
  styleUrls: ['./model-retrieve.component.scss']
})
export class ModelRetrieveComponent implements OnInit, OnDestroy {
  readonly faSpinner = faSpinner;
  readonly searchInputContext = searchInputContext;

  branch$: Observable<string>;
  branches$: Observable<BranchSummary[]>;
  currentPageIndex$: Observable<number>;
  from$: Observable<number>;
  modelCount$: Observable<number>;
  models$: Observable<ModelProvenance[]>;
  latestOnly$: Observable<boolean>;
  project$: Observable<Project>;
  search$: Observable<string>;
  until$: Observable<number>;

  itemsPerPage = MODEL_RETRIEVE_BATCH_SIZE;
  PermissionLevel = PermissionLevel;

  constructor(
    private readonly modelRetrieveService: ModelRetrieveService,
    private readonly projectService: ProjectService,
    private readonly retrieveModelService: RetrieveModelService,
    private readonly route: ActivatedRoute,
    private readonly router: Router
  ) {}

  ngOnInit() {
    this.project$ = this.projectService.selectCurrentProject();
    this.modelCount$ = this.modelRetrieveService.select('modelCount');
    this.models$ = this.modelRetrieveService.select('models');
    this.branches$ = this.modelRetrieveService.select('branches');
    this.latestOnly$ = this.modelRetrieveService.select([
      'filter',
      'latestOnly'
    ]);
    this.from$ = this.modelRetrieveService.select(['filter', 'from'], {
      includeFalsy: true
    });
    this.until$ = this.modelRetrieveService.select(['filter', 'until'], {
      includeFalsy: true
    });
    this.branch$ = this.modelRetrieveService.select(['filter', 'branch'], {
      includeFalsy: true
    });
    this.search$ = this.modelRetrieveService.select(['filter', 'search'], {
      includeFalsy: true
    });
    this.currentPageIndex$ = this.modelRetrieveService
      .select(['filter', 'pageIndex'])
      .pipe(shareReplay());
  }

  ngOnDestroy() {}

  clearBranchFilter() {
    this.router.navigate(['retrieve'], {
      relativeTo: this.route.parent.parent,
      queryParams: { branch: undefined },
      queryParamsHandling: 'merge'
    });
  }

  onToggleLatestOnly(event: Event) {
    this.router.navigate(['retrieve'], {
      relativeTo: this.route.parent.parent,
      queryParams: { latestOnly: event.srcElement['checked'] },
      queryParamsHandling: 'merge'
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

  setFromDate(timestamp: number) {
    this.router.navigate(['retrieve'], {
      relativeTo: this.route.parent.parent,
      queryParams: { from: timestamp },
      queryParamsHandling: 'merge'
    });
  }

  setUntilDate(timestamp: number) {
    const endTime =
      timestamp === null ? null : timestamp + (60 * 60 * 24 * 1000 - 1);
    this.router.navigate(['retrieve'], {
      relativeTo: this.route.parent.parent,
      queryParams: { to: endTime },
      queryParamsHandling: 'merge'
    });
  }

  setSearchQuery(search: string) {
    this.router.navigate(['retrieve'], {
      relativeTo: this.route.parent.parent,
      queryParams: { search },
      queryParamsHandling: 'merge'
    });
  }

  trackByBranchName(branch: BranchSummary) {
    return branch._id;
  }

  set currentPageIndex(pageIndex: number) {
    this.router.navigate(['retrieve'], {
      relativeTo: this.route.parent.parent,
      queryParams: { modelsPageIndex: pageIndex },
      queryParamsHandling: 'merge'
    });
  }

  @ViewChild(ProvenanceTableComponent, { static: false }) set provenanceTable(
    provenanceTable: ProvenanceTableComponent
  ) {
    if (provenanceTable) {
      provenanceTable.pageChanged
        .pipe(untilDestroyed(provenanceTable))
        .subscribe(pageIndex => (this.currentPageIndex = pageIndex));
    }
  }
}
