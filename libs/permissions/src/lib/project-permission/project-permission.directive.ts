import { Directive, Input, TemplateRef, ViewContainerRef } from '@angular/core';
import { ProjectPermissionLevel } from '@models4insight/repository';
import { AbstractProjectPermissionDirective } from './abstract-project-permission.directive';
import { ProjectPermissionService } from './project-permission.service';

@Directive({
  selector:
    'models4insight-project-permission, [models4insight-project-permission]',
})
export class ProjectPermissionDirective extends AbstractProjectPermissionDirective {
  constructor(
    projectPermissionService: ProjectPermissionService,
    templateRef: TemplateRef<any>,
    viewContainer: ViewContainerRef
  ) {
    super(projectPermissionService, templateRef, viewContainer);
  }

  @Input('models4insight-project-permission')
  set level(level: ProjectPermissionLevel) {
    this.level$.next(level);
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
