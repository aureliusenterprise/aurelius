import {
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
  ViewChild,
  ViewEncapsulation,
} from '@angular/core';
import { UntypedFormControl } from '@angular/forms';
import {
  MatDatepicker,
  MatDatepickerInputEvent,
} from '@angular/material/datepicker';
import { faCalendarAlt, faTimes } from '@fortawesome/free-solid-svg-icons';
import { untilDestroyed } from '@models4insight/utils';
import { fromEvent } from 'rxjs';
import {
  AbstractControlShell,
  ControlShellContext,
  defaultControlShellContext,
} from '../control-shell';

export interface DatePickerContext extends ControlShellContext {}

const defaultDatePickerContext: DatePickerContext = {
  icon: faCalendarAlt,
};

@Component({
  selector: 'models4insight-date-picker',
  templateUrl: 'date-picker.component.html',
  styleUrls: ['date-picker.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class DatePickerComponent
  extends AbstractControlShell
  implements OnInit, OnDestroy
{
  /**
   * Emits a timestamp whenever the user selects a date, or null when the selection is empty or does not match a date.
   */
  @Output() readonly dateChanged: EventEmitter<number | null> =
    new EventEmitter<number | null>();

  readonly faCalendarAlt = faCalendarAlt;
  readonly faTimes = faTimes;

  @ViewChild(MatDatepicker, { static: true }) datepicker: MatDatepicker<Date>;
  @ViewChild('dateInput', { static: true }) input: ElementRef<HTMLInputElement>;

  private _date = null;

  ngOnInit() {
    if (this.context === defaultControlShellContext) {
      this.context = defaultDatePickerContext;
    }

    this.control = new UntypedFormControl(this._date);

    // Whenever the selected date changes, emit the corresponding timestamp as an output
    this.control.valueChanges.pipe(untilDestroyed(this)).subscribe((date) => {
      this._date = date;
      const timestamp = date ? date.getTime() : null;
      this.dateChanged.emit(timestamp);
    });

    // Whenever the input field is clicked, open the date picker window
    fromEvent<MouseEvent>(this.input.nativeElement, 'click')
      .pipe(untilDestroyed(this))
      .subscribe((event) => {
        event.preventDefault();
        event.stopPropagation();
        this.datepicker.open();
      });
  }

  ngOnDestroy() {}

  @Input() set date(date: Date | number | null) {
    if (typeof date === 'number') {
      date = new Date(date);
    }

    this._date = date;

    if (this.control) {
      this.control.patchValue(date, { emitEvent: false });
    }
  }

  get date() {
    return this._date;
  }

  clearDate() {
    this.control.reset();
  }

  handleDateChange(event: MatDatepickerInputEvent<Date>) {
    const timestamp = event.value ? event.value.getTime() : null;
    this.dateChanged.emit(timestamp && timestamp > 0 ? timestamp : null);
  }
}
