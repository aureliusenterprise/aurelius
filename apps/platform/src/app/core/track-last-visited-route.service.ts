import { Injectable, OnDestroy } from '@angular/core';
import { Event, NavigationEnd, Router } from '@angular/router';
import { LastVisitedRouteService } from '@models4insight/services/user-info';
import { untilDestroyed } from '@models4insight/utils';
import { filter } from 'rxjs/operators';

// You can blacklist any set of routes by adding their common path prefix to this array. A prefix always starts with /.
const routesBlacklist = ['/home', '/about'];

function routeNotBlacklisted(event: Event) {
  return (
    event instanceof NavigationEnd &&
    !routesBlacklist.some((s: string) => event.urlAfterRedirects.startsWith(s))
  );
}

/**
 * This service updates the user info whenever the user visits a new route by monitoring the current router state.
 */
// TODO: Add Angular decorator.
@Injectable()
export class TrackLastVisitedRouteService implements OnDestroy {
  constructor(
    private readonly lastVisitedRouteService: LastVisitedRouteService,
    private readonly router: Router
  ) {}

  ngOnDestroy() {}

  init() {
    // Whenever a navigation event fires, update the last visited url if necessary.
    this.router.events
      .pipe(filter(routeNotBlacklisted), untilDestroyed(this))
      .subscribe((event: NavigationEnd) =>
        this.lastVisitedRouteService.updateLastVisitedRoute(
          event.urlAfterRedirects
        )
      );
  }
}
