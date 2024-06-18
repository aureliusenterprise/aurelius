import { Component, Input } from '@angular/core';
import { ContextMenuItem } from '../context-menu.component';

@Component({
  selector: 'models4insight-context-menu-item',
  templateUrl: 'context-menu-item.component.html',
  styleUrls: ['context-menu-item.component.scss'],
})
export class ContextMenuItemComponent {
  @Input() item: ContextMenuItem;
}
