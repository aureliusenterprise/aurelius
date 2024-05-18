# HTTP

This module extends the default Angular HTTP client with a custom client providing additional utilities, such as:

- Keycloak authorization
- Request caching
- Error handling

When this module is loaded, any modules using the default Angular HTTP Client will use the extended client instead.

To initialize the extended HTTP client, please include the following as part of your `AppModule`:

```javascript
import { NgModule } from '@angular/core';
import { HttpModule } from '@models4insight/http';
import { environment } from '../environments/environment';
import { AppComponent } from './app.component';

@NgModule({
  declarations: [AppComponent],
  imports: [HttpModule.forRoot({ production: environment.production })],
  bootstrap: [AppComponent]
})
export class AppModule {}
```

The `HttpModule` is loaded as part of the Models4Insight `core`.

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test http` to execute the unit tests.
