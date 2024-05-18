import { Injectable } from '@angular/core';
import { getTermById, TermDetails } from '@models4insight/atlas/api';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { switchMap } from 'rxjs/operators';

export interface TermStoreContext {
  readonly guid?: string;
  readonly isRetrievingTerm?: boolean;
  readonly term?: TermDetails;
}

@Injectable()
export class TermService extends BasicStore<TermStoreContext> {
  constructor() {
    super();
    this.init();
  }

  private init() {
    this.select('guid')
      .pipe(
        switchMap(guid => this.handleRetrieveTerm(guid)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  set guid(guid: string) {
    this.update({
      description: 'New term id available',
      payload: { guid }
    });
  }

  @ManagedTask('Retrieving the term definition', {
    isQuiet: true
  })
  @MonitorAsync('isRetrievingTerm')
  private async handleRetrieveTerm(guid: string) {
    const term = await getTermById(guid).toPromise();

    this.update({
      description: 'New term definition available',
      payload: { term }
    });
  }
}
