import { Directive, Input, TemplateRef, ViewContainerRef } from '@angular/core';
import { BranchPermissionLevel } from '@models4insight/repository';
import { AbstractBranchPermissionDirective } from './abstract-branch-permission.directive';
import { BranchPermissionService } from './branch-permission.service';

@Directive({
  selector:
    'models4insight-branch-permission, [models4insight-branch-permission]',
})
export class BranchPermissionDirective extends AbstractBranchPermissionDirective {
  constructor(
    branchPermissionService: BranchPermissionService,
    templateRef: TemplateRef<any>,
    viewContainer: ViewContainerRef
  ) {
    super(branchPermissionService, templateRef, viewContainer);
  }

  @Input('models4insight-branch-permission')
  set level(level: BranchPermissionLevel) {
    this.level$.next(level);
  }

  @Input('models4insight-branch-permissionBranch')
  set branchName(branchName: string) {
    this.branchName$.next(branchName);
  }

  /**
   * Creates or destroys the view based on the given permission state.
   */
  protected handlePermissionChange(hasPermission: boolean) {
    if (hasPermission && !this.hasView) {
      this.viewContainer.createEmbeddedView(this.templateRef);
      this.hasView = true;
    } else if (!hasPermission && this.hasView) {
      this.viewContainer.clear();
      this.hasView = false;
    }
  }
}
