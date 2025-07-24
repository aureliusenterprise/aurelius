// import { Component, OnInit } from '@angular/core';
// import { SortableTableShellConfig } from '@models4insight/components';
// import { Observable } from 'rxjs';
// import { DataForTable, PropertiesService } from './properties.service';

// const tableConfigProperties: SortableTableShellConfig<DataForTable> = {
//   name: { displayName: 'Key', isNarrow: true },
//   value: { displayName: 'Value', isNarrow: true }
// };

// @Component({
//   selector: 'models4insight-properties',
//   templateUrl: './properties.component.html',
//   styleUrls: ['./properties.component.scss'],
//   providers: [PropertiesService]
// })
// export class PropertiesComponent implements OnInit {
//   readonly tableConfigProperties = tableConfigProperties;

//   dataForTable$: Observable<DataForTable[]>;

//   isCollapsed = true; // collapsed by default

//   constructor(
//     private readonly propertiesService: PropertiesService
//   ) { }

//   ngOnInit() {
//     this.dataForTable$ = this.propertiesService.select('propertiesList');
//   }

// }

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
  // Remove static Properties headers
  setTimeout(() => {
    const headers = document.querySelectorAll('h3.title.is-3');
    headers.forEach(header => {
      if (header.textContent?.trim() === 'Properties') {
        (header as HTMLElement).style.display = 'none';
      }
    });
  });
}
}
