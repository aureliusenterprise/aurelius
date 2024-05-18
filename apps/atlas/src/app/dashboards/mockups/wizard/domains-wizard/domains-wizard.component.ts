import { Component } from '@angular/core';
import { faFlag } from '@fortawesome/free-regular-svg-icons';
import { faCheck, faPencilAlt, faSearch } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'models4insight-domains-wizard',
  templateUrl: 'domains-wizard.component.html',
  styleUrls: ['domains-wizard.component.scss'],
})
export class DomainsWizardComponent {
  readonly departments = [
    'Engineering',
    'Finance',
    'Human Resources',
    'IT',
    'Production',
  ];

  readonly faCheck = faCheck;
  readonly faFlag = faFlag;
  readonly faPencilAlt = faPencilAlt;
  readonly faSearch = faSearch;
}
