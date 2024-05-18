import { Component, Input } from '@angular/core';
import {
  faCheckCircle,
  faExclamationTriangle
} from '@fortawesome/free-solid-svg-icons';
import { EntityValidationResult } from '@models4insight/atlas/api';

@Component({
  selector: 'models4insight-gov-quality-display',
  templateUrl: './gov-quality-display.component.html',
  styleUrls: ['./gov-quality-display.component.scss'],
})
export class GovQualityDisplayComponent {
  readonly faCheckCircle = faCheckCircle;
  readonly faExclamationTriangle = faExclamationTriangle;

  @Input() rules: EntityValidationResult;
}
