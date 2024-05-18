import { Component } from '@angular/core';
import { faFlag } from '@fortawesome/free-regular-svg-icons';
import { faCheck, faSearch } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'models4insight-summary-wizard',
  templateUrl: 'summary-wizard.component.html',
  styleUrls: ['summary-wizard.component.scss'],
})
export class SummaryWizardComponent {
  readonly faCheck = faCheck;
  readonly faFlag = faFlag;
  readonly faSearch = faSearch;

  readonly departments = ['Finance', 'Human Resources'];
  readonly systems = ['ElasticSearch', 'SAP', 'ServiceNow'];
}
