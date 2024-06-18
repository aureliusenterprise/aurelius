import {
  Directive,
  EventEmitter,
  OnDestroy,
  OnInit,
  Output,
} from '@angular/core';
import { IntersectionObserverService } from '@models4insight/services/intersection-observer';
import { untilDestroyed } from '@models4insight/utils';

@Directive({
  selector:
    'models4insight-intersection-observer, [models4insight-intersection-observer]',
  providers: [IntersectionObserverService],
})
export class IntersectionObserverDirective implements OnInit, OnDestroy {
  /**
   * Emits an event whenever the element becomes visible, or becomes no longer so.
   */
  @Output() readonly intersectionStateChange = new EventEmitter<boolean>();

  /**
   * Emits an event whenever the element becomes visible.
   */
  @Output() readonly intersection = new EventEmitter<boolean>();

  constructor(
    private readonly intersectionObserver: IntersectionObserverService
  ) {}

  ngOnInit() {
    this.intersectionObserver.onIntersectionStateChange
      .pipe(untilDestroyed(this))
      .subscribe(this.intersectionStateChange);

    this.intersectionObserver.onIntersection
      .pipe(untilDestroyed(this))
      .subscribe(this.intersection);
  }

  ngOnDestroy() {}

  get hasIntersected(): boolean {
    return this.intersectionObserver.hasIntersected;
  }
}
