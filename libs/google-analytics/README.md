# Google-Analytics

The Google Analytics module provides a common service for tracking page views.

## Initialization

Please make sure that your `index.html` includes the following script near the top of the `head` tag:

```html
<!-- Global Site Tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    dataLayer.push(arguments);
  }
  gtag('js', new Date());
</script>
```

The Google Analytics module needs to be configured to connect to Google Analytics. It is recommended that you include your tracking ID configuration in your environment settings.

```javascript
export const environment = {
  googleAnalyticsMeasurementID: 'YOUR_TRACKING_ID'
};
```

To initialize the Google Analytics module, include the following in your `AppModule`:

```javascript
import { NgModule } from '@angular/core';
import { GoogleAnalyticsModule } from '@models4insight/google-analytics';
import { environment } from '../environments/environment';

@NgModule({
  imports: [
    GoogleAnalyticsModule.forRoot({
      measurementID: environment.googleAnalyticsMeasurementID,
      production: environment.production
    })
  ]
})
export class AppModule {}
```

The `GoogleAnalyticsModule` is loaded as part of the Models4Insight `core`.

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test google-analytics` to execute the unit tests.
