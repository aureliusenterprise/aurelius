# Version

This package implements the `VersionModule`, which provides several means of retrieving the current version of the app, as well as connected services.

The current version of the app is a combination of the `package.json` release number and the git hash at build time. Additionally, the version includes a postfix indicating whether or not the current build is running in development mode.

## Initialization

While the release number and git hash are static values, production mode is determined via a configuration parameter. To initialize the `VersionModule`, please configure your `AppModule` as follows:

```javascript
import { NgModule } from '@angular/core';
import { VersionModule } from '@models4insight/version';
import { environment } from '../environments/environment';
import { AppComponent } from './app.component';

@NgModule({
  declarations: [AppComponent],
  imports: [VersionModule.forRoot({ production: environment.production })],
  bootstrap: [AppComponent]
})
export class AppModule {}
```

The `VersionModule` is loaded as part of the Models4Insight `core`.

## Usage

The `VersionModule` provides the `VersionService`, which exposes the following:

- `appVersion`: The version string of the application
- `getRepositoryVersion()`: Returns the version string of the connected repository back end
- `getVersionDescriptor()`: Returns an object which represents the version of the app and connected services

You can inject the `VersionService` wherever you need version information.

Furthermore, the version descriptor is available from the browser console.
By running `version()` in the browser console, the application will retrieve and print the version descriptor of the app itself, as well as any connected services.
Run `version(true)` to refresh any cached values.

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test version` to execute the unit tests.
