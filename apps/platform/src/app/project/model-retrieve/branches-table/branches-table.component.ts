import { Component, OnInit } from '@angular/core';
import { AbstractSortableTable, SortableTableShellConfig } from '@models4insight/components';
import { Project } from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';

const branchesTableConfig: SortableTableShellConfig = {
  _id: { displayName: 'Branch name', description: 'The name of the branch' },
  cnt: {
    displayName: 'Total updates',
    description: 'The total numer of model versions in this branch'
  },
  context_menu: { isStatic: true }
};

@Component({
  selector: 'models4insight-branches-table',
  templateUrl: 'branches-table.component.html',
  styleUrls: ['branches-table.component.scss']
})
export class BranchesTableComponent extends AbstractSortableTable
  implements OnInit {
  project$: Observable<Project>;

  constructor(private readonly projectService: ProjectService) {
    super();
  }

  ngOnInit() {
    this.config = branchesTableConfig;

    this.project$ = this.projectService.selectCurrentProject().pipe(shareReplay());
  }
}
