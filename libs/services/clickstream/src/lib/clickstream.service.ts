import { Inject, Injectable } from '@angular/core';
import { NavigationEnd, Router, RouterEvent } from '@angular/router';
import { AuthenticationService } from '@models4insight/authentication';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import {
  ClickstreamEvent,
  logClickstreamEvent,
} from '@models4insight/repository';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { now } from 'lodash';
import { concatMap, filter } from 'rxjs/operators';
import {
  ClickstreamConfig,
  ClickstreamConfigService,
} from './clickstream-config.service';

function eventIsNavigationEnd(event: RouterEvent): event is NavigationEnd {
  return event instanceof NavigationEnd;
}

export interface ClickstreamStoreContext {
  readonly isLoggingClickstreamEvent?: boolean;
}

@Injectable()
export class ClickstreamService extends BasicStore<ClickstreamStoreContext> {
  constructor(
    private readonly authenticationService: AuthenticationService,
    @Inject(ClickstreamConfigService)
    private readonly config: ClickstreamConfig,
    private readonly router: Router,
    storeService: StoreService
  ) {
    super({ name: 'ClickstreamService', storeService });
  }

  init() {
    if (this.config.enabled) {
      this.router.events
        .pipe(
          filter(event => eventIsNavigationEnd(event as RouterEvent)),
          concatMap((event) => this.logClickstreamEvent(event as NavigationEnd)),
          untilDestroyed(this)
        )
        .subscribe();
    }
  }

  @ManagedTask('Logging the clickstream event', { isQuiet: true })
  @MonitorAsync('isLoggingClickstreamEvent')
  private async logClickstreamEvent(event: NavigationEnd) {
    const isAuthenticated = await this.authenticationService.get(
      'isAuthenticated'
    );

    if (!isAuthenticated) return;

    const userid = await this.authenticationService.get([
      'credentials',
      'username',
    ]);

    const clickstreamEvent: ClickstreamEvent = {
      app: this.config.app,
      timestamp: now(),
      url: event.urlAfterRedirects,
      userid,
    };

    return logClickstreamEvent(clickstreamEvent).toPromise();
  }
}
