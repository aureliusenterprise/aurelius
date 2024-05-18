import { Injectable } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';
import { MetricExemption } from '@models4insight/repository';
import { groupBy } from '@models4insight/utils';
import { Dictionary, flatten, omit } from 'lodash';
import { combineLatest } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { ExemptionsService } from './exemptions.service';
import { ReportService } from './report.service';

export interface ViolationsStoreContext {
  readonly bucketMapping?: Dictionary<string>;
  readonly filteredViolations?: Dictionary<any>[];
  readonly violationsPerConcept?: Dictionary<any[]>;
}

@Injectable()
export class ViolationsService extends BasicStore<ViolationsStoreContext> {
  constructor(
    private readonly exemptionsService: ExemptionsService,
    private readonly reportService: ReportService,
    storeService: StoreService
  ) {
    super({ name: 'ViolationsService', storeService });
    this.init();
  }

  private init() {
    // Whenever the dataset changes, build an index of the rows by ID if the ID column is known
    this.reportService
      .select('dataset')
      .pipe(switchMap(datasetName => this.handleIndexViolations(datasetName)))
      .subscribe();

    // Whenever the violations or exemptions index update, create a list of violations that excludes the exempt ones
    combineLatest([
      this.reportService.select('dataset'),
      this.select('violationsPerConcept'),
      this.exemptionsService.select('exemptionsPerConcept')
    ])
      .pipe(
        switchMap(([datasetName, violationsPerConcept, exemptionsPerConcept]) =>
          this.handleFilterVolations(
            datasetName,
            violationsPerConcept,
            exemptionsPerConcept
          )
        )
      )
      .subscribe();

    combineLatest([
      this.reportService.select('dataset'),
      this.select('filteredViolations')
    ])
      .pipe(
        switchMap(([datasetName, violationsPerConcept]) =>
          this.handleCreateBucketMapping(datasetName, violationsPerConcept)
        )
      )
      .subscribe();
  }

  private async handleCreateBucketMapping(
    datasetName: string,
    violations: Dictionary<any>[]
  ) {
    const bucketMapping: Dictionary<string> = {};

    const {
      color_column: colorColumn,
      id_column: idColumn
    } = await this.reportService.get(['metric', 'data', datasetName, 'config']);

    if (colorColumn && idColumn) {
      // If there are multiple violations per concept,
      // take the color column of the first violation as the bucket id
      // since the color view does not support multiple fill colors
      for (const violation of violations) {
        const conceptId = violation[idColumn];
        if (conceptId in bucketMapping) continue;
        bucketMapping[conceptId] = violation[colorColumn];
      }
    }

    this.update({
      description: 'New bucket mapping available',
      payload: { bucketMapping }
    });
  }

  private async handleFilterVolations(
    datasetName: string,
    violationsPerConcept: Dictionary<any[]>,
    exemptionsPerConcept: Dictionary<MetricExemption[]>
  ) {
    const dataset = await this.reportService.get([
      'metric',
      'data',
      datasetName
    ]);

    let filteredViolations = dataset.data;

    if (dataset.config.id_column) {
      const violationsPerNonExemptedConcept = omit(
        violationsPerConcept,
        Object.keys(exemptionsPerConcept)
      );
      filteredViolations = flatten(
        Object.values(violationsPerNonExemptedConcept)
      );
    }

    this.update({
      description: 'New filtered violations available',
      payload: { filteredViolations }
    });
  }

  private async handleIndexViolations(datasetName: string) {
    const dataset = await this.reportService.get([
      'metric',
      'data',
      datasetName
    ]);

    const violationsPerConcept =
      dataset && dataset.config.id_column
        ? groupBy(dataset.data, dataset.config.id_column)
        : {};

    this.update({
      description: 'New violations index available',
      payload: { violationsPerConcept }
    });
  }
}
