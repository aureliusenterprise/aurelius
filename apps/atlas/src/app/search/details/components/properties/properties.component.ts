import { Component, OnInit } from '@angular/core';
import { SortableTableShellConfig } from '@models4insight/components';
import { Observable } from 'rxjs';
import { DataForTable, PropertiesService } from './properties.service';

@Component({
    selector: 'models4insight-properties',
    templateUrl: './properties.component.html',
    styleUrls: ['./properties.component.scss'],
    providers: [PropertiesService],
})
export class PropertiesComponent implements OnInit {
    readonly tableConfigProperties: SortableTableShellConfig<DataForTable> = {
        name: { displayName: 'search.details.properties.name', isNarrow: true },
        value: { displayName: 'search.details.properties.value', isNarrow: true },
    };

    dataForTable$: Observable<DataForTable[]>;
    constructor(private readonly propertiesService: PropertiesService) {}

    ngOnInit() {
        this.dataForTable$ = this.propertiesService.select('propertiesList');
    }
}
