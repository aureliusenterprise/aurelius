import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { SortableTableShellModule } from '@models4insight/components';
import { TranslateModule } from '@ngx-translate/core';
import { PropertiesComponent } from './properties.component';
import { PropertiesItemComponent } from './properties-item/properties-item.component';
@NgModule({
  imports: [CommonModule, SortableTableShellModule, TranslateModule.forChild()],
  declarations: [PropertiesComponent, PropertiesItemComponent],
  exports: [PropertiesComponent, PropertiesItemComponent]
})
export class PropertiesModule { }
