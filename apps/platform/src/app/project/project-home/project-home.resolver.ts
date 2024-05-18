import { Injectable } from '@angular/core';
import {
  ActivatedRouteSnapshot,
  Resolve,
  RouterStateSnapshot
} from '@angular/router';
import {
  getProvenance,
  getProvenanceSummary,
  ModelProvenance,
  ModelProvenanceSummary
} from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import { ProjectHomeService } from './project-home.service';

export const RECENT_ACTIVITY_BATCH_SIZE = 5;

export interface ProjectHomeParams {
  heatmapData: ModelProvenanceSummary[];
  latestActivity: ModelProvenance[];
}

@Injectable()
export class ProjectHomeResolver implements Resolve<ProjectHomeParams> {
  constructor(
    private readonly projectHomeService: ProjectHomeService,
    private readonly projectService: ProjectService
  ) {}

  async resolve(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Promise<ProjectHomeParams> {
    const { project } = await this.projectService.getCurrentProject();

    const [heatmapData, latestActivity] = await Promise.all([
      this.handleGetHeatmapData(project),
      this.handleGetRecentActivity(project)
    ]);

    const result = {
      heatmapData,
      latestActivity
    };

    this.projectHomeService.update({
      description: 'New project home data available',
      payload: result
    });

    return result;
  }

  @ManagedTask('Retrieving the project activity summary', { isQuiet: true })
  private async handleGetHeatmapData(projectName: string) {
    return getProvenanceSummary(projectName, {
      forceUpdate: true
    }).toPromise();
  }

  @ManagedTask('Retrieving the most recent model versions', { isQuiet: true })
  private async handleGetRecentActivity(projectName: string) {
    return getProvenance(projectName, {
      batchSize: RECENT_ACTIVITY_BATCH_SIZE,
      forceUpdate: true
    }).toPromise();
  }
}
