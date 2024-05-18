import { Component, Input } from '@angular/core';
import { faCheck, faExclamationCircle, faExclamationTriangle, faInfoCircle } from '@fortawesome/free-solid-svg-icons';
import { ValidationResult, ValidationSeverityType } from '../extractor-types';

@Component({
  selector: 'models4insight-validation-result',
  templateUrl: 'validation-result.component.html',
  styleUrls: ['validation-result.component.scss']
})
export class ValidationResultComponent {
  readonly faCheck = faCheck;
  readonly faExclamationCircle = faExclamationCircle;
  readonly faExclamationTriangle = faExclamationTriangle;
  readonly faInfoCircle = faInfoCircle;

  readonly ValidationSeverityType = ValidationSeverityType;

  maxSeverity: ValidationSeverityType;
  tooltip: string;

  @Input() set errors(errors: ValidationResult | ValidationResult[]) {
    if (!Array.isArray(errors)) {
      errors = [errors];
    }
    this.maxSeverity = this.calculateMaxSeverity(errors);
    this.tooltip = this.buildTooltip(errors);
  }

  private calculateMaxSeverity(errors: ValidationResult[]) {
    if (!errors.length) {
      return null;
    }
    const severityMap = errors.map(error => error.type);
    if (severityMap.includes(ValidationSeverityType.ERROR)) {
      return ValidationSeverityType.ERROR;
    }
    if (severityMap.includes(ValidationSeverityType.WARNING)) {
      return ValidationSeverityType.WARNING;
    } else {
      return ValidationSeverityType.INFO;
    }
  }

  private buildTooltip(errors: ValidationResult[]) {
    return errors.map((error, index) => `${index + 1}. ${error.description}`).join('\n');
  }
}
