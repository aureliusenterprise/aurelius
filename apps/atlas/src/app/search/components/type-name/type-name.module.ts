import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TranslateModule } from '@ngx-translate/core';
import { TypeNameComponent } from './type-name.component';

@NgModule({
  imports: [CommonModule, FontAwesomeModule, TranslateModule],
  declarations: [TypeNameComponent],
  exports: [TypeNameComponent],
})
export class TypeNameModule {}
