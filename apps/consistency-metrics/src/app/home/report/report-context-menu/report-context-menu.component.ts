import { Component } from '@angular/core';
import { faDownload, faGlobe, faProjectDiagram } from '@fortawesome/free-solid-svg-icons';
import { ContextMenuItems } from '@models4insight/components';
import { ModelService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { ReportService } from '../report.service';

@Component({
  selector: 'models4insight-report-context-menu',
  templateUrl: 'report-context-menu.component.html',
  styleUrls: ['report-context-menu.component.scss']
})
export class ReportContextMenuComponent {
  contextMenuItems: ContextMenuItems = [
    [
      {
        click: () => this.reportService.retrieveModel(),
        icon: faDownload,
        iconModifier: 'has-text-success',
        title: 'Retrieve the model'
      }
    ],
    [
      {
        click: () => this.openExplorerInNewTab(),
        icon: faGlobe,
        iconModifier: 'has-text-link',
        title: 'Explore the model'
      },
      {
        click: () => this.openProjectInNewTab(),
        icon: faProjectDiagram,
        iconModifier: 'has-text-link',
        title: 'Open the project'
      }
    ]
  ];

  constructor(
    private readonly modelService: ModelService,
    private readonly projectService: ProjectService,
    private readonly reportService: ReportService
  ) {}

  private async openExplorerInNewTab() {
    const [branchName, projectId, version] = await Promise.all([
      this.modelService.get('branch'),
      this.projectService.get('projectId'),
      this.modelService.get('version')
    ]);
    window.open(
      `/platform/project/${projectId}/explore?branchName=${branchName}&version=${version}`,
      '_blank'
    );
  }

  private async openProjectInNewTab() {
    const projectId = await this.projectService.get('projectId');
    window.open(`/platform/project/${projectId}`, '_blank');
  }
}
