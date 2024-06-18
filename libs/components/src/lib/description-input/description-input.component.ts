import { Component, OnInit } from '@angular/core';
import {
  AbstractControlShell,
  ControlShellContext,
  defaultControlShellContext,
} from '../control-shell';

export interface DescriptionInputContext extends ControlShellContext {
  readonly placeholder: string;
}

export const defaultDescriptionInputContext: DescriptionInputContext = {
  ...defaultControlShellContext,
  label: 'Description',
  placeholder: 'Description',
  requiredErrorMessage: 'Please provide a description',
};

@Component({
  selector: 'models4insight-description-input',
  templateUrl: 'description-input.component.html',
  styleUrls: ['description-input.component.scss'],
})
export class DescriptionInputComponent
  extends AbstractControlShell
  implements OnInit
{
  ngOnInit() {
    if (this.context === defaultControlShellContext) {
      this.context = defaultDescriptionInputContext;
    }
  }
}
