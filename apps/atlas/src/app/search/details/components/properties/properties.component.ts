import { Component, OnInit } from '@angular/core';
import { SortableTableShellConfig } from '@models4insight/components';
import { TranslateService } from '@ngx-translate/core';
import { Observable } from 'rxjs';
import { DataForTable, PropertiesService } from './properties.service';

const createTableConfigProperties = (translateService: TranslateService): SortableTableShellConfig<DataForTable> => ({
    name: { displayName: translateService.instant('search.details.properties.name'), isNarrow: true },
    value: { displayName: translateService.instant('search.details.properties.value'), isNarrow: true },
});

@Component({
    selector: 'models4insight-properties',
    templateUrl: './properties.component.html',
    styleUrls: ['./properties.component.scss'],
    providers: [PropertiesService],
})
export class PropertiesComponent implements OnInit {
    readonly tableConfigProperties: SortableTableShellConfig<DataForTable>;

    dataForTable$: Observable<DataForTable[]>;
    constructor(
        private readonly propertiesService: PropertiesService,
        private readonly translateService: TranslateService,
    ) {
        this.tableConfigProperties = createTableConfigProperties(translateService);
    }

    ngOnInit() {
        this.dataForTable$ = this.propertiesService.select('propertiesList');
    }
}
