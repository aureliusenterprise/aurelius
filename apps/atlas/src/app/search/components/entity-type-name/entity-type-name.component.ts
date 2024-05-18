import { Component, Input } from '@angular/core';
import { EntityElementWithEXTInfo } from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';

@Component({
  selector: 'models4insight-entity-type-name',
  templateUrl: 'entity-type-name.component.html',
  styleUrls: ['entity-type-name.component.scss'],
})
export class EntityTypeNameComponent {
  /**
   * Whether or not to display the base type in parentheses when a type alias is given.
   */
  @Input() showBaseTypeName = false;

  /**
   * Whether or not to display the type icon.
   */
  @Input() showIcon = true;

  /**
   * Whether or not to display the type name or type alias.
   */
  @Input() showTypeName = true;

  /**
   * Observable stream of the current Atlas entity.
   */
  protected readonly entityDetails$: Observable<EntityElementWithEXTInfo>;

  constructor(private readonly entityDetailsService: EntityDetailsService) {
    this.entityDetails$ = this.entityDetailsService.entityDetails$;
  }
}
