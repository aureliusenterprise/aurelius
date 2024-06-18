import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { RepositoryModule } from '@models4insight/repository';
import { UserSearchInputComponent } from './user-search-input.component';

@NgModule({
  imports: [CommonModule, RepositoryModule],
  declarations: [UserSearchInputComponent],
  exports: [UserSearchInputComponent],
})
export class UserSearchInputModule {}
