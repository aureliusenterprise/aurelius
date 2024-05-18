import { Component, Inject, OnInit, Optional } from '@angular/core';
import { Observable } from 'rxjs';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';
import { SHOW_DATA_QUALITY } from '../config';

@Component({
  selector: 'models4insight-collection-details-card',
  templateUrl: 'collection-details-card.component.html',
  styleUrls: ['collection-details-card.component.scss']
})
export class CollectionDetailsCardComponent implements OnInit {
  parentId$: Observable<string>;

  constructor(
    @Optional() @Inject(SHOW_DATA_QUALITY) readonly showDataQuality: boolean,
    private readonly entityDetailsService: EntityDetailsService
  ) {
    this.showDataQuality = this.showDataQuality ?? true;
  }

  ngOnInit() {
    this.parentId$ = this.entityDetailsService.parent?.select('entityId');
  }
}
