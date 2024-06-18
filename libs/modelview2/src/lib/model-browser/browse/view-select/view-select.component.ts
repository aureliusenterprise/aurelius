import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import {
  AbstractSelectComponent,
  defaultModalContext,
  defaultSelectContext,
  ModalContext,
  Select,
  SelectContext,
  SortableTableShellConfig,
} from '@models4insight/components';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { ModelExplorerService } from '../../../model-explorer.service';
import { ModelviewService } from '../../../model-view.service';
import { ModelView } from '../../../parsers';

const viewSelectSearchModalContext: ModalContext = {
  ...defaultModalContext,
  cancel: 'Close',
  closeOnConfirm: true,
  confirm: null,
  title: 'Choose a view',
};

const viewSelectSearchTableConfig: SortableTableShellConfig<ModelView> = {
  name: { displayName: 'View name', description: 'The name of the view' },
  description: {
    displayName: 'Description',
    description: 'Documentation of the view',
    truncate: 'end',
  },
};

const viewSelectContext: SelectContext = {
  ...defaultSelectContext,
  label: 'View',
  noDataMessage: 'No views available',
  nullInputMessage: 'No view selected',
  searchModalContext: viewSelectSearchModalContext,
  searchTableConfig: viewSelectSearchTableConfig,
};

@Component({
  selector: 'models4insight-view-select',
  templateUrl: 'view-select.component.html',
  styleUrls: ['view-select.component.scss'],
})
export class ViewSelectComponent
  extends AbstractSelectComponent<ModelView>
  implements OnInit
{
  readonly viewSelectContext = viewSelectContext;

  @Output() readonly viewSelected = new EventEmitter<string>();

  views$: Observable<ModelView[]>;

  constructor(
    private readonly modelExplorerService: ModelExplorerService,
    private readonly modelviewService: ModelviewService
  ) {
    super();
  }

  ngOnInit() {
    // Compare views by their id property
    this.comparator = (a, b) => a?.id === b?.id;
    // The control can be empty for validation purposes
    this.control = new Select(false);
    // Show the name of the view in the dropdown menu
    this.displayField = 'name';

    // Whenever a view is selected externally, update the value of the control
    this.modelviewService
      .select('viewId')
      .pipe(
        switchMap((id) => this.modelExplorerService.select(['views', id])),
        untilDestroyed(this)
      )
      .subscribe((view) => {
        this.control.patchValue(view ?? null, { emitEvent: false });
      });

    // Whenever a view is selected, emit an event
    this.control.valueChanges
      .pipe(untilDestroyed(this))
      .subscribe((view) => this.viewSelected.emit(view.id));

    this.views$ = this.modelExplorerService
      .select('views')
      .pipe(map(Object.values));
  }
}
