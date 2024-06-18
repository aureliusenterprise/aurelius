import {
  Directive,
  EventEmitter,
  HostBinding,
  HostListener,
  Input,
  OnDestroy,
  Output,
} from '@angular/core';
import { untilDestroyed } from '@models4insight/utils';
import { TranslateService } from '@ngx-translate/core';
import { merge, Observable, Subject, timer } from 'rxjs';
import { filter, takeUntil, tap } from 'rxjs/operators';

@Directive({
  exportAs: 'models4insight-holdable',
  selector: 'models4insight-holdable, [models4insight-holdable]',
})
export class HoldableDirective implements OnDestroy {
  /**
   * The polling ratio in milliseconds
   */
  static readonly POLLING_RATIO = 100;

  /**
   * Emits true when the mouse was pressed long enough, false if released prematurely (canceled)
   */
  @Output() held: EventEmitter<boolean> = new EventEmitter();

  @HostBinding('attr.data-tooltip')
  get tooltip(): string {
    return this.translateService.instant(
      this.holdTime === 1
        ? 'holdable.tooltip.single'
        : 'holdable.tooltip.plural',
      {
        seconds: this.holdTime,
      }
    );
  }

  @HostBinding('class.tooltip')
  classTooltip = true;

  @HostBinding('class.is-tooltip-left')
  classIsTooltipLeft = true;

  private state: Subject<string> = new Subject();

  private cancel: Observable<string>;
  private done: Observable<string>;

  private _holdTime = 1;

  constructor(private translateService: TranslateService) {
    this.cancel = this.state.pipe(
      filter((v) => v === 'cancel'),
      tap((v) => {
        this.held.emit(false);
      })
    );

    this.done = this.state.pipe(
      filter((v) => v === 'done'),
      tap(() => {
        this.held.emit(true);
      })
    );
  }

  ngOnDestroy() {}

  @HostListener('mouseup', ['$event'])
  @HostListener('mouseleave', ['$event'])
  onExit() {
    this.state.next('cancel');
  }

  @HostListener('mousedown', ['$event'])
  onHold() {
    this.state.next('start');

    timer(0, HoldableDirective.POLLING_RATIO)
      .pipe(
        takeUntil(merge(this.cancel, this.done)),
        tap((v) => {
          if (v * HoldableDirective.POLLING_RATIO >= this._holdTime * 1000) {
            this.state.next('done');
          }
        }),
        untilDestroyed(this)
      )
      .subscribe();
  }

  /**
   * How long the mouse should be pressed in seconds
   */
  @Input()
  set holdTime(seconds: number | string) {
    if (typeof seconds === 'string') {
      this._holdTime = Number.parseInt(seconds);
    } else {
      this._holdTime = seconds;
    }
  }

  get holdTime() {
    return this._holdTime;
  }
}
