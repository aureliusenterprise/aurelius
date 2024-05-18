import { Component } from '@angular/core';
import { faFlag } from '@fortawesome/free-regular-svg-icons';

@Component({
  selector: 'models4insight-welcome-wizard',
  templateUrl: 'welcome-wizard.component.html',
  styleUrls: ['welcome-wizard.component.scss'],
})
export class WelcomeWizardComponent {
  readonly faFlag = faFlag;
}
