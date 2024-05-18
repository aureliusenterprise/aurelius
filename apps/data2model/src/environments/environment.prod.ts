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
    clientId: 'm4i_data2model'
  },
  notifications: {
    badgePath: 'assets/d2m-icon.png',
    iconPath: 'assets/d2m-icon.png'
  },
  production: true,
  shell: {
    appCopyright: 2020,
    appLogoPath: 'assets/d2m-logo-50.png',
    appName: 'Data2Model',
  }
};