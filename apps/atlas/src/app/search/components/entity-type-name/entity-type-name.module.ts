import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { TypeNameModule } from '../type-name/type-name.module';
import { EntityTypeNameComponent } from './entity-type-name.component';

@NgModule({
  imports: [CommonModule, TypeNameModule],
  declarations: [EntityTypeNameComponent],
  exports: [EntityTypeNameComponent],
})
export class EntityTypeNameModule {}
