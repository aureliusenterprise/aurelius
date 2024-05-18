export const environment = {
  name: 'm4i_index_page',
  googleAnalyticsMeasurementID: 'UA-138345924-1',

  i18n: {
    defaultLanguage: 'en-US',
    languages: {}
  },
  keycloak: {
    url: '/auth',
    realm: 'm4i',
    clientId: 'm4i_atlas'
  },
  notifications: {
    badgePath: 'assets/m4i-icon.png',
    iconPath: 'assets/m4i-icon.png'
  },
  production: true,
  shell: {
    appCopyright: 2022,
    appLogoPath: 'assets/aurelius-atlas-logo.png',
    appName: 'Aurelius Atlas Data Governance Index Page',
    standalone: true
  },
  telemetry: false
};
