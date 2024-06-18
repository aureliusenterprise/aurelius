import { Directive, Input, TemplateRef, ViewContainerRef } from '@angular/core';
import { KeycloakService } from '@models4insight/authentication';
import { AbstractKeycloakRolePermissionDirective } from './abstract-keycloak-role-permission.directive';

@Directive({
  selector:
    'models4insight-keycloak-role-permission, [models4insight-keycloak-role-permission]',
})
export class KeycloakRolePermissionDirective extends AbstractKeycloakRolePermissionDirective {
  constructor(
    keycloakService: KeycloakService,
    templateRef: TemplateRef<any>,
    viewContainer: ViewContainerRef
  ) {
    super(keycloakService, templateRef, viewContainer);
  }

  @Input('models4insight-keycloak-role-permission')
  set level(level: string) {
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
