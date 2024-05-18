import { Injectable } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';
import { MetricExemption } from '@models4insight/repository';
import { Dictionary, flatten, intersection } from 'lodash';
import { combineLatest } from 'rxjs';
import { map } from 'rxjs/operators';
import { ExemptionsService } from '../exemptions.service';
import { ViolationsService } from '../violations.service';

export interface ReportExemptionsStoreContext {
  readonly displayExemptionsPerConcept: Dictionary<(MetricExemption & any)[]>;
}

@Injectable()
export class ReportExemptionsService extends BasicStore<
  ReportExemptionsStoreContext
> {
  constructor(
    private readonly exemptionsService: ExemptionsService,
    private readonly violationsService: ViolationsService,
    storeService: StoreService
  ) {
    super({ name: 'ReportExemptionsService', storeService });
    this.init();
  }

  get exemptions() {
    return this.select('displayExemptionsPerConcept').pipe(
      map(exemptions => flatten(Object.values(exemptions)))
    );
  }

  private init() {
    // Whenever the violations or exemptions are updated, build an index of display values
    combineLatest([
      this.violationsService.select('violationsPerConcept'),
      this.exemptionsService.select('exemptionsPerConcept')
    ]).subscribe(([violationsPerConcept, exemptionsPerConcept]) =>
      this.reduceDisplayExemptions(violationsPerConcept, exemptionsPerConcept)
    );
  }

  private reduceDisplayExemptions(
    violationsPerConcept: Dictionary<any[]>,
    exemptionsPerConcept: Dictionary<MetricExemption[]>
  ) {
    // Find the concept ids which have both a violation and an exemption associated with them
    const sharedConceptIds = intersection(
      Object.keys(violationsPerConcept),
      Object.keys(exemptionsPerConcept)
    );

    // For every concept id found, join the violation and exemption together so we can display the combined values.
    // Assume there is always a single violation.
    const displayExemptionsPerConcept = sharedConceptIds.reduce(
      (result, conceptId) => ({
        ...result,
        [conceptId]: exemptionsPerConcept[conceptId].map(exemption => ({
          ...exemption,
          exemption_id: exemption.id,
          ...violationsPerConcept[conceptId][0]
        }))
      }),
      {} as Dictionary<(MetricExemption & any)[]>
    );

    this.update({
      description: 'New display exemptions available',
      payload: { displayExemptionsPerConcept }
    });
  }
}
