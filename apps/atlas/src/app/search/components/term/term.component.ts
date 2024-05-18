import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { TermDetails } from '@models4insight/atlas/api';
import { IntersectionObserverService } from '@models4insight/services/intersection-observer';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { TermService } from './term.service';

@Component({
  selector: 'models4insight-term',
  templateUrl: 'term.component.html',
  styleUrls: ['term.component.scss'],
  providers: [TermService, IntersectionObserverService]
})
export class TermComponent implements OnInit, OnDestroy {
  isRetrievingTerm$: Observable<boolean>;
  term$: Observable<TermDetails>;

  @Input() guid: string;

  constructor(
    private readonly termService: TermService,
    private readonly intersectionObserver: IntersectionObserverService
  ) {}

  ngOnInit() {
    this.isRetrievingTerm$ = this.termService.select('isRetrievingTerm');
    this.term$ = this.termService.select('term');

    this.intersectionObserver.onIntersection
      .pipe(untilDestroyed(this))
      .subscribe(
        () => (this.termService.guid = this.guid)
      );
  }

  ngOnDestroy() {}
}
