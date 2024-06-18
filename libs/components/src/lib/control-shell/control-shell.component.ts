import { Component, Input } from '@angular/core';
import { UntypedFormControl } from '@angular/forms';
import { IconDefinition } from '@fortawesome/free-solid-svg-icons';

export interface ControlShellContext {
  /** The icon to show as part of the control */
  readonly icon?: IconDefinition;
  /** List of HTML classes that should be applied to the control. Use this to e.g. influence the size of the control */
  readonly inputClasses?: string[];
  /** Whether or not the input has icons to the right of the control */
  readonly hasIconsRight?: boolean;
  /** The text to show as the label of the control */
  readonly label?: string;
  /** The message to show if the control is required and has no value */
  readonly requiredErrorMessage?: string;
}

export const defaultControlShellContext: ControlShellContext = {
  requiredErrorMessage: 'This field is required',
};

@Component({
  selector: 'models4insight-control-shell',
  templateUrl: 'control-shell.component.html',
  styleUrls: ['control-shell.component.scss'],
})
export class ControlShellComponent {
  @Input() context: ControlShellContext = defaultControlShellContext;
  @Input() control: UntypedFormControl;
  @Input() isSubmitted: boolean = false;
}
