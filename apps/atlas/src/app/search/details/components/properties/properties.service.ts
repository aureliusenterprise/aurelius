import { Injectable } from '@angular/core';
import { BasicStore } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { FilteredPropertiesService } from '../../../services/filtered-properties/filtered-properties.service';

export interface DataForTable {
  name: string;
  value: any;
  description?: string;
  cardinalitySET?: boolean;
  isReference?: boolean;
  showIfEmpty?: boolean;
}

export interface SuperTypeStoreContext {
  readonly propertiesList?: DataForTable[];
}

@Injectable()
export class PropertiesService extends BasicStore<SuperTypeStoreContext> {
  constructor(
    private readonly filteredPropertiesService: FilteredPropertiesService
  ) {
    super();
    this.init();
  }

  private init() {
    this.filteredPropertiesService.state
      .pipe(untilDestroyed(this))
      .subscribe(properties => this.handleFormatTableData(properties));
  }

  private handleFormatTableData(properties: Dictionary<any>) {
    const propertiesList = Object.entries(properties).map(([name, value]) => ({
      name,
      value
    }));
    this.update({
      description: 'New data for properties table available',
      payload: { propertiesList }
    });
  }
}
