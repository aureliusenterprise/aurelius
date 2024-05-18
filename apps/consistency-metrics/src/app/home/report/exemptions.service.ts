import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import {
  createMetricExemption,
  deleteMetricExemption,
  getMetricExemption,
  MetricExemption
} from '@models4insight/repository';
import { BranchesService } from '@models4insight/services/branch';
import { ModelService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import {
  groupBy,
  untilDestroyed,
  indexByProperty
} from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { Subject } from 'rxjs';
import { concatMap, map, switchMap } from 'rxjs/operators';
import { ReportService } from './report.service';

export interface ExemptionsStoreContext {
  readonly exemptionsById?: Dictionary<MetricExemption>;
  readonly exemptionsPerConcept?: Dictionary<MetricExemption[]>;
  readonly isCreatingExemption?: boolean;
  readonly isRemovingExemption?: boolean;
}

export const defaultExemptionsServiceState: ExemptionsStoreContext = {
  isCreatingExemption: false,
  isRemovingExemption: false
};

export type ExemptionScope = 'project' | 'branch' | 'version';

type CreateExemptionContext = [string, string, ExemptionScope, string?];

@Injectable()
export class ExemptionsService extends BasicStore<ExemptionsStoreContext> {
  private readonly createExemption$ = new Subject<CreateExemptionContext>();
  private readonly removeExemption$ = new Subject<string>();

  constructor(
    private readonly branchesService: BranchesService,
    private readonly modelService: ModelService,
    private readonly projectService: ProjectService,
    private readonly reportService: ReportService,
    storeService: StoreService
  ) {
    super({
      defaultState: defaultExemptionsServiceState,
      name: 'ExemptionsService',
      storeService
    });
    this.init();
  }

  private init() {
    this.createExemption$
      .pipe(
        concatMap(([conceptId, comment, scope, id]) =>
          this.handleCreateExemption(conceptId, comment, scope, id)
        ),
        untilDestroyed(this)
      )
      .subscribe();

    this.removeExemption$
      .pipe(
        concatMap(exemptionId => this.handleRemoveExemption(exemptionId)),
        untilDestroyed(this)
      )
      .subscribe();

    // Whenever the metric changes, retireve the associated exemptions
    this.reportService
      .select('metricKey')
      .pipe(
        switchMap(metricKey => this.retrieveMetricExemptions(metricKey)),
        untilDestroyed(this)
      )
      .subscribe();

    // Whenever the exemptions are updated, create an index of the exemptions per concept id
    this.exemptions
      .pipe(
        map(exemptions => groupBy(exemptions, 'concept_id')),
        untilDestroyed(this)
      )
      .subscribe(exemptionsPerConcept =>
        this.update({
          description: 'New exemptions per concept index available',
          payload: { exemptionsPerConcept }
        })
      );
  }

  createExemption(
    conceptId: string,
    comment: string,
    scope: ExemptionScope,
    id?: string
  ) {
    this.createExemption$.next([conceptId, comment, scope, id]);
  }

  removeExemption(exemptionId: string) {
    this.removeExemption$.next(exemptionId);
  }

  get exemptions() {
    return this.select('exemptionsById').pipe(map(Object.values));
  }

  @ManagedTask('Committing the exemption', { isQuiet: true })
  @MonitorAsync('isCreatingExemption')
  private async handleCreateExemption(
    conceptId: string,
    comment: string,
    scope: ExemptionScope,
    id: string = null
  ) {
    const [branchName, metricKey, project, version] = await Promise.all([
      this.modelService.get('branch'),
      this.reportService.get('metricKey'),
      this.projectService.get('projectId'),
      this.modelService.get('version', { includeFalsy: true })
    ]);

    const branch = await this.branchesService.getBranchByName(branchName);

    const exemption: MetricExemption = await createMetricExemption({
      id,
      branch: scope !== 'project' ? branch.id : null,
      comment,
      concept_id: conceptId,
      metric: metricKey,
      project_id: project,
      version: scope === 'version' ? version : null
    }).toPromise();

    this.update({
      description: 'Exemption successfully committed',
      path: ['exemptionsById', exemption.id],
      payload: exemption
    });
  }

  @ManagedTask('Removing the exemption', { isQuiet: true })
  @MonitorAsync('isRemovingExemption')
  private async handleRemoveExemption(exemptionId: string) {
    const projectId = await this.projectService.get('projectId');

    await deleteMetricExemption(projectId, exemptionId).toPromise();

    this.delete({
      description: `Removed exemption ${exemptionId}`,
      path: ['exemptionsById', exemptionId]
    });
  }

  @ManagedTask('Retrieving the exemptions for the metric', { isQuiet: true })
  @MonitorAsync('isRetrievingExemptions')
  private async retrieveMetricExemptions(metricName: string) {
    const [project, branchName, version] = await Promise.all([
      this.projectService.get('projectId'),
      this.modelService.get('branch'),
      this.modelService.get('version')
    ]);

    const branch = await this.branchesService.getBranchByName(branchName);

    const exemptions = await getMetricExemption(project, {
      branchId: branch.id,
      metricName,
      version,
      forceUpdate: true
    }).toPromise();

    const exemptionsById = exemptions ? indexByProperty(exemptions, 'id') : {};

    this.update({
      description: 'New exemptions available',
      payload: { exemptionsById }
    });
  }
}
