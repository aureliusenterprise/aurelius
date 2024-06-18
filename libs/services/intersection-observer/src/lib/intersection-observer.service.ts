import { ElementRef, Injectable, OnDestroy } from '@angular/core';
import { findLast, untilDestroyed } from '@models4insight/utils';
import { identity } from 'lodash';
import { BehaviorSubject, Subject } from 'rxjs';
import { concatMap, distinctUntilChanged, filter } from 'rxjs/operators';

// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
@Injectable({
  providedIn: 'root',
})
export class IntersectionObserverProvider
  extends IntersectionObserver
  implements OnDestroy
{
  private readonly elementsIntersectionStateChanged$ = new Subject<
    IntersectionObserverEntry[]
  >();

  constructor() {
    super((elements) => this.elementsIntersectionStateChanged$.next(elements));
  }

  ngOnDestroy() {
    this.disconnect();
  }

  get elementsIntersectionStateChanged() {
    return this.elementsIntersectionStateChanged$.asObservable();
  }
}

// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
@Injectable()
export class IntersectionObserverService implements OnDestroy {
  private readonly isIntersecting$ = new BehaviorSubject(this.hasIntersected);

  private _hasIntersected = false;

  constructor(
    private readonly elementRef: ElementRef,
    private readonly intersectionObserver: IntersectionObserverProvider
  ) {
    this.init();
  }

  private init() {
    this.intersectionObserver.elementsIntersectionStateChanged
      .pipe(
        concatMap((events) => this.handleIntersectionStateChange(events)),
        untilDestroyed(this)
      )
      .subscribe();

    this.intersectionObserver.observe(this.elementRef.nativeElement);
  }

  ngOnDestroy() {
    this.intersectionObserver.unobserve(this.elementRef.nativeElement);
  }

  get hasIntersected() {
    return this._hasIntersected;
  }

  get onIntersection() {
    return this.isIntersecting$.pipe(filter(identity));
  }

  get onIntersectionStateChange() {
    return this.isIntersecting$.pipe(distinctUntilChanged());
  }

  private async handleIntersectionStateChange(
    events: IntersectionObserverEntry[]
  ) {
    // There can be multiple events for the same element. Find the most recent event for the element.
    const hostElementIntersectionChange = findLast(
      events,
      (event) => event.target === this.elementRef.nativeElement
    );

    if (!hostElementIntersectionChange) return;

    if (hostElementIntersectionChange.isIntersecting) {
      this._hasIntersected = true;
    }

    this.isIntersecting$.next(hostElementIntersectionChange.isIntersecting);
  }
}
