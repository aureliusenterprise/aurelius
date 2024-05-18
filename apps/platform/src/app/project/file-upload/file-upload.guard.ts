import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot } from '@angular/router';
import { Logger } from '@models4insight/logger';
import { ProjectPermissionService } from '@models4insight/permissions';
import { PermissionLevel } from '@models4insight/repository';

const log = new Logger('FileUploadGuard');

@Injectable()
export class FileUploadGuard implements CanActivate {
  constructor(
    private readonly projectPermissionService: ProjectPermissionService,
    private readonly router: Router
  ) {}

  async canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    const hasPermission = await this.projectPermissionService.hasPermission(
      PermissionLevel.CONTRIBUTOR
    );

    log.debug(`Can access model upload: ${hasPermission}`);

    if (!hasPermission) {
      const [parentRoute] = state.url.split('/upload');
      return this.router.createUrlTree([parentRoute]);
    }

    return hasPermission;
  }
}
