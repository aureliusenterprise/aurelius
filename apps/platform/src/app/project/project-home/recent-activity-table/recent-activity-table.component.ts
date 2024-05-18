import { Component, OnInit } from '@angular/core';
import { AbstractSortableTable, SortableTableShellConfig } from '@models4insight/components';

const recentActivityTableConfig: SortableTableShellConfig = {
  start_user: {
    displayName: 'User',
    description: 'The name of the user who committed the model'
  },
  branch: {
    displayName: 'Branch',
    description: 'The name of the branch to which the model was committed'
  },
  operation: {
    displayName: 'Operation',
    description: 'Whether the model was cloned, merged, or committed directly'
  },
  comment: {
    displayName: 'Comment',
    description: 'A short description of the model'
  },
  start_date: {
    displayName: 'Timestamp',
    description: 'When the model was committed',
    isTimestamp: true
  },
  context_menu: { isStatic: true }
};

@Component({
  selector: 'models4insight-recent-activity-table',
  templateUrl: 'recent-activity-table.component.html',
  styleUrls: ['recent-activity-table.component.scss']
})
export class RecentActivityTableComponent extends AbstractSortableTable
  implements OnInit {

  ngOnInit() {
    this.config = recentActivityTableConfig;
  }
}
