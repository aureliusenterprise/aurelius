import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot } from '@angular/router';
import { Logger } from '@models4insight/logger';
import { ProjectPermissionService } from '@models4insight/permissions';
import { PermissionLevel } from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';

const log = new Logger('ProjectGuard');

@Injectable()
export class ProjectGuard implements CanActivate {
  constructor(
    private readonly projectService: ProjectService,
    private readonly projectPermissionService: ProjectPermissionService,
    private readonly router: Router
  ) {}

  async canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    this.projectService.setCurrentProject(route.params.id);

    const hasPermission = await this.projectPermissionService.hasPermission(
      PermissionLevel.BUSINESS_USER
    );

    log.debug(`Can access project: ${hasPermission}`);

    if (!hasPermission) {
      return this.router.createUrlTree(['projects']);
    }

    return hasPermission;
  }
}
