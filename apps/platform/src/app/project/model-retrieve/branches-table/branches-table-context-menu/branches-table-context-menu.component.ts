import { Component, Input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { faArrowLeft, faArrowRight, faChartPie, faDownload, faEquals, faFilter, faGlobe, faUpload } from '@fortawesome/free-solid-svg-icons';
import { ContextMenuItems } from '@models4insight/components';
import { BranchPermissionService, ProjectPermissionService } from '@models4insight/permissions';
import { BranchSummary, ModelCommitContentTypeEnum, PermissionLevel, Project } from '@models4insight/repository';
import { BranchesService } from '@models4insight/services/branch';
import { RetrieveModelService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { combineLatest, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { CompareModalService } from '../../../compare-modal.service';

export interface BranchesTableContextMenuContext {
  branch: BranchSummary;
  project: Project;
}

@Component({
  selector: 'models4insight-branches-table-context-menu',
  templateUrl: 'branches-table-context-menu.component.html',
  styleUrls: ['branches-table-context-menu.component.scss']
})
export class BranchesTableContextMenuComponent {
  branch: BranchSummary;
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

  @Input() set context(branch: BranchSummary) {
    this.branch = branch;
    this.contextMenuItems = this.createContextMenuItems(branch);
  }

  private createContextMenuItems(branch: BranchSummary): ContextMenuItems {
    return [
      [
        {
          click: () => this.retrieveLatest(branch._id),
          hasPermission: () =>
            this.checkPermission(branch, PermissionLevel.MODEL_USER),
          icon: faDownload,
          iconModifier: 'has-text-primary',
          title: 'Retrieve latest'
        },
        {
          click: () => this.filterByBranch(branch._id),
          icon: faFilter,
          iconModifier: 'has-text-primary',
          title: 'Filter branch'
        }
      ],
      [
        {
          click: () => this.exploreLatest(branch._id),
          hasPermission: () =>
            this.checkPermission(branch, PermissionLevel.BUSINESS_USER),
          icon: faGlobe,
          iconModifier: 'has-text-success',
          title: 'Explore latest'
        },
        {
          click: () => this.compareModalService.activateModal(branch._id),
          hasPermission: () =>
            this.checkPermission(branch, PermissionLevel.BUSINESS_USER),
          icon: faEquals,
          iconModifier: 'has-text-success',
          title: 'Compare latest'
        },
        {
          click: () => this.uploadToBranch(branch._id),
          hasPermission: () =>
            this.checkPermission(branch, PermissionLevel.CONTRIBUTOR),
          icon: faUpload,
          iconModifier: 'has-text-success',
          title: 'Upload to'
        },
        {
          click: () => this.mergeFromBranch(branch._id),
          hasPermission: () =>
            this.checkPermission(branch, PermissionLevel.CONTRIBUTOR),
          icon: faArrowRight,
          iconModifier: 'has-text-success',
          title: 'Move from'
        },
        {
          click: () => this.mergeToBranch(branch._id),
          hasPermission: () =>
            this.checkPermission(branch, PermissionLevel.CONTRIBUTOR),
          icon: faArrowLeft,
          iconModifier: 'has-text-success',
          title: 'Move to'
        }
      ],
      /*
      [
        {
          click: () => this.openConsistencyMetricsInNewTab(branch._id),
          hasPermission: () =>
            this.checkPermission(branch, PermissionLevel.BUSINESS_USER),
          icon: faChartPie,
          iconModifier: 'has-text-link',
          title: 'Analyze latest'
        }
      ]
      */
    ];
  }

  private checkPermission(
    branch: BranchSummary,
    permissionLevel: PermissionLevel
  ): Observable<boolean> {
    return combineLatest([
      this.projectPermissionService.checkPermission(permissionLevel),
      this.branchPermissionService.checkPermission(branch._id, permissionLevel)
    ]).pipe(
      map(
        ([projectPermission, branchPermission]) =>
          projectPermission && branchPermission
      )
    );
  }

  private exploreLatest(branchName: string) {
    this.router.navigate(['explore'], {
      relativeTo: this.route.parent.parent,
      queryParams: {
        branchName: branchName
      }
    });
  }

  private filterByBranch(branchName: string) {
    this.router.navigate(['retrieve'], {
      relativeTo: this.route.parent.parent,
      queryParams: { branch: branchName },
      queryParamsHandling: 'merge'
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

  private async openConsistencyMetricsInNewTab(branchName: string) {
    const [{ id: branchId }, projectId] = await Promise.all([
      this.branchesService.getBranchByName(branchName),
      this.projectService.get('projectId')
    ]);
    window.open(
      `/consistency_metrics/home/report?project=${projectId}&branch=${branchId}`,
      '_blank'
    );
  }

  private uploadToBranch(branchName: string) {
    this.router.navigate(['upload'], {
      relativeTo: this.route.parent.parent,
      queryParams: { toBranch: branchName }
    });
  }

  private retrieveLatest(
    branchName: string,
    contentType: ModelCommitContentTypeEnum = ModelCommitContentTypeEnum.ARCHIMATE
  ) {
    this.retrieveModelService.retrieveModel(branchName, contentType);
  }
}
