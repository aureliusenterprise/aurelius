import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { PeopleComponent } from './people.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TranslateModule } from '@ngx-translate/core';

@NgModule({
    imports: [CommonModule, FontAwesomeModule, TranslateModule.forChild()],
    declarations: [PeopleComponent],
    exports: [PeopleComponent],
})
export class PeopleModule {}
