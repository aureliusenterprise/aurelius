import { TemplateRef, ViewContainerRef, Directive } from '@angular/core';
import { KeycloakService } from '@models4insight/authentication';
import { Observable, ReplaySubject } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { AbstractPermissionDirective } from '../abstract-permission.directive';

@Directive()
export abstract class AbstractKeycloakRolePermissionDirective extends AbstractPermissionDirective {
  protected readonly level$ = new ReplaySubject<string>();

  constructor(
    protected readonly keycloakService: KeycloakService,
    templateRef: TemplateRef<any>,
    viewContainer: ViewContainerRef
  ) {
    super(templateRef, viewContainer);
  }

  get permissionProvider(): Observable<boolean> {
    const tokenParsed = this.keycloakService.tokenParsed;
    return this.level$.pipe(
      map((level) => tokenParsed.realm_access?.roles.includes(level))
    );
  }
}
