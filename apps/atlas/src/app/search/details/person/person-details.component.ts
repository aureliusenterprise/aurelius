import { Component, OnInit, ViewChild } from '@angular/core';
import { defaultIfFalsy } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { EntityDetailsService } from '../../services/entity-details/entity-details.service';
import { FilteredPropertiesService } from '../../services/filtered-properties/filtered-properties.service';
import { GovernanceRolesCardsComponent } from './governance-roles-cards/governance-roles-cards.component';

@Component({
  selector: 'models4insight-person-details',
  templateUrl: 'person-details.component.html',
  styleUrls: ['person-details.component.scss'],
})
export class PersonDetailsComponent implements OnInit {
  @ViewChild(GovernanceRolesCardsComponent, { static: true })
  private readonly governanceRoles: GovernanceRolesCardsComponent;

  dataOwnerAttributeCount$: Observable<number>;
  dataOwnerEntityCount$: Observable<number>;
  dataStewardAttributeCount$: Observable<number>;
  dataStewardEntityCount$: Observable<number>;
  domainLeadCount$: Observable<number>;
  propertyCount$: Observable<number>;

  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly filteredPropertiesService: FilteredPropertiesService
  ) {}

  ngOnInit() {
    this.dataOwnerEntityCount$ = this.entityDetailsService
      .select(
        [
          'entityDetails',
          'entity',
          'relationshipAttributes',
          'businessOwnerEntity',
          'length',
        ],
        { includeFalsy: true }
      )
      .pipe(defaultIfFalsy(0));

    this.dataOwnerAttributeCount$ = this.entityDetailsService
      .select(
        [
          'entityDetails',
          'entity',
          'relationshipAttributes',
          'businessOwnerAttribute',
          'length',
        ],
        { includeFalsy: true }
      )
      .pipe(defaultIfFalsy(0));

    this.dataStewardEntityCount$ = this.entityDetailsService
      .select(
        [
          'entityDetails',
          'entity',
          'relationshipAttributes',
          'stewardEntity',
          'length',
        ],
        { includeFalsy: true }
      )
      .pipe(defaultIfFalsy(0));

    this.dataStewardAttributeCount$ = this.entityDetailsService
      .select(
        [
          'entityDetails',
          'entity',
          'relationshipAttributes',
          'stewardAttribute',
          'length',
        ],
        { includeFalsy: true }
      )
      .pipe(defaultIfFalsy(0));

    this.domainLeadCount$ = this.entityDetailsService
      .select(
        [
          'entityDetails',
          'entity',
          'relationshipAttributes',
          'domainLead',
          'length',
        ],
        { includeFalsy: true }
      )
      .pipe(defaultIfFalsy(0));

    this.propertyCount$ = this.filteredPropertiesService.state.pipe(
      map((properties) => Object.keys(properties).length)
    );
  }

  async filterResponsibilitiesByType(
    typeName: string,
    role: 'datasteward' | 'dataowner' | 'domainlead'
  ) {
    const [id, queryObject] = await Promise.all([
      this.entityDetailsService.get('entityId'),
      this.governanceRoles.searchService.get('queryObject'),
    ]);

    const currentFilters = queryObject.filters;

    this.governanceRoles.searchService.filters = {
      ...currentFilters,
      all: [
        { typename: [typeName] },
        { [`derived${role}guid`]: [id] },
      ],
    };
  }
}
