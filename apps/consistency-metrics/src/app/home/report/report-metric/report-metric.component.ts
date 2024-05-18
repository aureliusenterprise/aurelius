import { Component, Input, OnInit } from '@angular/core';
import { faDownload } from '@fortawesome/free-solid-svg-icons';
import { Dictionary } from 'lodash';
import { Observable } from 'rxjs';
import { ReportMetric } from '../../../core/report.service';
import { ReportService } from '../report.service';
import { ViolationsService } from '../violations.service';

@Component({
  selector: 'models4insight-report-metric',
  templateUrl: 'report-metric.component.html',
  styleUrls: ['report-metric.component.scss']
})
export class ReportMetricComponent implements OnInit {
  readonly faDownload = faDownload;

  @Input() metric: ReportMetric;

  bucketMapping$: Observable<Dictionary<string>>;
  dataset$: Observable<string>;
  filteredViolations$: Observable<Dictionary<any>[]>;

  constructor(
    private readonly reportService: ReportService,
    private readonly violationsService: ViolationsService
  ) {}

  ngOnInit() {
    this.bucketMapping$ = this.violationsService.select('bucketMapping');
    this.dataset$ = this.reportService.select('dataset');
    this.filteredViolations$ = this.violationsService.select(
      'filteredViolations'
    );
  }

  sortByKeyOrder() {
    return 0;
  }
}
