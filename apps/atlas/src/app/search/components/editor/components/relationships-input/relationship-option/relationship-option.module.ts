import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TranslateModule } from '@ngx-translate/core';
import { BreadCrumbsModule } from '../../../../bread-crumbs/bread-crumbs.module';
import { TypeNameModule } from '../../../../type-name/type-name.module';
import { RelationshipOptionComponent } from './relationship-option.component';

@NgModule({
  imports: [
    CommonModule,
    FontAwesomeModule,
    BreadCrumbsModule,
    TranslateModule.forChild(),
    TypeNameModule,
  ],
  declarations: [RelationshipOptionComponent],
  exports: [RelationshipOptionComponent],
})
export class RelationshipOptionModule {}
