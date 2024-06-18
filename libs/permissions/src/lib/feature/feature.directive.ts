import { Directive, Input, TemplateRef, ViewContainerRef } from '@angular/core';
import { Observable, ReplaySubject, Subject } from 'rxjs';
import { distinctUntilChanged, switchMap } from 'rxjs/operators';
import { AbstractPermissionDirective } from '../abstract-permission.directive';
import { Feature, FeatureService } from './feature.service';

@Directive({
  selector: 'models4insight-feature, [models4insight-feature]',
})
export class FeatureDirective extends AbstractPermissionDirective {
  private subscription$: Subject<Feature> = new ReplaySubject<Feature>();

  constructor(
    private readonly featureService: FeatureService,
    templateRef: TemplateRef<any>,
    viewContainer: ViewContainerRef
  ) {
    super(templateRef, viewContainer);
  }

  @Input('models4insight-feature')
  set subscription(value: Feature) {
    this.subscription$.next(value);
  }

  get permissionProvider(): Observable<boolean> {
    return this.subscription$.pipe(
      distinctUntilChanged(),
      switchMap((subscription) =>
        this.featureService.checkPermission(subscription)
      )
    );
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
