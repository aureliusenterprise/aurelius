import { Component, Input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { faArrowLeft, faArrowRight, faChartPie, faDownload, faEquals, faGlobe } from '@fortawesome/free-solid-svg-icons';
import { ContextMenuItems } from '@models4insight/components';
import { BranchPermissionService, ProjectPermissionService } from '@models4insight/permissions';
import { ModelCommitContentTypeEnum, ModelProvenance, PermissionLevel, Project } from '@models4insight/repository';
import { BranchesService } from '@models4insight/services/branch';
import { RetrieveModelService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { combineLatest, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { CompareModalService } from '../../../compare-modal.service';

export interface RecentActivityContextMenuContext {
  project: Project;
  provenance: ModelProvenance;
}

@Component({
  // tslint:disable-next-line: component-selector
  selector: 'models4insight-recent-activity-context-menu',
  templateUrl: 'recent-activity-context-menu.component.html',
  styleUrls: ['recent-activity-context-menu.component.scss']
})
export class RecentActivityContextMenuComponent {
  provenance: ModelProvenance;
  contextMenuItems: ContextMenuItems = [];

  constructor(
    private readonly branchesService: BranchesService,
    private readonly branchPermissionService: BranchPermissionService,
    private readonly compareModalService: CompareModalService,
    private readonly projectService: ProjectService,
    private readonly projectPermissionService: ProjectPermissionService,
    private readonly retrieveModelService: RetrieveModelService,
    private readonly route: ActivatedRoute,
    private readonly router: Router
  ) {}

  @Input() set context(provenance: ModelProvenance) {
    this.provenance = provenance;
    this.contextMenuItems = this.createContextMenuItems(provenance);
  }

  private createContextMenuItems(
    provenance: ModelProvenance
  ): ContextMenuItems {
    return [
      [
        {
          click: () =>
            this.retrieveModel(provenance.branch, provenance.start_date),
          hasPermission: () =>
            this.checkPermission(provenance, PermissionLevel.MODEL_USER),
          icon: faDownload,
          iconModifier: 'has-text-primary',
          title: 'Retrieve'
        }
      ],
      [
        {
          click: () =>
            this.exploreModel(provenance.branch, provenance.start_date),
          hasPermission: () =>
            this.checkPermission(provenance, PermissionLevel.BUSINESS_USER),
          icon: faGlobe,
          iconModifier: 'has-text-success',
          title: 'Explore'
        },
        {
          click: () =>
            this.compareModalService.activateModal(
              provenance.branch,
              provenance.start_date
            ),
          hasPermission: () =>
            this.checkPermission(provenance, PermissionLevel.BUSINESS_USER),
          icon: faEquals,
          iconModifier: 'has-text-success',
          title: 'Compare'
        },
        {
          click: () => this.mergeFromBranch(provenance.branch),
          hasPermission: () =>
            this.checkPermission(provenance, PermissionLevel.CONTRIBUTOR),
          icon: faArrowRight,
          iconModifier: 'has-text-success',
          title: 'Move from'
        },
        {
          click: () => this.mergeToBranch(provenance.branch),
          hasPermission: () =>
            this.checkPermission(provenance, PermissionLevel.CONTRIBUTOR),
          icon: faArrowLeft,
          iconModifier: 'has-text-success',
          title: 'Move to'
        }
      ],
      [
        {
          click: () =>
            this.openConsistencyMetricsInNewTab(
              provenance.branch,
              provenance.start_date
            ),
          hasPermission: () =>
            this.checkPermission(provenance, PermissionLevel.BUSINESS_USER),
          icon: faChartPie,
          iconModifier: 'has-text-link',
          title: 'Analyze'
        }
      ]
    ];
  }

  private checkPermission(
    provenance: ModelProvenance,
    permissionLevel: PermissionLevel
  ): Observable<boolean> {
    return combineLatest([
      this.projectPermissionService.checkPermission(permissionLevel),
      this.branchPermissionService.checkPermission(
        provenance.branch,
        permissionLevel
      )
    ]).pipe(
      map(
        ([projectPermission, branchPermission]) =>
          projectPermission && branchPermission
      )
    );
  }

  private exploreModel(branchName: string, version?: number) {
    this.router.navigate(['explore'], {
      relativeTo: this.route.parent.parent,
      queryParams: {
        branchName: branchName,
        version: version
      }
    });
  }

  private mergeFromBranch(branchName: string) {
    this.router.navigate(['branches'], {
      relativeTo: this.route.parent.parent,
      queryParams: { fromBranch: branchName }
    });
  }

  private mergeToBranch(branchName: string) {
    this.router.navigate(['branches'], {
      relativeTo: this.route.parent.parent,
      queryParams: { toBranch: branchName }
    });
  }

  private async openConsistencyMetricsInNewTab(
    branchName: string,
    version?: number
  ) {
    const [{ id: branchId }, projectId] = await Promise.all([
      this.branchesService.getBranchByName(branchName),
      this.projectService.get('projectId')
    ]);
    window.open(
      `/consistency_metrics/home/report?project=${projectId}&branch=${branchId}&version=${version}`,
      '_blank'
    );
  }

  private retrieveModel(
    branchName: string,
    version?: number,
    contentType: ModelCommitContentTypeEnum = ModelCommitContentTypeEnum.ARCHIMATE
  ) {
    this.retrieveModelService.retrieveModel(branchName, contentType, version);
  }
}
