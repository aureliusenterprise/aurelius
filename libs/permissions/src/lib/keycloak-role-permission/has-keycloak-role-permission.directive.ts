import { Directive, Input, TemplateRef, ViewContainerRef } from '@angular/core';
import { KeycloakService } from '@models4insight/authentication';
import { AbstractKeycloakRolePermissionDirective } from './abstract-keycloak-role-permission.directive';

@Directive({
  selector:
    'models4insight-has-keycloak-role-permission, [models4insight-has-keycloak-role-permission]',
})
export class HasKeycloakRolePermissionDirective extends AbstractKeycloakRolePermissionDirective {
  private context = { hasPermission: false };

  constructor(
    keycloakService: KeycloakService,
    templateRef: TemplateRef<any>,
    viewContainer: ViewContainerRef
  ) {
    super(keycloakService, templateRef, viewContainer);
  }

  @Input('models4insight-has-keycloak-role-permission')
  set level(level: string) {
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
