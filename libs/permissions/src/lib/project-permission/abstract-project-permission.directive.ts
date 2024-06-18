import { AbstractPermissionDirective } from '../abstract-permission.directive';
import { Observable, combineLatest, Subject, ReplaySubject } from 'rxjs';
import { distinctUntilChanged, switchMap } from 'rxjs/operators';
import { Project, ProjectPermissionLevel } from '@models4insight/repository';
import { ProjectPermissionService } from './project-permission.service';
import { TemplateRef, ViewContainerRef, Directive } from '@angular/core';

@Directive()
export abstract class AbstractProjectPermissionDirective extends AbstractPermissionDirective {
  protected readonly level$: Subject<ProjectPermissionLevel> =
    new ReplaySubject<ProjectPermissionLevel>();

  constructor(
    protected readonly projectPermissionService: ProjectPermissionService,
    templateRef: TemplateRef<any>,
    viewContainer: ViewContainerRef
  ) {
    super(templateRef, viewContainer);
  }

  get permissionProvider(): Observable<boolean> {
    return this.level$.pipe(
      switchMap((permissionLevel) =>
        this.projectPermissionService.checkPermission(permissionLevel)
      )
    );
  }
}
