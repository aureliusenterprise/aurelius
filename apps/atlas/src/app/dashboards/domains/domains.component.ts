import { Component, OnInit } from '@angular/core';
import { DomainForDashboard } from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import { DomainsService } from './domains.service';

@Component({
  selector: 'models4insight-domains',
  templateUrl: './domains.component.html',
  styleUrls: ['./domains.component.scss'],
  providers: [DomainsService]
})
export class DomainsComponent implements OnInit {
  totalNumberOfDataDomains$: Observable<number>
  totalNumberOfActiveDomains$: Observable<number>
  listOfDashboardDomains$: Observable<DomainForDashboard[]>
  isRetrivingDomainsForDashboards$: Observable<boolean>

  constructor(private readonly domainsService: DomainsService) { }

  ngOnInit() {
    this.listOfDashboardDomains$ = this.domainsService.select('listOfDashboardDomains');
    this.isRetrivingDomainsForDashboards$ = this.domainsService.select('isRetrivingDashboardInformation');
    this.totalNumberOfDataDomains$ = this.domainsService.select('totalNumberOfDataDomains');
    this.totalNumberOfActiveDomains$ = this.domainsService.select('totalNumberOfActiveDomains')
  }
}
