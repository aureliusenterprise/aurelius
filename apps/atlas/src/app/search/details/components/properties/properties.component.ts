import { Component, OnInit, AfterViewInit } from '@angular/core';
import { SortableTableShellConfig } from '@models4insight/components';
import { Observable } from 'rxjs';
import { DataForTable, PropertiesService } from './properties.service';

const tableConfigProperties: SortableTableShellConfig<DataForTable> = {
  name: { displayName: 'Key', isNarrow: true },
  value: { displayName: 'Value', isNarrow: true }
};

@Component({
  selector: 'models4insight-properties',
  templateUrl: './properties.component.html',
  styleUrls: ['./properties.component.scss'],
  providers: [PropertiesService]
})
export class PropertiesComponent implements OnInit, AfterViewInit {
  readonly tableConfigProperties = tableConfigProperties;

  dataForTable$: Observable<DataForTable[]>;
  isCollapsed = true; // collapsed by default

  constructor(
    private readonly propertiesService: PropertiesService
  ) { }

  ngOnInit() {
    this.dataForTable$ = this.propertiesService.select('propertiesList');
  }
ngAfterViewInit() {
  // Only hide parent static headers, not our own
  setTimeout(() => {
    const parentBox = document.querySelector('#properties-details');
    if (parentBox) {
      const headers = parentBox.querySelectorAll('h3.title.is-3');
      headers.forEach(header => {
        // Check if this header is a direct child of the parent box (not our header)
        if (header.parentElement === parentBox && header.textContent?.trim() === 'Properties') {
          (header as HTMLElement).style.display = 'none';
        }
      });
    }
  });
}
}
