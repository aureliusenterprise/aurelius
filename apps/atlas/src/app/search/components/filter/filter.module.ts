import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import { CheckBoxComponent } from './check-box/check-box.component';
import { FacetComponent } from './facet/facet.component';
import { FilterComponent } from './filter.component';

@NgModule({
  imports: [CommonModule, ReactiveFormsModule, TranslateModule.forChild()],
  declarations: [CheckBoxComponent, FacetComponent, FilterComponent],
  exports: [FilterComponent]
})
export class FilterModule {}
