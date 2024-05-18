import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { faCopy } from '@fortawesome/free-regular-svg-icons';
import { faCheck } from '@fortawesome/free-solid-svg-icons';
import { untilDestroyed } from '@models4insight/utils';
import { Subject, timer } from 'rxjs';
import { switchMapTo, tap } from 'rxjs/operators';

const CHECK_DURATION = 1500; //ms

@Component({
  selector: 'models4insight-copy-button',
  templateUrl: 'copy-button.component.html',
  styleUrls: ['copy-button.component.scss']
})
export class CopyButtonComponent implements OnInit, OnDestroy {
  readonly faCheck = faCheck;
  readonly faCopy = faCopy;

  private readonly toggleCheck$: Subject<void> = new Subject<void>();

  showCheck = false;
  @Input() value = '';

  ngOnInit() {
    this.toggleCheck$
      .pipe(
        tap(() => (this.showCheck = true)),
        switchMapTo(timer(CHECK_DURATION)),
        tap(() => (this.showCheck = false)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  ngOnDestroy() {}

  toggleCheck() {
    this.toggleCheck$.next();
  }
}
