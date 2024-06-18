import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ModalModule } from '../modal';
import { UserSearchInputModule } from '../user-search-input';
import { UserSearchModalComponent } from './user-search-modal.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

@NgModule({
  imports: [
    CommonModule,
    FontAwesomeModule,
    ModalModule,
    UserSearchInputModule,
  ],
  declarations: [UserSearchModalComponent],
  exports: [UserSearchModalComponent],
})
export class UserSearchModalModule {}
