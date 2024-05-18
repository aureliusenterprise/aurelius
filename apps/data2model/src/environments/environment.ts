// This file can be replaced during build by using the `fileReplacements` array.
// `ng build --prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

export const environment = {
  name: 'm4i_data2model',
  googleAnalyticsMeasurementID: 'UA-138359451-1',
  i18n: {
    defaultLanguage: 'en-US',
    languages: {}
  },
  keycloak: {
    url: '/auth',
    realm: 'm4i',
    clientId: 'm4i_thijs'
  },
  notifications: {
    badgePath: 'assets/d2m-icon.png',
    iconPath: 'assets/d2m-icon.png'
  },
  production: false,
  shell: {
    appCopyright: 2020,
    appLogoPath: 'assets/m4i-data2model-logo.png',
    appName: 'Data2Model',
  }
};

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
import 'zone.js/plugins/zone-error'; // Included with Angular CLI.
