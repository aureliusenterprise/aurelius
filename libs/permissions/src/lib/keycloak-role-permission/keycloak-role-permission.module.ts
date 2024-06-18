import { NgModule } from '@angular/core';
import { RepositoryModule } from '@models4insight/repository';
import { HasKeycloakRolePermissionDirective } from './has-keycloak-role-permission.directive';
import { KeycloakRolePermissionDirective } from './keycloak-role-permission.directive';

@NgModule({
  imports: [RepositoryModule],
  declarations: [
    KeycloakRolePermissionDirective,
    HasKeycloakRolePermissionDirective,
  ],
  exports: [
    KeycloakRolePermissionDirective,
    HasKeycloakRolePermissionDirective,
  ],
})
export class KeycloakRolePermissionModule {}
