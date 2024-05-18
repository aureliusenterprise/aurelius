import { Injectable } from '@angular/core';
import { AuthenticationService } from '@models4insight/authentication';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import { downloadModel } from '@models4insight/repository';
import { ModelService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary, invert } from 'lodash';
import { Subject } from 'rxjs';
import { exhaustMap, switchMap } from 'rxjs/operators';
import {
  Report,
  ReportCategory,
  ReportMetric,
  ReportService as ApiService
} from '../../core/report.service';

export interface ReportParameters {
  readonly branch?: string;
  readonly metricKey?: string;
  readonly project?: string;
  readonly version?: number;
}

export interface ReportStoreContext {
  readonly dataset?: string;
  readonly isBuildingMetricNamesIndex?: boolean;
  readonly isRetrievingMetric?: boolean;
  readonly metric?: ReportMetric;
  readonly metricKey?: string;
  readonly metricIdByName?: Dictionary<string>;
  readonly metricNameById?: Dictionary<string>;
  readonly report?: Report;
}

export type ExemptionScope = 'project' | 'branch' | 'version';

@Injectable()
export class ReportService extends BasicStore<ReportStoreContext> {
  private readonly retrieveModel$ = new Subject<void>();

  constructor(
    private readonly apiService: ApiService,
    private readonly authenticationService: AuthenticationService,
    private readonly modelService: ModelService,
    private readonly projectService: ProjectService,
    storeService: StoreService
  ) {
    super({ name: 'ReportService', storeService });
    this.init();
  }

  private init() {
    this.retrieveModel$
      .pipe(
        exhaustMap(() => this.handleRetrieveModel()),
        untilDestroyed(this)
      )
      .subscribe();

    this.select('report')
      .pipe(
        switchMap(report => this.handleBuildMetricNamesIndex(report)),
        untilDestroyed(this)
      )
      .subscribe();

    this.select('metricKey')
      .pipe(
        switchMap(metricKey => this.handleRetrieveMetric(metricKey)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  retrieveModel() {
    this.retrieveModel$.next();
  }

  @MonitorAsync('isRetrievingMetric')
  @ManagedTask('Retrieving the metric', { isQuiet: true })
  private async handleRetrieveMetric(metricKey: string) {
    const [branchName, { project }, version] = await Promise.all([
      this.modelService.get('branch'),
      this.projectService.getCurrentProject(),
      this.modelService.get('version', { includeFalsy: true })
    ]);

    const metric = await this.apiService
      .getMetric(project, branchName, metricKey, version)
      .toPromise();

    const dataset = Object.keys(metric?.data ?? {})[0];

    this.update({
      description: 'New metric available',
      payload: {
        metric,
        dataset
      }
    });
  }

  @MonitorAsync('isBuildingMetricNamesIndex')
  @ManagedTask('Building the metric names index', { isQuiet: true })
  private async handleBuildMetricNamesIndex(report: Report) {
    const indexMetricCategory = (category: ReportCategory) =>
      Object.entries(category).reduce(
        (categoryNamesIndex, [metricName, metricId]) => ({
          ...categoryNamesIndex,
          [metricId]: metricName
        }),
        {}
      );

    const result = Object.values(report).reduce(
      (metricNamesIndex, category) => ({
        ...metricNamesIndex,
        ...indexMetricCategory(category)
      }),
      {}
    );

    this.update({
      description: 'New metric names index available',
      payload: { metricNameById: result, metricIdByName: invert(result) }
    });
  }

  @ManagedTask('Retrieving the model')
  @MonitorAsync('isRetrievingModel')
  private async handleRetrieveModel() {
    const [branch, project, username, version] = await Promise.all([
      this.modelService.get('branch'),
      this.projectService.get('projectId'),
      this.authenticationService.get(['credentials', 'username']),
      this.modelService.get('version', { includeFalsy: true })
    ]);

    return downloadModel(project, branch, username, version).toPromise();
  }
}
