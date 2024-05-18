import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { AbstractSortableTable, SortableTableShellConfig } from '@models4insight/components';
import { Branch, Project } from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';

const branchesTableConfig: SortableTableShellConfig = {
  name: { displayName: 'Branch name', description: 'The name of the branch' },
  description: {
    displayName: 'Description',
    description: 'The description of the branch'
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
  @Output() edit: EventEmitter<Branch> = new EventEmitter<Branch>();

  project$: Observable<Project>;

  constructor(private readonly projectService: ProjectService) {
    super();
  }

  ngOnInit() {
    this.config = branchesTableConfig;

    this.project$ = this.projectService.selectCurrentProject().pipe(shareReplay());
  }

  onEdit(branch: Branch) {
    this.edit.emit(branch);
  }
}