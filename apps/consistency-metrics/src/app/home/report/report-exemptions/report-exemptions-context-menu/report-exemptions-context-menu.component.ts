import { Component, EventEmitter, Output } from '@angular/core';
import { faEdit } from '@fortawesome/free-regular-svg-icons';
import { faTimes } from '@fortawesome/free-solid-svg-icons';
import { ContextMenuItems } from '@models4insight/components';

@Component({
  selector: 'models4insight-report-exemptions-context-menu',
  templateUrl: 'report-exemptions-context-menu.component.html',
  styleUrls: ['report-exemptions-context-menu.component.scss']
})
export class ReportExemptionsContextMenuComponent {
  @Output() readonly delete: EventEmitter<void> = new EventEmitter<void>();
  @Output() readonly edit: EventEmitter<void> = new EventEmitter<void>();

  readonly menuItems: ContextMenuItems = [
    [
      {
        click: () => this.edit.emit(),
        title: 'Edit',
        icon: faEdit,
        iconModifier: 'has-text-primary'
      }
    ],
    [
      {
        click: () => this.delete.emit(),
        title: 'Delete',
        holdTime: 1,
        icon: faTimes,
        iconModifier: 'has-text-danger'
      }
    ]
  ];
}
