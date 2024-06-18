import {
  Component,
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
} from '@angular/core';
import { UntypedFormControl } from '@angular/forms';
import { faSearch, faTimes } from '@fortawesome/free-solid-svg-icons';
import { untilDestroyed } from '@models4insight/utils';
import {
  AbstractControlShell,
  ControlShellContext,
  defaultControlShellContext,
} from '../control-shell';

export interface SimpleSearchInputContext extends ControlShellContext {
  readonly placeholder?: string;
  readonly withSubmitButton?: boolean;
}

export const defaultSimpleSearchInputContext: SimpleSearchInputContext = {
  ...defaultControlShellContext,
  hasIconsRight: true,
  icon: faSearch,
  label: 'Search',
  withSubmitButton: true,
};

@Component({
  selector: 'models4insight-simple-search-input',
  templateUrl: 'simple-search-input.component.html',
  styleUrls: ['simple-search-input.component.scss'],
})
export class SimpleSearchInputComponent
  extends AbstractControlShell
  implements OnInit, OnDestroy
{
  readonly faSearch = faSearch;
  readonly faTimes = faTimes;

  private _query: string;

  @Output() queryChanged: EventEmitter<string> = new EventEmitter<string>();
  @Output() querySubmitted: EventEmitter<string> = new EventEmitter<string>();

  ngOnInit() {
    if (this.context === defaultControlShellContext) {
      this.context = defaultSimpleSearchInputContext;
    }

    this.control = new UntypedFormControl(this.query);

    this.control.valueChanges.pipe(untilDestroyed(this)).subscribe((query) => {
      if (!query) {
        query = null;
      }
      this.query = query;
      this.queryChanged.emit(query);
    });
  }

  ngOnDestroy() {}

  clearQuery() {
    this.control.reset();
    this.query = null;
    this.querySubmitted.emit(this.query);
  }

  submitQuery() {
    this.querySubmitted.next(this.query);
  }

  @Input() set query(query: string) {
    this._query = query;
    if (this.control) {
      this.control.patchValue(query, { emitEvent: false });
    }
  }

  get query() {
    return this._query;
  }
}
