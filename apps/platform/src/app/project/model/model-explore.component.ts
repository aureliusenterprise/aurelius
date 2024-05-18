import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { faArrowLeft, faDownload } from '@fortawesome/free-solid-svg-icons';
import { ModelCommitContentTypeEnum, PermissionLevel, Project } from '@models4insight/repository';
import { RetrieveModelService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { ShellService } from '@models4insight/shell';
import { getQueryParametersFromUrl } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map, shareReplay } from 'rxjs/operators';
import { ModelExploreService } from './model-explore.service';

@Component({
  selector: 'models4insight-modelexplore',
  templateUrl: 'model-explore.component.html',
  styleUrls: ['model-explore.component.scss']
})
export class ModelExploreComponent implements OnInit, OnDestroy {
  readonly faArrowLeft = faArrowLeft;
  readonly faDownload = faDownload;

  readonly PermissionLevel = PermissionLevel;

  branch$: Observable<string>;
  previousRoute$: Observable<string>;
  project$: Observable<Project>;
  selectedView$: Observable<string>;
  version$: Observable<number>;

  constructor(
    private readonly projectService: ProjectService,
    private readonly modelExploreService: ModelExploreService,
    private readonly retrieveModelService: RetrieveModelService,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly shellService: ShellService
  ) {}

  ngOnInit() {
    this.branch$ = this.modelExploreService
      .select('branch', {
        includeFalsy: true
      })
      .pipe(shareReplay());

    this.previousRoute$ = this.shellService.select('previousRoute');

    this.project$ = this.projectService.selectCurrentProject();
    this.selectedView$ = this.route.queryParamMap.pipe(
      map(params => params.get('view'))
    );

    this.version$ = this.modelExploreService.select('version', {
      includeFalsy: true
    });
  }

  ngOnDestroy() {}

  async goBack() {
    const previousRoute = await this.shellService.get('previousRoute', {
      includeFalsy: true
    });

    if (previousRoute) {
      const [path] = previousRoute.split('?');
      const queryParams = getQueryParametersFromUrl(previousRoute);
      this.router.navigate([path], { queryParams });
    }
  }

  async retrieveModel(
    contentType: ModelCommitContentTypeEnum = ModelCommitContentTypeEnum.ARCHIMATE
  ) {
    const [branch, version] = await Promise.all([
      this.modelExploreService.get('branch'),
      this.modelExploreService.get('version', { includeFalsy: true })
    ]);

    this.retrieveModelService.retrieveModel(branch, contentType, version);
  }

  updateViewSelection(view: string) {
    this.router.navigate(['explore'], {
      relativeTo: this.route.parent.parent,
      queryParams: {
        view
      },
      queryParamsHandling: 'merge'
    });
  }
}
