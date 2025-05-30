import { Component, Inject, OnInit, Optional } from '@angular/core';
import { Observable } from 'rxjs';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';
import { SHOW_DATA_QUALITY } from '../config';

@Component({
  selector: 'models4insight-dataset-details-card',
  templateUrl: 'dataset-details-card.component.html',
  styleUrls: ['dataset-details-card.component.scss']
})
export class DatasetDetailsCardComponent implements OnInit {
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
