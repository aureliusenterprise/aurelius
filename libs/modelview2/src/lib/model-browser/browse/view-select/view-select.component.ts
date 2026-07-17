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
import { TranslateService } from '@ngx-translate/core';
import { Observable } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { ModelExplorerService } from '../../../model-explorer.service';
import { ModelviewService } from '../../../model-view.service';
import { ModelView } from '../../../parsers';

const viewSelectSearchModalContext: ModalContext = {
    ...defaultModalContext,
    cancel: 'modelview2.modelBrowser.browse.viewSelect.cancel',
    closeOnConfirm: true,
    confirm: null,
    title: 'modelview2.modelBrowser.browse.viewSelect.title',
};

const viewSelectSearchTableConfig: SortableTableShellConfig<ModelView> = {
    name: {
        displayName: 'modelview2.modelBrowser.browse.viewSelect.nameDisplayName',
        description: 'modelview2.modelBrowser.browse.viewSelect.nameDescription',
    },
    description: {
        displayName: 'modelview2.modelBrowser.browse.viewSelect.descriptionDisplayName',
        description: 'modelview2.modelBrowser.browse.viewSelect.descriptionDescription',
        truncate: 'end',
    },
};

@Component({
    selector: 'models4insight-view-select',
    templateUrl: 'view-select.component.html',
    styleUrls: ['view-select.component.scss'],
})
export class ViewSelectComponent extends AbstractSelectComponent<ModelView> implements OnInit {
    viewSelectContext!: SelectContext;

    @Output() readonly viewSelected = new EventEmitter<string>();

    views$: Observable<ModelView[]>;

    constructor(
        private readonly modelExplorerService: ModelExplorerService,
        private readonly modelviewService: ModelviewService,
        private readonly translateService: TranslateService,
    ) {
        super();
    }

    ngOnInit() {
        this.viewSelectContext = {
            ...defaultSelectContext,
            label: this.translateService.instant('modelview2.modelBrowser.browse.viewSelect.label'),
            noDataMessage: this.translateService.instant('modelview2.modelBrowser.browse.viewSelect.noDataMessage'),
            nullInputMessage: this.translateService.instant(
                'modelview2.modelBrowser.browse.viewSelect.nullInputMessage',
            ),
            searchModalContext: viewSelectSearchModalContext,
            searchTableConfig: viewSelectSearchTableConfig,
        };

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
                untilDestroyed(this),
            )
            .subscribe((view) => {
                this.control.patchValue(view ?? null, { emitEvent: false });
            });

        // Whenever a view is selected, emit an event
        this.control.valueChanges.pipe(untilDestroyed(this)).subscribe((view) => this.viewSelected.emit(view.id));

        this.views$ = this.modelExplorerService.select('views').pipe(map(Object.values));
    }
}
