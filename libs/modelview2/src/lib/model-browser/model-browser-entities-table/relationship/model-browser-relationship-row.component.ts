import { Component, Input, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { ModelEntity, ModelRelation } from '../../../parsers';
import { ModelBrowserRelationshipRowService } from './model-browser-relationship-row.service';

@Component({
  selector: 'models4insight-model-browser-relationship-row',
  templateUrl: 'model-browser-relationship-row.component.html',
  styleUrls: ['model-browser-relationship-row.component.scss'],
  providers: [ModelBrowserRelationshipRowService],
})
export class ModelBrowserRelationshipRowComponent implements OnInit {
  displayName$: Observable<string>;
  source$: Observable<ModelEntity>;
  target$: Observable<ModelEntity>;
  type$: Observable<string>;

  constructor(
    private readonly modelBrowserRelationshipRowService: ModelBrowserRelationshipRowService
  ) {}

  ngOnInit() {
    this.displayName$ = this.modelBrowserRelationshipRowService.displayName;
    this.source$ = this.modelBrowserRelationshipRowService.source;
    this.target$ = this.modelBrowserRelationshipRowService.target;
    this.type$ = this.modelBrowserRelationshipRowService.type;
  }

  @Input() set entity(relationship: ModelRelation) {
    this.modelBrowserRelationshipRowService.relationship = relationship;
  }
}
