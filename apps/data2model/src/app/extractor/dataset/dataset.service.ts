import { Injectable } from '@angular/core';
import { SortableTableShellColumnConfig, SortableTableShellConfig } from '@models4insight/components';
import { BasicStore, StoreService } from '@models4insight/redux';
import { ExtractorService } from '../extractor.service';

export interface DatasetStoreContext {
  readonly tableConfig: SortableTableShellConfig;
}

@Injectable()
export class DatasetService extends BasicStore<DatasetStoreContext> {
  constructor(
    private readonly extractorService: ExtractorService,
    storeService: StoreService
  ) {
    super({ name: 'DatasetService', storeService });
    this.init();
  }

  private init() {
    // Whenever the dataset headers update, update the table config
    this.extractorService
      .select('currentHeaders')
      .subscribe(headers => this.updateTableConfig(headers));
  }

  private updateTableConfig(headers: string[]) {
    const tableConfig: SortableTableShellConfig = headers.reduce(
      (config, key) => ({
        ...config,
        [key]: { displayName: key } as SortableTableShellColumnConfig
      }),
      {} as SortableTableShellConfig
    );

    this.update({
      description: 'New table config available',
      payload: {
        tableConfig
      }
    });
  }
}
