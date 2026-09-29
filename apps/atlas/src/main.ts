import { enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/app.module';
import { environment } from './environments/environment';

if (environment.production) {
  enableProdMode();
}

/**
 * Settings of the tenant this page belongs to (Keycloak realm, auth URL), served next to index.html as
 * config.json. The same build then serves every tenant; without config.json the built-in defaults apply.
 * The Keycloak settings object is shared with the authentication module, so it is updated in place before the
 * application starts.
 */
function loadRuntimeConfig(): Promise<void> {
  return fetch('config.json', { cache: 'no-store', credentials: 'same-origin' })
    .then((response) => (response.ok ? response.json() : null))
    .then((config) => {
      if (config && config.keycloak) {
        const { url, realm, clientId } = config.keycloak;
        Object.assign(environment.keycloak, {
          ...(url ? { url } : {}),
          ...(realm ? { realm } : {}),
          ...(clientId ? { clientId } : {}),
        });
      }
      if (config && config.tenant) {
        (window as any).aureliusTenant = config.tenant;
      }
    })
    .catch(() => undefined);
}

loadRuntimeConfig().then(() =>
  platformBrowserDynamic()
    .bootstrapModule(AppModule)
    .catch((err) => console.error(err))
);
