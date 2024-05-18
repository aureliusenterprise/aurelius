# Shell

The `Shell` module provides the `ShellComponent` which is intended to be used as a wrapper around Models4Insight applications.

## Initialization

You can initialize the `Shell` with the following configurations:

- `appLogo`
  - The runtime path of the logo image
- `appName`
  - The display name of the application
- `appVersion`
  - The version number of the app
- `appCopyright`
  - The copyright year for the app

To initialize the `Shell`, set up your `AppModule` as follows:

```javascript
import { NgModule } from '@angular/core';
import { ShellModule } from '@models4insight/shell';
import { environment } from '../environments/environment';
import { AppComponent } from './app.component';

@NgModule({
  declarations: [AppComponent],
  imports: [
    ShellModule.forRoot({
      appCopyright: environment.copyright,
      appLogoPath: 'assets/app-logo.png',
      appName: 'Example App',
      appVersion: environment.version
    })
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
```

The `ShellModule` is loaded as part of the Models4Insight `core`.

## Usage

The `Shell` uses the Angular `Router` to inject the component at the current route. The following is an example Routing Module for a component including the `Shell`:

```javascript
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Shell } from '@models4insight/shell';
import { ExampleComponent } from './example.component';

const routes: Routes = [
  Shell.childRoutes([
    {
      path: '',
      component: ExampleComponent,
      data: { title: 'Example' }
    }
  ])
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ExampleRoutingModule {}
```

The example routing module imports the Shell, and uses the `childRoutes()` function to wrap the routes array. Any child routes of this route will now also use the Shell.

All routes wrapped by the `Shell` are protected by the `AuthenticationGuard` from `@models4insight/authentication`. This means the user needs to be logged in to Keycloak to access these routes.

## ShellComponent

The `ShellComponent` includes the following subcomponents:

- `HeaderComponent`
  - From left to right, the header includes the following:
    - App logo
    - Primary navigation links. These are derived from the top level routes in the router. See the example below.
    - PWA install/update buttons
    - Link to the documentation
    - Link to account security
    - Logout button
    - App drawer with links to more Models4Insight applications and services.
- `LoadingComponent`
  - Shows a progress bar while the user is navigating to a different route. If your app uses resolvers to pre-load data, this will reassure the user that their actions have registered while the data is loading.
- `PipelineComponent`
  - Shows the progress of each active task registered with the `TaskManagerService` from `@models4insight/task-manager`.
- `FooterComponent`
  - The footer contains the copyright notice, the name of the application, and the version number.

### Header Links

The links in the header are derived from the top-level routes in defined in your `app-routing.module.ts`. You can add data attributes to each route configure each menu entry. See also the example below:

- `title`
  - The name of the page
- `icon`
  - The class name of the icon to use
- `hidden`
  - Whether or not to show the item in the header. True if the item should be hidden.

```javascript
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: '', redirectTo: '/home/welcome', pathMatch: 'full' },
  {
    path: 'home',
    loadChildren: () => import('./home/home.module').then(m => m.HomeModule),
    data: { title: 'Home', icon: 'fas fa-home' }
  },
  {
    path: 'about',
    loadChildren: () => import('./about/about.module').then(m => m.AboutModule),
    data: { title: 'About', icon: 'fas fa-question-circle' }
  },
  {
    path: 'project',
    loadChildren: () =>
      import('./project/project.module').then(m => m.ProjectModule),
    data: { hidden: true }
  },
  // Fallback when no prior route is matched
  { path: '**', redirectTo: '', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
  providers: []
})
export class AppRoutingModule {}
```

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test shell` to execute the unit tests.
