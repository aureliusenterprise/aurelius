import { Injectable } from '@angular/core';
import { EntityElementWithEXTInfo } from '@models4insight/atlas/api';
import { BasicStore } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary, isNil, isObjectLike, omitBy } from 'lodash';
import { EntityDetailsService } from '../entity-details/entity-details.service';
import { blacklistedProperties } from './blacklist-properties';

function propertiesFilter(value: any, key: string) {
  return isNil(value) || blacklistedProperties.has(key);
}

@Injectable()
export class FilteredPropertiesService extends BasicStore<Dictionary<any>> {
  constructor(private readonly entityDetailsService: EntityDetailsService) {
    super();
    this.init();
  }

  private init() {
    this.entityDetailsService
      .select(['entityDetails', 'entity'])
      .pipe(untilDestroyed(this))
      .subscribe(entity => this.handleFilterWhitelistedProperties(entity));
  }

  private handleFilterWhitelistedProperties(entity: EntityElementWithEXTInfo) {
    const properties = {
      ...entity.attributes,
      ...entity.relationshipAttributes
    };

    const filteredProperties = omitBy(properties, propertiesFilter);

    this.set({
      description: 'New whitelisted properties available',
      payload: filteredProperties
    });
  }
}
