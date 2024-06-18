import {
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
  Directive,
} from '@angular/core';
import { UntypedFormGroup } from '@angular/forms';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { AbstractModal } from '../modal';

@Directive()
export abstract class AbstractModalForm<T>
  extends AbstractModal
  implements OnInit, OnDestroy
{
  /** Emits whenever the form is successfully submitted */
  @Output() public readonly submission: EventEmitter<T> = new EventEmitter<T>();

  /** The form and its controls */
  public form: UntypedFormGroup;

  /** Whether or not the form has been submitted */
  public isSubmitted = false;

  protected defaultValue: Dictionary<any> = {};

  private _subject: T;

  constructor(
    /** Describes what sort of object this modal form creates/edits. */
    public readonly category: string
  ) {
    super();
  }

  ngOnInit() {
    // Whenever the modal is confirmed, handle form submission
    this.modal.confirmed
      .pipe(untilDestroyed(this))
      .subscribe(() => this.submit());

    // Whenever the modal is cancelled, clear the form
    this.modal.cancelled
      .pipe(untilDestroyed(this))
      .subscribe(() => this.clear());
  }

  /** Takes the value of the form and transforms it into the desired output format */
  protected abstract createSubmission(): T;

  /** Initializes the form and its controls */
  protected abstract initForm(): UntypedFormGroup;

  /** Resets the form and sets the isSubmitted status to false */
  clear(): void {
    this.isSubmitted = false;
    if (this.subject) {
      this.subject = null;
    }
    this.form.reset(this.defaultValue, { emitEvent: false });
  }

  /** Submits the form and handles output after checking form validity */
  submit(): void {
    this.isSubmitted = true;
    this.form.updateValueAndValidity();
    if (this.form.valid) {
      this.submission.emit(this.createSubmission());
      this.clear();
      this.close();
    }
  }

  @Input()
  set isLoading(state: boolean) {
    this.modal.isLoading = state;
  }

  /** Emits whenever the form is saved */
  @Output()
  get saved() {
    return this.modal.confirmed;
  }

  /** The current subject of the form (if this has a value, the form is in edit mode)*/
  @Input() set subject(subject: T) {
    this._subject = subject;
    this.onSubjectChanged(subject);
  }

  get subject(): T {
    return this._subject;
  }

  protected onSubjectChanged(subject: T) {
    if (subject) {
      this.modal.context.title = `Edit ${this.category}`;
      this.form.patchValue(subject);
    } else {
      this.modal.context.title = `Create a new ${this.category}`;
    }
  }
}
