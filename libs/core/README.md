# Core

This module defines the core of all Models4Insight applications by providing a set of shared module imports for use in the `AppModule` of every application, as well as a shared `index.html` page.

## Usage

To import the shared modules, include the following in your `AppModule`:

```javascript
import { NgModule } from '@angular/core';
import { Core } from '@models4insight/core';
import { environment } from '../environments/environment';

@NgModule({
  imports: [...Core.imports(environment)]
})
export class AppModule {}
```

To use the shared `index.html` for your application, include the following in the `angular.json` for the application project:

```json
{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "projects": {
    "<your-app-name>": {
      "architect": {
        "build": {
          "options": {
            "index": "libs/core/src/index.html"
          }
        }
      }
    }
  }
}
```

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test core` to execute the unit tests.
