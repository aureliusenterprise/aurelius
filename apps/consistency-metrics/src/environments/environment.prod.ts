export const environment = {
  name: 'm4i_consistency_metrics',
  googleAnalyticsMeasurementID: 'G-1B9CJ1S11',
  i18n: {
    defaultLanguage: 'en-US',
    languages: {}
  },
  keycloak: {
    url: '/auth',
    realm: 'm4i',
    clientId: 'm4i_consistency_metrics'
  },
  notifications: {
    badgePath: 'assets/m4i-icon.png',
    iconPath: 'assets/m4i-icon.png'
  },
  production: true,
  shell: {
    appCopyright: 2020,
    appLogoPath: 'assets/m4i-analytics-logo-50.png',
    appName: 'Models4Insight Consistency Metrics',
  }
};
