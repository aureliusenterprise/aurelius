import { Input, OnDestroy, ViewChild, Directive } from '@angular/core';
import { Dictionary } from 'lodash';
import { Select } from './select';
import { SelectComponent, SelectContext } from './select.component';

@Directive()
export class AbstractSelectComponent<
  T extends Dictionary<any> = Dictionary<any>
> implements OnDestroy
{
  @ViewChild(SelectComponent, { static: true })
  protected readonly select: SelectComponent<T>;

  ngOnDestroy() {}

  @Input() set context(context: SelectContext) {
    this.select.context = context;
  }

  get context() {
    return this.select.context;
  }

  @Input() set comparator(comparator: (a: T, b: T) => boolean) {
    this.select.comparator = comparator;
  }

  get comparator() {
    return this.select.comparator;
  }

  @Input() set control(control: Select) {
    this.select.control = control;
  }

  get control() {
    return this.select.control;
  }

  @Input() set data(data: T[]) {
    this.select.data = data;
  }

  get data() {
    return this.select.data;
  }

  @Input() set displayField(displayField: keyof T) {
    this.select.displayField = displayField;
  }

  get displayField() {
    return this.select.displayField;
  }

  @Input() set isDisabled(disabled: boolean) {
    this.select.isDisabled = disabled;
  }

  get isDisabled() {
    return this.select.isDisabled;
  }

  @Input() set isSubmitted(isSubmitted: boolean) {
    this.select.isSubmitted = isSubmitted;
  }

  get isSubmitted() {
    return this.select.isSubmitted;
  }
}
