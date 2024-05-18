import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { PeopleComponent } from './people.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

@NgModule({
  imports: [CommonModule, FontAwesomeModule],
  declarations: [PeopleComponent],
  exports: [PeopleComponent]
})
export class PeopleModule {}
