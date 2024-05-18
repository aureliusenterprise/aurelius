import { Injectable } from '@angular/core';
import { DomainForDashboard, getDashboard, ListOfDomainsForDashboard } from '@models4insight/atlas/api';
import { BasicStore } from '@models4insight/redux';

export interface DashboardDomainsContext {
  readonly isRetrivingDashboardInformation: boolean,
  readonly listOfDashboardDomains?: DomainForDashboard[]
  readonly totalNumberOfDataDomains?: number
  readonly totalNumberOfActiveDomains?: number
}

const dashboardDomainsDefaultContext: DashboardDomainsContext = {
  isRetrivingDashboardInformation: true
};

@Injectable()
export class DomainsService extends BasicStore<DashboardDomainsContext> {
  constructor() {
    super({ name: 'DashBoardDomain', defaultState: dashboardDomainsDefaultContext });
    this.init();
  }

  private init() {
    this.getAllDomainsForDashboard();
  }

  private async getAllDomainsForDashboard() {
    const results: ListOfDomainsForDashboard = await getDashboard().toPromise()

    const listOfDomains = Object.values(results.domains).sort(function (a, b) {
      return a.name.localeCompare(b.name);
    })
    const totalNumberOfDataDomains = results.totalNumberOfDomains
    const numberOfActiveDomains = results.totalNumberOfActiveDomains

    this.update({
      description: "New set of Dashboards available",
      payload: {
        isRetrivingDashboardInformation: false,
        listOfDashboardDomains: listOfDomains,
        totalNumberOfDataDomains: totalNumberOfDataDomains,
        totalNumberOfActiveDomains: numberOfActiveDomains
      }
    })
  }
}


