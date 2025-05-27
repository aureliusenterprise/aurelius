import { Component, Input, OnInit } from '@angular/core';
import { Observable, of } from 'rxjs';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';

@Component({
  selector: 'models4insight-description',
  templateUrl: './description.component.html',
  styleUrls: ['./description.component.scss'],
})
export class DescriptionComponent implements OnInit {
  description$: Observable<string>;

  @Input() showPlaceholder = true;

  constructor(private readonly entityDetailsService: EntityDetailsService) {}

  ngOnInit() {
    this.description$ = this.entityDetailsService.select(
      ['entityDetails', 'entity', 'attributes', 'definition'],
      { includeFalsy: true }
    );
    this.entityDetailsService.select(['entityDetails', 'entity', 'typeName'], { includeFalsy: true }).subscribe(typeName => {
      if (typeName === 'm4i_gov_data_quality' || typeName === 'm4i_data_quality') {
        this.description$ = this.entityDetailsService.select(
          ['entityDetails', 'entity', 'attributes', 'ruleDescription'],
          { includeFalsy: true }
        );
      }
    });
  }
}
