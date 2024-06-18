import { Injectable, OnDestroy } from '@angular/core';
import {
  Event as RouterNavigationEvent,
  NavigationCancel,
  NavigationEnd,
  NavigationError,
  NavigationStart,
  Route,
  Router,
} from '@angular/router';
import { SwUpdate } from '@angular/service-worker';
import { AuthenticationService } from '@models4insight/authentication';
import { Logger } from '@models4insight/logger';
import { BasicStore, StoreService } from '@models4insight/redux';
import { untilDestroyed } from '@models4insight/utils';
import { combineLatest, ConnectableObservable, fromEvent, Subject } from 'rxjs';
import {
  concatMap,
  exhaustMap,
  filter,
  pairwise,
  publish,
  switchMap,
  tap,
} from 'rxjs/operators';

const log = new Logger('ShellService');

/**
 * The BeforeInstallPromptEvent is fired at the Window.onbeforeinstallprompt handler
 * before a user is prompted to "install" a web site to a home screen on mobile.
 *
 * @deprecated Only supported on Chrome and Android Webview.
 */
interface BeforeInstallPromptEvent extends Event {
  /**
   * Returns an array of DOMString items containing the platforms on which the event was dispatched.
   * This is provided for user agents that want to present a choice of versions to the user such as,
   * for example, "web" or "play" which would allow the user to chose between a web version or
   * an Android version.
   */
  readonly platforms: Array<string>;

  /**
   * Returns a Promise that resolves to a DOMString containing either "accepted" or "dismissed".
   */
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;

  /**
   * Allows a developer to show the install prompt at a time of their own choosing.
   * This method returns a Promise.
   */
  prompt(): Promise<void>;
}

export interface ShellStoreContext {
  readonly isAppInstallable?: boolean;
  readonly isNavigating?: boolean;
  readonly isUpdateAvailable?: boolean;
  readonly previousRoute?: string;
  readonly routes?: Route[];
}

export const shellServiceDefaultState: ShellStoreContext = {
  isAppInstallable: false,
  isNavigating: false,
  isUpdateAvailable: false,
};

// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
// TODO: Add Angular decorator.
@Injectable({
  providedIn: 'root',
})
export class ShellService
  extends BasicStore<ShellStoreContext>
  implements OnDestroy
{
  private readonly applyUpdate$: Subject<void> = new Subject<void>();
  private readonly installApp$: Subject<void> = new Subject<void>();
  private readonly updateToken$: Subject<void> = new Subject<void>();

  constructor(
    private readonly authenticationService: AuthenticationService,
    private readonly router: Router,
    private readonly swUpdate: SwUpdate,
    storeService: StoreService
  ) {
    super({
      defaultState: shellServiceDefaultState,
      name: 'ShellService',
      storeService,
    });
    this.init();
  }

  ngOnDestroy() {}

  private init() {
    // These are the top level routes of the application which are not configured to be hidden and are not redirects
    const routes = this.router.config.filter(
      (route) =>
        route.redirectTo === undefined && !(route.data && route.data.hidden)
    );

    // Update the store with the routes found
    this.update({
      description: 'New top level routes available',
      payload: { routes },
    });

    // Whenever update token fires, update the authentication token
    this.updateToken$
      .pipe(
        exhaustMap(() => this.authenticationService.updateToken()),
        untilDestroyed(this)
      )
      .subscribe(() => log.debug('Authentication token successfully updated'));

    // Intercept router navigation events
    this.router.events
      .pipe(untilDestroyed(this))
      .subscribe((event) => this.navigationInterceptor(event));

    // Track the previous page route for go back functionality
    this.router.events
      .pipe(
        filter((event) => event instanceof NavigationEnd),
        pairwise(),
        concatMap(([previousRoute, currentRoute]) =>
          this.handleTrackPreviousRoute(
            previousRoute as NavigationEnd,
            currentRoute as NavigationEnd
          )
        ),
        untilDestroyed(this)
      )
      .subscribe();

    // Handle service worker triggers if the service worker is enabled
    if (this.swUpdate.isEnabled) {
      // Check whether an update is available
      this.swUpdate.versionUpdates
        .pipe(
          filter((event) => event.type === 'VERSION_READY'),
          untilDestroyed(this)
        )
        .subscribe((event) =>
          this.update({
            description: 'Service worker update available',
            payload: {
              isUpdateAvailable: !!event,
            },
          })
        );

      // When the user applies an update, activate the update and reload the page
      this.applyUpdate$
        .pipe(
          exhaustMap(() => this.swUpdate.activateUpdate()),
          untilDestroyed(this)
        )
        .subscribe(() => document.location.reload());

      // Check for updates on startup
      this.swUpdate.checkForUpdate();

      const beforeInstallPrompt$ = fromEvent<BeforeInstallPromptEvent>(
        window,
        'beforeinstallprompt'
      ).pipe(publish()) as ConnectableObservable<BeforeInstallPromptEvent>;

      beforeInstallPrompt$
        .pipe(
          tap(() =>
            this.update({
              description: 'App is installable',
              payload: {
                isAppInstallable: true,
              },
            })
          ),
          switchMap((event) => event.userChoice),
          tap(() =>
            this.update({
              description: 'User decided whether or not to install the app',
              payload: {
                isAppInstallable: false,
              },
            })
          ),
          untilDestroyed(this)
        )
        .subscribe((decision) =>
          log.debug(`App install outcome: ${decision.outcome}`)
        );

      // Prompt the user to install the app
      combineLatest([beforeInstallPrompt$, this.installApp$])
        .pipe(
          exhaustMap(([event]) => event.prompt()),
          untilDestroyed(this)
        )
        .subscribe(() => log.debug('User prompted to intall the app'));

      beforeInstallPrompt$.connect();
    }
  }

  applyUpdate() {
    this.applyUpdate$.next();
  }

  installApp() {
    this.installApp$.next();
  }

  updateToken() {
    this.updateToken$.next();
  }

  private async handleTrackPreviousRoute(
    previousRoute: NavigationEnd,
    currentRoute: NavigationEnd
  ) {
    const [previousPath] = previousRoute.urlAfterRedirects.split('?'),
      [currentPath] = currentRoute.urlAfterRedirects.split('?');

    if (previousPath === currentPath) return;

    this.update({
      description: 'New previous route available',
      payload: { previousRoute: previousRoute.urlAfterRedirects },
    });
  }

  private navigationInterceptor(event: RouterNavigationEvent) {
    if (event instanceof NavigationStart) {
      this.update({
        description: 'Navigation start',
        payload: {
          isNavigating: true,
        },
      });
    } else if (
      event instanceof NavigationEnd ||
      event instanceof NavigationCancel ||
      event instanceof NavigationError
    ) {
      this.update({
        description: 'Navigation complete',
        payload: {
          isNavigating: false,
        },
      });
    }
  }
}
