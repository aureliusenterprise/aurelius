import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TranslateModule } from '@ngx-translate/core';
import { BreadCrumbsComponent } from './bread-crumbs.component';

@NgModule({
  imports: [CommonModule, FontAwesomeModule, TranslateModule.forChild()],
  declarations: [BreadCrumbsComponent],
  exports: [BreadCrumbsComponent]
})
export class BreadCrumbsModule {}
