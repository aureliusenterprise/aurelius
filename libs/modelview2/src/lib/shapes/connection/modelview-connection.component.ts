import {
  Component,
  HostBinding,
  HostListener,
  Input,
  OnDestroy,
  OnInit,
} from '@angular/core';
import { stringToHash, untilDestroyed } from '@models4insight/utils';
import { combineLatest, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ModelExplorerService } from '../../model-explorer.service';
import { ModelViewConnection } from '../../parsers';
import { ConnectionStyleDescriptor } from '../types';
import { ModelviewConnectionService } from './modelview-connection.service';

@Component({
  selector: '[models4insight-modelview-connection]',
  templateUrl: './modelview-connection.component.svg',
  styleUrls: [],
  providers: [ModelviewConnectionService],
})
export class ModelviewConnectionComponent implements OnInit, OnDestroy {
  @HostBinding('class')
  class = 'connection';

  @HostBinding('attr.id')
  id: string;

  @HostBinding('class.is-highlighted')
  isHighlighted: boolean;

  @HostBinding('class.is-selected')
  isSelected: boolean;

  @HostBinding('attr.transform')
  transform: string;

  color$: Observable<string>;
  displayName$: Observable<string>;
  path$: Observable<string>;
  style$: Observable<ConnectionStyleDescriptor>;

  pathId: string;
  textPathRef: string;

  constructor(
    private readonly modelExplorerService: ModelExplorerService,
    private readonly modelviewConnectionService: ModelviewConnectionService
  ) {}

  ngOnInit() {
    this.color$ = this.modelviewConnectionService.color;
    this.displayName$ = this.modelviewConnectionService.displayName;
    this.path$ = this.modelviewConnectionService.select('path', {
      includeFalsy: true,
    });
    this.style$ = this.modelviewConnectionService.style;

    this.modelviewConnectionService
      .select(['viewConnection', 'id'])
      .pipe(untilDestroyed(this))
      .subscribe((id) => {
        this.id = id;
        this.pathId = `${stringToHash(id)}-path`;
        this.textPathRef = `${location?.href ?? ''}#${this.pathId}`;
      });

    this.modelviewConnectionService
      .select('transform')
      .pipe(untilDestroyed(this))
      .subscribe((transform) => (this.transform = transform));

    combineLatest([
      this.modelExplorerService.select('selectedEntity', {
        includeFalsy: true,
      }),
      this.modelviewConnectionService.select('viewConnection'),
    ])
      .pipe(
        map(
          ([selectedConcept, { id, ref }]) =>
            (ref && selectedConcept === ref) || selectedConcept === id
        ),
        untilDestroyed(this)
      )
      .subscribe((isSelected) => (this.isSelected = isSelected));

    combineLatest([
      this.modelExplorerService.select('highlightedEntity', {
        includeFalsy: true,
      }),
      this.modelviewConnectionService.select('viewConnection'),
    ])
      .pipe(
        map(
          ([highlightedConcept, { id, ref }]) =>
            (ref && highlightedConcept === ref) || highlightedConcept === id
        ),
        untilDestroyed(this)
      )
      .subscribe((isHighlighted) => (this.isHighlighted = isHighlighted));
  }

  ngOnDestroy() {}

  @HostListener('click')
  onHostElementClicked() {
    if (this.isSelected) {
      this.modelExplorerService.deleteConceptSelection();
    } else {
      this.modelviewConnectionService.selectConnection();
    }
  }

  @Input('models4insight-modelview-connection')
  set connection(connection: ModelViewConnection) {
    this.modelviewConnectionService.viewConnection = connection;
  }
}
