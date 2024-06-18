import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { HoldableModule } from '@models4insight/directives';
import { ContextMenuItemComponent } from './context-menu-item/context-menu-item.component';
import { ContextMenuComponent } from './context-menu.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

@NgModule({
  imports: [CommonModule, FontAwesomeModule, HoldableModule],
  declarations: [ContextMenuComponent, ContextMenuItemComponent],
  exports: [ContextMenuComponent],
})
export class ContextMenuModule {}
