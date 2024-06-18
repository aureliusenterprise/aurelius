import { Directive, Input, TemplateRef, ViewContainerRef } from '@angular/core';
import { ProjectPermissionLevel } from '@models4insight/repository';
import { AbstractProjectPermissionDirective } from './abstract-project-permission.directive';
import { ProjectPermissionService } from './project-permission.service';

@Directive({
  selector:
    'models4insight-has-project-permission, [models4insight-has-project-permission]',
})
export class HasProjectPermissionDirective extends AbstractProjectPermissionDirective {
  private context: { hasPermission: boolean } = { hasPermission: false };

  constructor(
    projectPermissionService: ProjectPermissionService,
    templateRef: TemplateRef<any>,
    viewContainer: ViewContainerRef
  ) {
    super(projectPermissionService, templateRef, viewContainer);
  }

  @Input('models4insight-has-project-permission')
  set level(level: ProjectPermissionLevel) {
    this.level$.next(level);
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
