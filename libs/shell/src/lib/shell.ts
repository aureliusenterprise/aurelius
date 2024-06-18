import { Route, Routes } from '@angular/router';
import { AuthenticationGuard } from '@models4insight/authentication';
import { ShellComponent } from './shell.component';

/**
 * Provides helper methods to create routes.
 */
export class Shell {
  /**
   * Creates routes using the shell component and authentication.
   * @param routes The routes to add.
   * @return The new route using shell as the base.
   */
  static childRoutes(routes: Routes, requiresAuth: Boolean = true): Route {
    const route: Route = {
      path: '',
      component: ShellComponent,
      children: routes,
      // Reuse ShellComponent instance when navigating between child views
      data: { reuse: true, hidden: true },
    };

    // If authentication is required, add the AuthenticationGuard
    if (requiresAuth) {
      route['canActivate'] = [AuthenticationGuard];
    }

    return route;
  }
}
