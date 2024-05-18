import { Component } from '@angular/core';
import { faFlag } from '@fortawesome/free-regular-svg-icons';
import {
  faCheck,
  faPencilAlt,
  faSearch
} from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'models4insight-systems-wizard',
  templateUrl: 'systems-wizard.component.html',
  styleUrls: ['systems-wizard.component.scss'],
})
export class SystemsWizardComponent {
  readonly systems = [
    'Azure Active Directory',
    'ElasticSearch',
    'Confluent Kafka',
    'SAP',
    'ServiceNow',
  ];

  readonly faCheck = faCheck;
  readonly faFlag = faFlag;
  readonly faPencilAlt = faPencilAlt;
  readonly faSearch = faSearch;
}
