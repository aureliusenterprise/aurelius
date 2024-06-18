import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { HoldableModule } from '@models4insight/directives';
import { DescriptionInputModule } from '../description-input';
import { FuzzySearchInputModule } from '../fuzzy-search-input';
import { ModalModule } from '../modal';
import { SortableTableShellModule } from '../sortable-table-shell';
import { AddGroupMemberComponent } from './add-group-member/add-group-member.component';
import { CreateUserGroupModalComponent } from './create-user-group-modal.component';
import { CreateUserGroupModalService } from './create-user-group-modal.service';
import { GroupMembersComponent } from './group-members/group-members.component';

@NgModule({
  imports: [
    CommonModule,
    FontAwesomeModule,
    DescriptionInputModule,
    FormsModule,
    ReactiveFormsModule,
    ModalModule,
    HoldableModule,
    FuzzySearchInputModule,
    SortableTableShellModule,
  ],
  declarations: [
    AddGroupMemberComponent,
    CreateUserGroupModalComponent,
    GroupMembersComponent,
  ],
  providers: [CreateUserGroupModalService],
  exports: [CreateUserGroupModalComponent],
})
export class CreateUserGroupModalModule {}
