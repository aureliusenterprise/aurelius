import { DOCUMENT } from '@angular/common';
import {
  Directive,
  EventEmitter,
  HostListener,
  Inject,
  Injectable,
  Input,
  OnDestroy
} from '@angular/core';
import { untilDestroyed } from '@models4insight/utils';
import { PageScrollService } from 'ngx-page-scroll-core';
import { Subject } from 'rxjs';
import { exhaustMap, first } from 'rxjs/operators';

// TODO: Add Angular decorator.
@Injectable()
export class DetailsNavigationItemService implements OnDestroy {
  private readonly queue = new Subject<string | HTMLElement>();
  private readonly scrollFinished = new EventEmitter<boolean>();

  constructor(
    private readonly pageScrollService: PageScrollService,
    @Inject(DOCUMENT) private readonly document: Document
  ) {
    this.init();
  }

  private init() {
    this.queue
      .pipe(
        exhaustMap(target => this.handleScrollToTarget(target)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  ngOnDestroy() {}

  scrollToTarget(target: string | HTMLElement) {
    this.queue.next(target);
  }

  private async handleScrollToTarget(target: string | HTMLElement) {
    const scrollInstance = this.pageScrollService.create({
      document: this.document,
      scrollFinishListener: this.scrollFinished,
      scrollOffset: 68,
      scrollTarget: target,
      speed: 500
    });

    let startPosition: number = null,
      uninterrupted = true;

    do {
      this.pageScrollService.start(scrollInstance);

      // Stop when the destination is reached
      if (
        scrollInstance.distanceToScroll <=
        scrollInstance.pageScrollOptions._minScrollDistance
      )
        break;

      // Prevents an infinite loop when the element is near the bottom of the page, where the scroll distance cannot reach 0.
      if (startPosition === scrollInstance.startScrollPosition) break;

      uninterrupted = await this.scrollFinished.pipe(first()).toPromise();

      startPosition = scrollInstance.startScrollPosition;
    } while (
      uninterrupted &&
      scrollInstance.distanceToScroll >
        scrollInstance.pageScrollOptions._minScrollDistance
    );
  }
}

@Directive({
  selector:
    'models4insightDetailsNavigationItem, [models4insightDetailsNavigationItem]'
})
export class DetailsNavigationItemDirective {
  @Input('models4insightDetailsNavigationItem') target: string | HTMLElement;

  constructor(
    private readonly detailsNavigationItemService: DetailsNavigationItemService
  ) {}

  @HostListener('click')
  scrollToTarget() {
    if (!this.target) return;
    this.detailsNavigationItemService.scrollToTarget(this.target);
  }
}
