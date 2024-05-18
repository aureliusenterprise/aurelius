import { Injectable } from '@angular/core';
import { CalendarHeatmapContext } from '@models4insight/components';
import { BasicStore, StoreService } from '@models4insight/redux';
import { ModelProvenance, ModelProvenanceSummary } from '@models4insight/repository';
import { untilDestroyed } from '@models4insight/utils';
import { sum } from 'lodash';
import { switchMap } from 'rxjs/operators';

export interface ProjectHomeStoreContext {
  readonly latestActivity?: ModelProvenance[];
  readonly heatmapData?: ModelProvenanceSummary[];
  readonly heatmapContext?: CalendarHeatmapContext;
}

export const defaultProjectHomeServiceState: ProjectHomeStoreContext = {
  heatmapContext: {
    data: {},
    domain: 'month',
    legend: [],
    range: 12,
    start: new Date(),
    subdomain: 'x_day'
  }
};

@Injectable()
export class ProjectHomeService extends BasicStore<ProjectHomeStoreContext> {
  constructor(storeService: StoreService) {
    super({
      defaultState: defaultProjectHomeServiceState,
      name: 'ProjectHomeService',
      storeService
    });
    this.init();
  }

  private init() {
    this.select('heatmapData')
      .pipe(
        switchMap(data => this.handleCalculateHeatmapContext(data)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  private async handleCalculateHeatmapContext(
    provenance: ModelProvenanceSummary[]
  ) {
    // Rounds the timestamp down to a day based on the current timezone of the user
    const roundTimestamp = (timestamp: number) => {
      // Subtract amount of time since midnight
      timestamp -= timestamp % (24 * 60 * 60 * 1000);
      // Add on the timezone offset
      timestamp += new Date().getTimezoneOffset() * 60 * 1000;
      return timestamp;
    };

    const roundedDates = provenance.map(p => ({
      ...p,
      start_date: roundTimestamp(p.start_date)
    }));

    const data = roundedDates.reduce((acc, p) => {
      acc[p.start_date / 1000] = p.cnt;
      return acc;
    }, {} as { [key: number]: number });

    const dates = roundedDates.map(p => p.start_date);

    const start = Math.min(...dates);
    const end = Math.max(...dates);

    const days = (end - start) / (60 * 60 * 24 * 1000);
    const avg = sum(Object.values(data)) / days;

    this.update({
      description: 'New heatmap context available',
      path: ['heatmapContext'],
      payload: {
        start: new Date(end - 60 * 60 * 24 * 1000 * 365),
        legend: [Math.round(avg * 0.5), Math.round(avg), Math.round(avg * 1.5)],
        range: 13,
        domain: 'month',
        subdomain: 'x_day',
        data: data
      }
    });
  }
}
