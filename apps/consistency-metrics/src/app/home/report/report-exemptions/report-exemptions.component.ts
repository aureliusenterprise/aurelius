import { Component, Input, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { SortableTableShellConfig } from '@models4insight/components';
import { MetricExemption } from '@models4insight/repository';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ReportMetric } from '../../../core/report.service';
import { AddExemptionModalComponent, AddExemptionModalFormContext } from '../add-exemption-modal/add-exemption-modal.component';
import { ExemptionsService } from '../exemptions.service';
import { ReportService } from '../report.service';
import { ReportExemptionsService } from './report-exemptions.service';

const defaultExemptionsTableConfig: SortableTableShellConfig = {};

@Component({
  selector: 'models4insight-report-exemptions',
  templateUrl: 'report-exemptions.component.html',
  styleUrls: ['report-exemptions.component.scss']
})
export class ReportExemptionsComponent implements OnInit, OnDestroy {
  exemptions$: Observable<MetricExemption[]>;

  exemptionsTableConfig: SortableTableShellConfig = defaultExemptionsTableConfig;

  @ViewChild(AddExemptionModalComponent, { static: true })
  private readonly addExemptionModal: AddExemptionModalComponent;

  @Input() metric: ReportMetric;

  constructor(
    private readonly reportService: ReportService,
    private readonly exemptionsService: ExemptionsService,
    private readonly reportExemptionsService: ReportExemptionsService
  ) {}

  ngOnInit() {
    this.exemptions$ = this.reportExemptionsService.exemptions;

    // Whenever an exemption is modified, save it
    this.addExemptionModal.submission
      .pipe(untilDestroyed(this))
      .subscribe(exemption =>
        this.exemptionsService.createExemption(
          exemption.conceptId,
          exemption.comment,
          exemption.scope,
          exemption.id
        )
      );

    // Whenever a new dataset is selected, generate an extended table config for the exemptions table
    this.reportService
      .select('dataset')
      .pipe(
        map(dataset =>
          this.metric
            ? this.extendTableConfig(this.metric['data'][dataset].config.data)
            : null
        )
      )
      .subscribe(
        extendedTableConfig =>
          (this.exemptionsTableConfig = extendedTableConfig)
      );
  }

  ngOnDestroy() {}

  editExemption(exemption: any) {
    const subject: AddExemptionModalFormContext = {
      id: exemption.exemption_id,
      conceptId: exemption.concept_id,
      scope: {
        type: exemption.version
          ? 'version'
          : exemption.branch === '*'
          ? 'project'
          : 'branch'
      } as any,
      comment: exemption.comment
    };
    this.addExemptionModal.subject = subject;
    this.addExemptionModal.activate();
  }

  removeExemption(exemption: any) {
    this.exemptionsService.removeExemption(exemption.exemption_id);
  }

  sortByKeyOrder() {
    return 0;
  }

  private extendTableConfig(config: SortableTableShellConfig) {
    return {
      copy_button: {
        isNarrow: true,
        isStatic: true
      },
      ...config,
      comment: {
        displayName: 'Description',
        description: 'A description of the exemption'
      },
      scope: {
        displayName: 'Scope',
        description: 'The scope of the exemption',
        isStatic: true
      },
      context_menu: {
        isNarrow: true,
        isStatic: true
      }
    };
  }
}
