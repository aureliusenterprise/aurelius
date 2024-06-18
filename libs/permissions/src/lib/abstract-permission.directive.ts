import {
  OnDestroy,
  OnInit,
  TemplateRef,
  ViewContainerRef,
  Directive,
} from '@angular/core';
import { untilDestroyed } from '@models4insight/utils';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { distinctUntilChanged } from 'rxjs/operators';

@Directive()
export abstract class AbstractPermissionDirective implements OnInit, OnDestroy {
  /** Indicates the current user permission state */
  protected readonly hasPermission$: Subject<boolean> = new BehaviorSubject(
    false
  );

  /** Indicates whether or not the view has been created. Can also be false if previously created, but destroyed. */
  protected hasView = false;

  constructor(
    protected readonly templateRef: TemplateRef<any>,
    protected readonly viewContainer: ViewContainerRef
  ) {}

  ngOnInit() {
    // Whenever the permission provider emits a new value, propagate the new permission state.
    this.permissionProvider
      .pipe(untilDestroyed(this))
      .subscribe(this.hasPermission$);

    //Whenever the permissions change, trigger the update of the view.
    this.hasPermission$
      .pipe(distinctUntilChanged(), untilDestroyed(this))
      .subscribe((hasPermission) => this.handlePermissionChange(hasPermission));
  }

  ngOnDestroy() {
    this.hasPermission$.complete();
  }

  /**
   * Provides the permission state as an observable stream.
   */
  protected abstract get permissionProvider(): Observable<boolean>;

  /**
   * Updates the view based on the given permission state.
   */
  protected abstract handlePermissionChange(hasPermission: boolean): void;
}
