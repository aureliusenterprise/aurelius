import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { BranchSelectModule, ContextMenuModule, CreateBranchModalModule, DescriptionInputModule, SortableTableShellModule } from '@models4insight/components';
import { BranchPermissionModule, ProjectPermissionModule } from '@models4insight/permissions';
import { TranslateModule } from '@ngx-translate/core';
import { BranchMergeRoutingModule } from './branch-merge-routing.module';
import { BranchMergeComponent } from './branch-merge.component';
import { BranchMergeGuard } from './branch-merge.guard';
import { BranchMergeService } from './branch-merge.service';
import { BranchesTableContextMenuComponent } from './branches-table/branches-table-context-menu/branches-table-context-menu.component';
import { BranchesTableComponent } from './branches-table/branches-table.component';

@NgModule({
  imports: [
    CommonModule,
    TranslateModule,
    BranchMergeRoutingModule,
    ReactiveFormsModule,
    ProjectPermissionModule,
    BranchPermissionModule,
    BranchSelectModule,
    DescriptionInputModule,
    ContextMenuModule,
    CreateBranchModalModule,
    SortableTableShellModule,
  ],
  declarations: [
    BranchMergeComponent,
    BranchesTableComponent,
    BranchesTableContextMenuComponent
  ],
  providers: [BranchMergeGuard, BranchMergeService]
})
export class BranchMergeModule {}
