import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { SortableTableShellConfig } from '@models4insight/components';
import { createHttpParams, GetOptions } from '@models4insight/repository';
import { Dictionary } from 'lodash';
import { Observable } from 'rxjs';
import { CoreModule } from './core.module';

export interface ReportDatasetConfig<T = Dictionary<any>> {
  readonly data?: SortableTableShellConfig<T>;
  readonly description?: string;
  readonly docsUrl?: string;
  readonly color_column?: keyof T;
  readonly id_column?: keyof T;
}

export interface ReportDataset<T = Dictionary<any>> {
  readonly config: ReportDatasetConfig<T>;
  readonly data: T[];
  readonly type: 'accepted' | 'aggregate' | 'metric';
}

export interface ReportData<T = Dictionary<any>> {
  readonly [title: string]: ReportDataset<T>;
}

export interface ReportChart<T = Dictionary<any>> {
  readonly type: 'chart';
  readonly chart: any;
  readonly data: ReportData<T>;
}

export interface ReportTable<T = Dictionary<any>> {
  readonly type: 'table';
  readonly data: ReportData<T>;
}

export type ReportMetric<T = Dictionary<any>> = ReportChart<T> | ReportTable<T>;

export interface ReportCategory {
  readonly [title: string]: string;
}

export interface Report {
  readonly [title: string]: ReportCategory;
}

@Injectable({
  providedIn: CoreModule
})
export class ReportService {
  readonly basePath = 'flask';

  constructor(private readonly http: HttpClient) {}

  getMetric(
    project: string,
    branch: string,
    metric: string,
    version?: number,
    options: GetOptions = {}
  ): Observable<ReportMetric> {
    const path = `${this.basePath}/metric`;

    // verify required parameter 'project' is not null or undefined
    if (project === null || project === undefined) {
      throw new Error(
        'Required parameter project was null or undefined when calling getMetric.'
      );
    }

    // verify required parameter 'branch' is not null or undefined
    if (branch === null || branch === undefined) {
      throw new Error(
        'Required parameter branch was null or undefined when calling getMetric.'
      );
    }

    // verify required parameter 'metric' is not null or undefined
    if (metric === null || metric === undefined) {
      throw new Error(
        'Required parameter metric was null or undefined when calling getMetric.'
      );
    }

    const requestParams = createHttpParams({
      project,
      branch,
      metric,
      version
    });

    const requestOptions = {
      params: requestParams
    };

    return this.http
      .authorize()
      .cache(options.forceUpdate)
      .get<ReportMetric>(path, requestOptions);
  }

  getReport(options: GetOptions = {}): Observable<Report> {
    return this.http
      .cache(options.forceUpdate)
      .get<Report>(`${this.basePath}/report`);
  }
}
