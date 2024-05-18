import { Component, OnInit } from '@angular/core';
import { AbstractSortableTable, SortableTableShellConfig } from '@models4insight/components';
import { Project } from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';

const provenanceTableConfig: SortableTableShellConfig = {
  start_user: {
    displayName: 'User',
    description: 'The name of the user who committed the model',
    isStatic: true
  },
  branch: {
    displayName: 'Branch',
    description: 'The name of the branch to which the model was committed',
    isStatic: true
  },
  operation: {
    displayName: 'Operation',
    description: 'Whether the model was cloned, merged, or committed directly',
    isStatic: true
  },
  comment: {
    displayName: 'Comment',
    description: 'A short description of the model',
    isStatic: true
  },
  start_date: {
    displayName: 'Timestamp',
    description: 'When the model was committed',
    isStatic: true,
    isTimestamp: true
  },
  context_menu: { isStatic: true }
};

@Component({
  selector: 'models4insight-provenance-table',
  templateUrl: 'provenance-table.component.html',
  styleUrls: ['provenance-table.component.scss']
})
export class ProvenanceTableComponent extends AbstractSortableTable
  implements OnInit {
  project$: Observable<Project>;

  constructor(private readonly projectService: ProjectService) {
    super();
  }

  ngOnInit() {
    this.config = provenanceTableConfig;

    this.project$ = this.projectService.selectCurrentProject().pipe(shareReplay());
  }
}
