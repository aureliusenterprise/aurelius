import { Component, Input } from '@angular/core';
import { Observable, switchMap } from 'rxjs';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';

@Component({
  selector: 'models4insight-description',
  templateUrl: './description.component.html',
  styleUrls: ['./description.component.scss'],
})
export class DescriptionComponent {
  description$: Observable<string> = this.entityDetailsService.select(
    ['entityDetails', 'entity', 'typeName'],
    { includeFalsy: true }
  ).pipe(
    switchMap((typeName) => this.selectDescriptionField(typeName))
  );

  @Input() showPlaceholder = true;

  constructor(private readonly entityDetailsService: EntityDetailsService) {}

  private selectDescriptionField(typeName: string): Observable<string> {
    if (typeName === 'm4i_gov_data_quality' || typeName === 'm4i_data_quality') {
      return this.entityDetailsService.select(
        ['entityDetails', 'entity', 'attributes', 'ruleDescription'],
        { includeFalsy: true }
      );
    }
    else {
      return this.entityDetailsService.select(
        ['entityDetails', 'entity', 'attributes', 'definition'],
        { includeFalsy: true }
      );
    }
  }
}
