export const environment = {
  name: 'm4i_platform',
  googleAnalyticsMeasurementID: 'UA-138345924-1',
  i18n: {
    defaultLanguage: 'en-US',
    languages: {}
  },
  keycloak: {
    url: '/auth',
    realm: 'm4i',
    clientId: 'm4i_platform'
  },
  notifications: {
    badgePath: 'assets/m4i-icon.png',
    iconPath: 'assets/m4i-icon.png'
  },
  production: true,
  shell: {
    appCopyright: 2020,
    appLogoPath: 'assets/m4i-platform-logo.png',
    appName: 'Models4Insight',
  }
};
