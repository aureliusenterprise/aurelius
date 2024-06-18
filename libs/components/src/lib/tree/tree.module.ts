import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatTreeModule } from '@angular/material/tree';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TreeComponent } from './tree.component';

@NgModule({
  imports: [CommonModule, FontAwesomeModule, MatButtonModule, MatTreeModule],
  declarations: [TreeComponent],
  exports: [TreeComponent],
})
export class TreeModule {}
