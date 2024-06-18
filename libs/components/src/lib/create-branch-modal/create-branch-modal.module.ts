import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { HoldableModule } from '@models4insight/directives';
import { BranchNameInputModule } from '../branch-name-input';
import { DescriptionInputModule } from '../description-input';
import { FuzzySearchInputModule } from '../fuzzy-search-input';
import { ModalModule } from '../modal/modal.module';
import { PermissionSelectModule } from '../permission-select';
import { SortableTableShellModule } from '../sortable-table-shell';
import { AddBranchMemberComponent } from './add-branch-member/add-branch-member.component';
import { BranchMembersComponent } from './branch-members/branch-members.component';
import { CreateBranchModalComponent } from './create-branch-modal.component';
import { CreateBranchModalService } from './create-branch-modal.service';

@NgModule({
  imports: [
    CommonModule,
    FontAwesomeModule,
    BranchNameInputModule,
    ModalModule,
    FormsModule,
    ReactiveFormsModule,
    DescriptionInputModule,
    FuzzySearchInputModule,
    HoldableModule,
    PermissionSelectModule,
    SortableTableShellModule,
  ],
  declarations: [
    AddBranchMemberComponent,
    BranchMembersComponent,
    CreateBranchModalComponent,
  ],
  providers: [CreateBranchModalService],
  exports: [CreateBranchModalComponent],
})
export class CreateBranchModalModule {}
