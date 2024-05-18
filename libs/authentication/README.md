# Authentication

This library provides a common authentication service that integrates with Keycloak.

## Initialization

The authentication module needs to be configured to connect to Keycloak. It is recommended that you include your Keycloak configuration as part of your app's environment settings.

```javascript
export const environment = {
  keycloak: {
    url: '/auth',
    realm: 'example_realm',
    clientId: 'example_client'
  }
};
```

To initialize the authentication module, include the following in your AppModule:

```javascript
import { NgModule } from '@angular/core';
import { AuthenticationModule } from '@models4insight/authentication';
import { environment } from '../environments/environment';

@NgModule({
  imports: [AuthenticationModule.forRoot(environment.keycloak)]
})
export class AppModule {}
```

The `AuthenticationModule` is loaded as part of the Models4Insight `core`.

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test authentication` to execute the unit tests.
