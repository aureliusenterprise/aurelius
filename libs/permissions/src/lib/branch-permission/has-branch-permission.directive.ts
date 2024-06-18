import { Directive, Input, TemplateRef, ViewContainerRef } from '@angular/core';
import { Project, BranchPermissionLevel } from '@models4insight/repository';
import { AbstractBranchPermissionDirective } from './abstract-branch-permission.directive';
import { BranchPermissionService } from './branch-permission.service';

@Directive({
  selector:
    'models4insight-has-branch-permission, [models4insight-has-branch-permission]',
})
export class HasBranchPermissionDirective extends AbstractBranchPermissionDirective {
  private context: { hasPermission: boolean } = { hasPermission: false };

  constructor(
    branchPermissionService: BranchPermissionService,
    templateRef: TemplateRef<any>,
    viewContainer: ViewContainerRef
  ) {
    super(branchPermissionService, templateRef, viewContainer);
  }

  @Input('models4insight-has-branch-permission')
  set level(level: BranchPermissionLevel) {
    this.level$.next(level);
  }

  @Input('models4insight-has-branch-permissionBranch')
  set branchName(branchName: string) {
    this.branchName$.next(branchName);
  }

  /**
   * Updates the context of the view based on the given permission state.
   */
  protected handlePermissionChange(hasPermission: boolean) {
    if (!this.hasView) {
      this.viewContainer.createEmbeddedView(this.templateRef, this.context);
      this.hasView = true;
    }
    this.context.hasPermission = hasPermission;
  }
}
