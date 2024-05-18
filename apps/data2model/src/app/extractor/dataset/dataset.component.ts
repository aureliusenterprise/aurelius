import { Component, OnInit } from '@angular/core';
import { SortableTableShellConfig } from '@models4insight/components';
import { Observable } from 'rxjs';
import { ExtractorDatasetEntry } from '../extractor-types';
import { ExtractorService } from '../extractor.service';
import { DatasetService } from './dataset.service';

@Component({
  selector: 'models4insight-dataset',
  templateUrl: 'dataset.component.html',
  styleUrls: ['dataset.component.scss']
})
export class DatasetComponent implements OnInit {
  dataset$: Observable<ExtractorDatasetEntry[]>;
  tableConfig$: Observable<SortableTableShellConfig>;

  constructor(
    private datasetService: DatasetService,
    private extractorService: ExtractorService
  ) {}

  ngOnInit() {
    this.dataset$ = this.extractorService.select('currentDataset');
    this.tableConfig$ = this.datasetService.select('tableConfig');
  }
}
