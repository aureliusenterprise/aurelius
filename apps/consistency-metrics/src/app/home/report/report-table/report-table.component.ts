import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { faPlus } from '@fortawesome/free-solid-svg-icons';
import { AbstractSortableTable, SortableTableShellConfig } from '@models4insight/components';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { AddExemptionModalComponent } from '../add-exemption-modal/add-exemption-modal.component';
import { ExemptionsService } from '../exemptions.service';
import { ReportService } from '../report.service';

@Component({
  selector: 'models4insight-report-table',
  templateUrl: 'report-table.component.html',
  styleUrls: ['report-table.component.scss']
})
export class ReportTableComponent<T extends Dictionary<any> = Dictionary<any>>
  extends AbstractSortableTable<Dictionary<any>>
  implements OnInit {
  readonly faPlus = faPlus;

  @ViewChild(AddExemptionModalComponent, { static: true })
  private readonly addExemptionModal: AddExemptionModalComponent;

  @Input() idColumn: keyof T;

  @Input() isSummary = false;

  constructor(
    private readonly exemptionsService: ExemptionsService,
    private readonly reportService: ReportService,
    private readonly route: ActivatedRoute,
    private readonly router: Router
  ) {
    super();
  }

  ngOnInit() {
    // Whenever the add exemption modal is submitted, create a new exemption
    this.addExemptionModal.submission
      .pipe(untilDestroyed(this))
      .subscribe(({ conceptId, comment, scope }) =>
        this.exemptionsService.createExemption(conceptId, comment, scope)
      );
  }

  addExemption(conceptId: string) {
    this.addExemptionModal.conceptId = conceptId;
    this.addExemptionModal.activate();
  }

  async selectMetricByName(metricName: string) {
    const metricId = await this.reportService.get([
      'metricIdByName',
      metricName
    ]);

    this.router.navigate(['report'], {
      queryParams: { metric: metricId },
      queryParamsHandling: 'merge',
      relativeTo: this.route.parent.parent
    });
  }

  sortByKeyOrder() {
    return 0;
  }

  trackByIndex(row: T, index: number) {
    return index;
  }

  @Input() set config(config: SortableTableShellConfig<T>) {
    this.table.config = {
      copy: {
        isNarrow: true,
        isStatic: true
      },
      ...config,
      except: {
        isNarrow: true,
        isStatic: true
      }
    };
  }

  get config(): SortableTableShellConfig<T> {
    return this.table.config as SortableTableShellConfig<T>;
  }
}
