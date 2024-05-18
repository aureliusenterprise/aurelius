import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { faAngleDoubleRight, faHashtag } from '@fortawesome/free-solid-svg-icons';
import { ClassificationDef } from '@models4insight/atlas/api';
import { IntersectionObserverService } from '@models4insight/services/intersection-observer';
import { untilDestroyed } from '@models4insight/utils';
import { combineLatest, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';
import { ClassificationService } from './classification.service';

@Component({
  selector: 'models4insight-classification',
  templateUrl: 'classification.component.html',
  styleUrls: ['classification.component.scss'],
  providers: [ClassificationService, IntersectionObserverService]
})
export class ClassificationComponent implements OnInit, OnDestroy {
  readonly faAngleDoubleRight = faAngleDoubleRight;
  readonly faHashtag = faHashtag;

  classificationType$: Observable<ClassificationDef>;
  isPropagated$: Observable<boolean>;
  isRetrievingTypeDefinition$: Observable<boolean>;
  sources$: Observable<string[]>;

  @Input() classificationName: string;

  constructor(
    private readonly classificationService: ClassificationService,
    private readonly entityDetailsService: EntityDetailsService,
    private readonly intersectionObserver: IntersectionObserverService
  ) {}

  ngOnInit() {
    this.classificationType$ = this.classificationService.select(
      'classificationType'
    );
    this.isRetrievingTypeDefinition$ = this.classificationService.select(
      'isRetrievingTypeDefinition'
    );

    this.isPropagated$ = combineLatest([
      this.classificationService.select('sources'),
      this.entityDetailsService.select('entityId')
    ]).pipe(map(([sources, entityId]) => !sources.includes(entityId)));

    this.sources$ = this.classificationService.select('sources');

    this.intersectionObserver.onIntersection
      .pipe(untilDestroyed(this))
      .subscribe(
        () =>
          (this.classificationService.classificationName = this.classificationName)
      );
  }

  ngOnDestroy() {}

  @Input()
  set sources(sources: string[]) {
    this.classificationService.sources = sources;
  }
}
