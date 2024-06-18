import { TemplateRef, ViewContainerRef, Directive } from '@angular/core';
import { BranchPermissionLevel } from '@models4insight/repository';
import { combineLatest, Observable, ReplaySubject, Subject } from 'rxjs';
import { distinctUntilChanged, switchMap } from 'rxjs/operators';
import { AbstractPermissionDirective } from '../abstract-permission.directive';
import { BranchPermissionService } from './branch-permission.service';

@Directive()
export abstract class AbstractBranchPermissionDirective extends AbstractPermissionDirective {
  protected readonly level$: Subject<BranchPermissionLevel> =
    new ReplaySubject<BranchPermissionLevel>();

  protected readonly branchName$: Subject<string> = new ReplaySubject<string>();

  constructor(
    protected readonly branchPermissionService: BranchPermissionService,
    templateRef: TemplateRef<any>,
    viewContainer: ViewContainerRef
  ) {
    super(templateRef, viewContainer);
  }

  get permissionProvider(): Observable<boolean> {
    return combineLatest([this.branchName$, this.level$]).pipe(
      distinctUntilChanged(),
      switchMap(([branchName, permissionLevel]) =>
        this.branchPermissionService.checkPermission(
          branchName,
          permissionLevel
        )
      )
    );
  }
}
