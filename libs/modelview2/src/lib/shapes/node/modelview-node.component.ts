import {
  Component,
  HostBinding,
  HostListener,
  Input,
  OnDestroy,
  OnInit,
} from '@angular/core';
import { untilDestroyed } from '@models4insight/utils';
import { combineLatest, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ModelExplorerService } from '../../model-explorer.service';
import { ModelViewNode } from '../../parsers';
import { classes } from '../classes';
import { NodeShapeDefinition } from '../types';
import { ModelviewNodeService } from './modelview-node.service';

@Component({
  selector: '[models4insight-modelview-node]',
  templateUrl: './modelview-node.component.svg',
  styleUrls: ['modelview-node.component.scss'],
  providers: [ModelviewNodeService],
})
export class ModelviewNodeComponent implements OnInit, OnDestroy {
  @HostBinding('class')
  class = 'node';

  @HostBinding('attr.height')
  height: number;

  @HostBinding('attr.id')
  id: string;

  @HostBinding('class.is-highlighted')
  isHighlighted: boolean;

  @HostBinding('class.is-selected')
  isSelected: boolean;

  @HostBinding('attr.width')
  width: number;

  @HostBinding('attr.transform')
  transform: string;

  class$: Observable<string>;
  color$: Observable<string>;
  displayName$: Observable<string>;
  shapeDefinition$: Observable<NodeShapeDefinition>;
  type$: Observable<string>;

  constructor(
    private readonly modelExplorerService: ModelExplorerService,
    private readonly modelviewNodeService: ModelviewNodeService
  ) {}

  ngOnInit() {
    this.color$ = this.modelviewNodeService.color;
    this.displayName$ = this.modelviewNodeService.displayName;
    this.shapeDefinition$ = this.modelviewNodeService.shape;
    this.type$ = this.modelviewNodeService.type;

    this.modelviewNodeService
      .select(['viewNode', 'height'])
      .pipe(untilDestroyed(this))
      .subscribe((height) => (this.height = height));

    this.modelviewNodeService
      .select(['viewNode', 'id'])
      .pipe(untilDestroyed(this))
      .subscribe((id) => (this.id = id));

    this.modelviewNodeService
      .select(['viewNode', 'width'])
      .pipe(untilDestroyed(this))
      .subscribe((width) => (this.width = width));

    this.modelviewNodeService.position
      .pipe(untilDestroyed(this))
      .subscribe((position) => (this.transform = position));

    this.class$ = this.modelviewNodeService.type.pipe(
      map((type) => classes[type])
    );

    combineLatest([
      this.modelExplorerService.select('selectedEntity', {
        includeFalsy: true,
      }),
      this.modelviewNodeService.select('viewNode'),
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
      this.modelviewNodeService.select('viewNode'),
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
      this.modelviewNodeService.selectNode();
    }
  }

  @Input('models4insight-modelview-node')
  set node(node: ModelViewNode) {
    this.modelviewNodeService.viewNode = node;
  }
}
