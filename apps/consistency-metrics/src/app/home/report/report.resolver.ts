import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, Resolve, RouterStateSnapshot } from '@angular/router';
import { BranchesService } from '@models4insight/services/branch';
import { ModelService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import { ReportService } from '../../core/report.service';
import { ReportService as ReportStore } from './report.service';

@Injectable()
export class ReportResolver implements Resolve<void> {
  constructor(
    private readonly branchesService: BranchesService,
    private readonly modelService: ModelService,
    private readonly projectService: ProjectService,
    private readonly reportStore: ReportStore,
    private readonly reportService: ReportService
  ) {}

  async resolve(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Promise<void> {
    const projectId = route.queryParamMap.get('project'),
      branchId = route.queryParamMap.get('branch'),
      version = Number.parseInt(route.queryParamMap.get('version'), 10),
      metricKey = route.queryParamMap.get('metric');

    this.projectService.setCurrentProject(projectId);

    const branch = branchId
      ? await this.branchesService.getBranchById(branchId)
      : null;

    this.modelService.update({
      description: 'New branch and version available',
      payload: {
        branch: branch?.name,
        version
      }
    });

    const report = await this.retrieveReportStructure();

    this.reportStore.update({
      description: 'New report context available',
      payload: {
        metricKey,
        report
      }
    });
  }

  @ManagedTask('Retrieving the report structure', { isQuiet: true })
  private retrieveReportStructure() {
    return this.reportService.getReport().toPromise();
  }
}
