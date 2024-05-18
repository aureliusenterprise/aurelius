import { Component } from '@angular/core';
import { PermissionLevel } from '@models4insight/repository';

@Component({
  selector: 'models4insight-project-settings',
  templateUrl: 'project-settings.component.html',
  styleUrls: ['project-settings.component.scss']
})
export class ProjectSettingsComponent {
  readonly PermissionLevel = PermissionLevel;
}
