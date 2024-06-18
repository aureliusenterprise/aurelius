import { Input, ViewChild, Directive } from '@angular/core';
import { UntypedFormControl } from '@angular/forms';
import {
  ControlShellComponent,
  ControlShellContext,
} from './control-shell.component';

@Directive()
export class AbstractControlShell {
  @ViewChild(ControlShellComponent, { static: true })
  protected readonly shell: ControlShellComponent;

  @Input() set context(context: ControlShellContext) {
    this.shell.context = context;
  }

  get context() {
    return this.shell.context;
  }

  @Input() set control(control: UntypedFormControl) {
    this.shell.control = control;
  }

  get control() {
    return this.shell.control;
  }

  @Input() set isSubmitted(isSubmitted: boolean) {
    this.shell.isSubmitted = isSubmitted;
  }

  get isSubmitted() {
    return this.shell.isSubmitted;
  }
}
