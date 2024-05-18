import { Component, EventEmitter, Input, Output } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import {
  faArrowLeft,
  faArrowRight,
  faChartPie,
  faEdit,
  faEquals,
  faGlobe,
  faTimes,
  faUpload
} from '@fortawesome/free-solid-svg-icons';
import { ContextMenuItems } from '@models4insight/components';
import { BranchPermissionService } from '@models4insight/permissions';
import { Branch, PermissionLevel, Project } from '@models4insight/repository';
import { BranchesService } from '@models4insight/services/branch';
import { ProjectService } from '@models4insight/services/project';
import { CompareModalService } from '../../../compare-modal.service';

export interface BranchesTableRowContext {
  branch: Branch;
  project: Project;
}

@Component({
  // tslint:disable-next-line: component-selector
  selector: 'models4insight-branches-table-context-menu',
  templateUrl: 'branches-table-context-menu.component.html',
  styleUrls: ['branches-table-context-menu.component.scss']
})
export class BranchesTableContextMenuComponent {
  @Output() edit: EventEmitter<Branch> = new EventEmitter<Branch>();

  branch: Branch;
  contextMenuItems: ContextMenuItems = [];

  constructor(
    private readonly branchPermissionService: BranchPermissionService,
    private readonly branchesService: BranchesService,
    private readonly compareModalService: CompareModalService,
    private readonly projectService: ProjectService,
    private readonly route: ActivatedRoute,
    private readonly router: Router
  ) {}

  @Input() set context(branch: Branch) {
    this.branch = branch;
    this.contextMenuItems = this.createContextMenuItems(branch);
  }

  private createContextMenuItems(branch: Branch): ContextMenuItems {
    return [
      [
        {
          click: () => this.edit.emit(this.branch),
          hasPermission: () =>
            this.branchPermissionService.checkPermission(
              branch.name,
              PermissionLevel.CONTRIBUTOR
            ),
          icon: faEdit,
          iconModifier: 'has-text-primary',
          title: 'Edit'
        },
        {
          click: () => this.mergeFromBranch(branch.name),
          hasPermission: () =>
            this.branchPermissionService.checkPermission(
              branch.name,
              PermissionLevel.CONTRIBUTOR
            ),
          icon: faArrowRight,
          iconModifier: 'has-text-primary',
          title: 'Move from'
        },
        {
          click: () => this.mergeToBranch(branch.name),
          hasPermission: () =>
            this.branchPermissionService.checkPermission(
              branch.name,
              PermissionLevel.CONTRIBUTOR
            ),
          icon: faArrowLeft,
          iconModifier: 'has-text-primary',
          title: 'Move to'
        }
      ],
      [
        {
          click: () => this.branchesService.deleteBranch(branch),
          hasPermission: () =>
            this.branchPermissionService.checkPermission(
              branch.name,
              PermissionLevel.OWNER
            ),
          holdTime: 3,
          icon: faTimes,
          iconModifier: 'has-text-danger',
          title: 'Delete'
        }
      ],
      [
        {
          click: () => this.exploreLatest(branch.name),
          hasPermission: () =>
            this.branchPermissionService.checkPermission(
              branch.name,
              PermissionLevel.BUSINESS_USER
            ),
          icon: faGlobe,
          iconModifier: 'has-text-success',
          title: 'Explore latest'
        },
        {
          click: () => this.compareModalService.activateModal(branch.name),
          hasPermission: () =>
            this.branchPermissionService.checkPermission(
              branch.name,
              PermissionLevel.BUSINESS_USER
            ),
          icon: faEquals,
          iconModifier: 'has-text-success',
          title: 'Compare latest'
        },
        {
          click: () => this.uploadToBranch(branch.name),
          hasPermission: () =>
            this.branchPermissionService.checkPermission(
              branch.name,
              PermissionLevel.CONTRIBUTOR
            ),
          icon: faUpload,
          iconModifier: 'has-text-success',
          title: 'Upload to'
        }
      ],
      /*
      [
        {
          click: () => this.openConsistencyMetricsInNewTab(branch.id),
          hasPermission: () =>
            this.branchPermissionService.checkPermission(
              branch.name,
              PermissionLevel.BUSINESS_USER
            ),
          icon: faChartPie,
          iconModifier: 'has-text-link',
          title: 'Analyze latest'
        }
      ]
      */
    ];
  }

  private exploreLatest(branchName: string) {
    this.router.navigate(['explore'], {
      relativeTo: this.route.parent.parent,
      queryParams: {
        branchName: branchName
      }
    });
  }

  private uploadToBranch(branchName: string) {
    this.router.navigate(['upload'], {
      relativeTo: this.route.parent.parent,
      queryParams: { toBranch: branchName }
    });
  }

  private mergeFromBranch(branchName: string) {
    this.router.navigate(['branches'], {
      relativeTo: this.route.parent.parent,
      queryParams: { fromBranch: branchName },
      queryParamsHandling: 'merge'
    });
  }

  private mergeToBranch(branchName: string) {
    this.router.navigate(['branches'], {
      relativeTo: this.route.parent.parent,
      queryParams: { toBranch: branchName },
      queryParamsHandling: 'merge'
    });
  }

  private async openConsistencyMetricsInNewTab(branchId: string) {
    const projectId = await this.projectService.get('projectId');
    window.open(
      `/consistency_metrics/home/report?project=${projectId}&branch=${branchId}`,
      '_blank'
    );
  }
}
