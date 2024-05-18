import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { faDownload, faProjectDiagram, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { ProjectService } from '@models4insight/services/project';
import { Observable } from 'rxjs';
import { shareReplay, switchMap, tap } from 'rxjs/operators';
import { Report, ReportMetric } from '../../core/report.service';
import { ReportService } from './report.service';

@Component({
  selector: 'models4insight-report',
  templateUrl: 'report.component.html',
  styleUrls: ['report.component.scss']
})
export class ReportComponent implements OnInit {
  readonly faDownload = faDownload;
  readonly faProjectDiagram = faProjectDiagram;
  readonly faSpinner = faSpinner;

  dataset$: Observable<string>;
  isLoadingMetric$: Observable<boolean>;
  metric$: Observable<ReportMetric>;
  metricKey$: Observable<string>;
  metricName$: Observable<string>;
  projectId$: Observable<string>;
  report$: Observable<Report>;

  currentTab: 'metric' | 'exemptions' = 'metric';

  constructor(
    private readonly reportService: ReportService,
    private readonly projectService: ProjectService,
    private readonly route: ActivatedRoute,
    private readonly router: Router
  ) {}

  ngOnInit() {
    this.dataset$ = this.reportService.select('dataset');
    this.isLoadingMetric$ = this.reportService.select('isRetrievingMetric');
    this.metric$ = this.reportService
      .select('metric', { includeFalsy: true })
      .pipe(tap(() => (this.currentTab = 'metric')));
    this.metricKey$ = this.reportService
      .select('metricKey', {
        includeFalsy: true
      })
      .pipe(shareReplay());
    this.metricName$ = this.metricKey$.pipe(
      switchMap(key => this.reportService.select(['metricNameById', key]))
    );
    this.projectId$ = this.projectService.select('projectId');
    this.report$ = this.reportService.select('report', { includeFalsy: true });
  }

  retrieveModel() {
    this.reportService.retrieveModel();
  }

  selectDataset(dataset: string) {
    this.reportService.update({
      description: 'New dataset selected',
      payload: { dataset }
    });
  }

  selectMetric(metric: string) {
    this.router.navigate(['report'], {
      queryParams: { metric },
      queryParamsHandling: 'merge',
      relativeTo: this.route.parent.parent
    });
  }

  sortByKeyOrder() {
    return 0;
  }
}
