import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ColorPickerModule } from 'ngx-color-picker';
import { ColorSquareComponent } from './color-square.component';

@NgModule({
  imports: [ColorPickerModule, CommonModule],
  declarations: [ColorSquareComponent],
  exports: [ColorSquareComponent],
})
export class ColorSquareModule {}
